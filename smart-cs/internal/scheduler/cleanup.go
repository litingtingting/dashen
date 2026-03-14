package scheduler

import (
	"log"
	"time"

	"smart-cs/pkg/db"
)

// StartCleanup 启动定时清理任务
func StartCleanup(retainDays int) {
	log.Printf("🕐 启动定时清理任务：保留%s天前的对话", retainDays)

	// 每天凌晨 2 点执行
	go func() {
		for {
			now := time.Now()
			next := time.Date(now.Year(), now.Month(), now.Day(), 2, 0, 0, 0, now.Location())
			
			// 如果已经过了今天的 2 点，则设置为明天 2 点
			if now.After(next) {
				next = next.Add(24 * time.Hour)
			}

			duration := next.Sub(now)
			log.Printf("⏰ 下次清理时间：%s (%s 后)", next.Format("2006-01-02 15:04:05"), duration)

			time.Sleep(duration)
			cleanupOldConversations(retainDays)
		}
	}()
}

// cleanupOldConversations 清理旧对话
func cleanupOldConversations(retainDays int) {
	log.Println("🧹 开始清理旧对话...")

	cutoff := time.Now().AddDate(0, 0, -retainDays)

	result, err := db.DB.Exec(`DELETE FROM conversations WHERE created_at < ?`, cutoff)
	if err != nil {
		log.Printf("❌ 清理对话失败：%v", err)
		return
	}

	deleted, _ := result.RowsAffected()
	log.Printf("✅ 清理完成：删除了 %d 条对话记录", deleted)
}
