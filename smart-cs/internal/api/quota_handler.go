package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// handleQuota 查询当前租户的配额用量
// GET /api/quota
func handleQuota(c *gin.Context) {
	tc := TenantCtx(c)
	if tc == nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "缺少认证凭证"})
		return
	}

	usage := GetQuotaUsage(tc.TenantID)
	res := CheckQuota(tc.TenantID)

	c.JSON(http.StatusOK, gin.H{
		"tenant_id": usage.TenantID,
		"date":      usage.Date,
		"plan":      usage.PlanName,
		"usage": gin.H{
			"messages":      usage.MessageCount,
			"ai_calls":      usage.AICallCount,
			"daily_limit":   usage.DailyLimit,
			"ai_daily_limit": usage.AILimit,
		},
		"quota": res,
	})
}
