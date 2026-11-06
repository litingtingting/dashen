package api

import (
	"database/sql"
	"net/http"
	"time"

	"smart-cs/pkg/db"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

const (
	// DefaultPlanID 默认套餐 ID
	DefaultPlanID = "default"
	// DefaultDailyLimit 默认每日消息条数上限
	DefaultDailyLimit = 100
	// DefaultAILimit 默认每日 AI 调用上限
	DefaultAILimit = 100
	// UnlimitedSentinel -1 表示不限量
	UnlimitedSentinel = -1
	// RetentionDays 对话保留天数
	RetentionDays = 7
)

// QuotaUsage 租户当日用量
type QuotaUsage struct {
	TenantID     string
	Date         string
	MessageCount int
	AICallCount  int
	DailyLimit   int
	AILimit      int
	PlanName     string
}

// QuotaResult 配额检查结果
type QuotaResult struct {
	Allowed   bool   `json:"allowed"`
	Reason    string `json:"reason,omitempty"`
	Used      int    `json:"used"`
	Limit     int    `json:"limit"`
	Remaining int    `json:"remaining"`
	PlanName  string `json:"plan_name,omitempty"`
	ResetsAt  string `json:"resets_at,omitempty"`
}

// planLimits 读取租户当前订阅套餐的限制；无有效订阅则用默认套餐
func planLimits(tenantID string) (dailyLimit, aiLimit int, planName string) {
	dailyLimit = DefaultDailyLimit
	aiLimit = DefaultAILimit
	planName = "默认套餐"

	var dl, al sql.NullInt64
	var pn sql.NullString
	err := db.DB.QueryRow(`SELECT p.daily_limit, p.ai_daily_limit, p.name
		FROM subscriptions s JOIN plans p ON p.id = s.plan_id
		WHERE s.tenant_id = ? AND s.status = 'active'
		  AND (s.start_date IS NULL OR s.start_date <= datetime('now'))
		  AND (s.end_date IS NULL OR s.end_date >= datetime('now'))
		ORDER BY s.start_date DESC LIMIT 1`, tenantID).Scan(&dl, &al, &pn)
	if err != nil {
		return dailyLimit, aiLimit, planName
	}
	if dl.Valid {
		dailyLimit = int(dl.Int64)
	}
	if al.Valid {
		aiLimit = int(al.Int64)
	}
	if pn.Valid && pn.String != "" {
		planName = pn.String
	}
	return dailyLimit, aiLimit, planName
}

// todayString 今日日期
func todayString() string {
	return time.Now().Format("2006-01-02")
}

// GetQuotaUsage 查询租户当日用量与限额
func GetQuotaUsage(tenantID string) QuotaUsage {
	dailyLimit, aiLimit, planName := planLimits(tenantID)
	u := QuotaUsage{
		TenantID:   tenantID,
		Date:       todayString(),
		DailyLimit: dailyLimit,
		AILimit:    aiLimit,
		PlanName:   planName,
	}

	var mc, ac sql.NullInt64
	err := db.DB.QueryRow(`SELECT message_count, ai_call_count FROM usage_stats
		WHERE tenant_id = ? AND date = ?`, tenantID, u.Date).Scan(&mc, &ac)
	if err == nil {
		u.MessageCount = int(mc.Int64)
		u.AICallCount = int(ac.Int64)
	}
	return u
}

// CheckQuota 检查租户是否还有配额
func CheckQuota(tenantID string) QuotaResult {
	u := GetQuotaUsage(tenantID)

	res := QuotaResult{
		Allowed:  true,
		Used:     u.MessageCount,
		Limit:    u.DailyLimit,
		PlanName: u.PlanName,
	}
	if u.DailyLimit == UnlimitedSentinel {
		res.Remaining = -1
		return res
	}
	res.Remaining = u.DailyLimit - u.MessageCount
	if res.Remaining < 0 {
		res.Remaining = 0
	}

	if u.MessageCount >= u.DailyLimit {
		res.Allowed = false
		res.Reason = "已达到套餐每日消息上限"
		res.ResetsAt = nextReset()
		return res
	}
	if u.AILimit != UnlimitedSentinel && u.AICallCount >= u.AILimit {
		res.Allowed = false
		res.Reason = "已达到套餐每日 AI 调用上限"
		res.ResetsAt = nextReset()
	}
	return res
}

// nextReset 次日零点
func nextReset() string {
	now := time.Now()
	return time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, now.Location()).
		AddDate(0, 0, 1).Format("2006-01-02 15:04:05")
}

// enforceQuota 配额中间件：超限返回 429
func enforceQuota() gin.HandlerFunc {
	return func(c *gin.Context) {
		tc := TenantCtx(c)
		if tc == nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "缺少认证凭证"})
			return
		}
		res := CheckQuota(tc.TenantID)
		if !res.Allowed {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
				"error": res.Reason,
				"quota": res,
			})
			return
		}
		c.Next()
	}
}

// incrementUsage 累加当日用量（不存在则插入）
func incrementUsage(tenantID string, messages, aiCalls int) {
	_, err := db.DB.Exec(`INSERT INTO usage_stats (id, tenant_id, date, message_count, ai_call_count)
		VALUES (?, ?, ?, ?, ?)
		ON CONFLICT(tenant_id, date) DO UPDATE SET
			message_count = message_count + ?,
			ai_call_count = ai_call_count + ?`,
		uuid.New().String(), tenantID, todayString(), messages, aiCalls, messages, aiCalls)
	if err != nil {
		// 非致命：用量统计失败不阻断主流程
		return
	}
}
