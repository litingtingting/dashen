package scheduler

import (
	"fmt"
	"log"
	"time"

	"smart-cs/internal/memory"
	"smart-cs/pkg/compress"

	"github.com/google/uuid"
)

// SummaryScheduler 摘要调度器
type SummaryScheduler struct {
	memoryManager *memory.MemoryManager
	compressor    *compress.SummaryConfig
}

// NewSummaryScheduler 创建摘要调度器
func NewSummaryScheduler(mm *memory.MemoryManager) *SummaryScheduler {
	return &SummaryScheduler{
		memoryManager: mm,
		compressor:    compress.NewSummaryConfig(),
	}
}

// StartDailySummary 启动每日摘要任务
func (s *SummaryScheduler) StartDailySummary() {
	log.Println("🕐 启动每日对话摘要任务（23:00 执行）")

	// 每天 23:00 执行
	go func() {
		for {
			now := time.Now()
			next := time.Date(now.Year(), now.Month(), now.Day(), 23, 0, 0, 0, now.Location())
			if now.After(next) {
				next = next.Add(24 * time.Hour)
			}

			duration := next.Sub(now)
			log.Printf("⏰ 下次摘要时间：%s (%s 后)", next.Format("2006-01-02 15:04:05"), duration)

			time.Sleep(duration)
			s.runDailySummary()
		}
	}()
}

// runDailySummary 执行每日摘要
func (s *SummaryScheduler) runDailySummary() {
	log.Println("📝 开始执行每日对话摘要...")

	// TODO: 从数据库读取今日对话
	// conversations := loadTodayConversations()

	// 临时测试数据
	conversations := []compress.Conversation{
		{Role: "客户", Content: "这个商品有货吗？", Time: "2026-03-14 10:00"},
		{Role: "客服", Content: "亲，您好呀~ 这款商品目前有现货哦！", Time: "2026-03-14 10:01"},
		{Role: "客户", Content: "什么时候发货？", Time: "2026-03-14 10:05"},
		{Role: "客服", Content: "亲，一般下单后 24 小时内发货哦~", Time: "2026-03-14 10:06"},
		{Role: "客户", Content: "有什么优惠吗？", Time: "2026-03-14 14:30"},
		{Role: "客服", Content: "现在关注可以领 10 元优惠券哦！", Time: "2026-03-14 14:31"},
	}

	// 压缩对话
	result, err := s.compressor.CompressConversations(conversations)
	if err != nil {
		log.Printf("❌ 摘要失败：%v", err)
		return
	}

	// 保存摘要到记忆库
	entry := &memory.MemoryEntry{
		ID:        uuid.New().String(),
		TenantID:  "test-tenant",
		Type:      "archive",
		Content:   fmt.Sprintf("今日对话：%d 条", len(conversations)),
		Summary:   fmt.Sprintf("关键点：%v\n待办：%v\n洞察：%v", result.KeyPoints, result.Actions, result.Insights),
		Tags:      []string{"daily-summary", "customer-service"},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	if err := s.memoryManager.SaveMemory(entry); err != nil {
		log.Printf("❌ 保存记忆失败：%v", err)
		return
	}

	log.Printf("✅ 摘要完成！压缩率：%.2fx", result.Compression)
	log.Printf("   原始对话：%d 条", result.OriginalCount)
	log.Printf("   关键点：%d 个", len(result.KeyPoints))
	log.Printf("   待办事项：%d 个", len(result.Actions))
	log.Printf("   客户洞察：%d 个", len(result.Insights))
}
