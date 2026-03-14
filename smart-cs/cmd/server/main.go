package main

import (
	"flag"
	"fmt"
	"log"
	"smart-cs/internal/api"
	"smart-cs/internal/scheduler"
	"smart-cs/pkg/db"
)

func main() {
	configPath := flag.String("config", "configs/config.yml", "path to config file")
	flag.Parse()

	// 加载配置
	cfg, err := loadConfig(*configPath)
	if err != nil {
		log.Fatalf("加载配置失败：%v", err)
	}

	// 初始化数据库
	if err := db.Init(cfg.Database.SQLite.Path); err != nil {
		log.Fatalf("初始化数据库失败：%v", err)
	}
	defer db.Close()

	// 启动定时任务（清理 7 天前的对话）
	scheduler.StartCleanup(cfg.Cleanup.ConversationRetainDays)

	// 启动 HTTP 服务
	addr := fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port)
	log.Printf("🚀 智能客服系统启动中... 监听地址：%s", addr)

	router := api.SetupRouter(cfg)
	if err := router.Run(addr); err != nil {
		log.Fatalf("启动服务失败：%v", err)
	}
}
