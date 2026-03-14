package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/joho/godotenv"
	"smart-cs/internal/scheduler"
	"smart-cs/internal/api"
	"smart-cs/pkg/config"
	"smart-cs/pkg/db"
)

func main() {
	configPath := flag.String("config", "configs/config.yml", "path to config file")
	loadEnv := flag.Bool("env", true, "load .env file")
	flag.Parse()

	// 加载环境变量（支持 .env 文件）
	if *loadEnv {
		envFile := ".env"
		// 检查当前目录和上级目录
		if _, err := os.Stat(envFile); os.IsNotExist(err) {
			if _, err := os.Stat(filepath.Join("..", envFile)); err == nil {
				envFile = filepath.Join("..", envFile)
			}
		}
		if err := godotenv.Load(envFile); err != nil {
			log.Printf("⚠️  未加载 .env 文件：%v（如使用环境变量可忽略）", err)
		} else {
			log.Printf("✅ 已加载环境变量：%s", envFile)
		}
	}

	// 加载配置
	cfg, err := config.LoadConfig(*configPath)
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

	// 启动对话摘要任务（每日 23:00）
	// TODO: 需要先初始化记忆管理器
	// memoryManager, err := memory.NewMemoryManager(cfg.Database.SQLite.Path)
	// if err != nil {
	// 	log.Fatalf("初始化记忆管理器失败：%v", err)
	// }
	// summaryScheduler := scheduler.NewSummaryScheduler(memoryManager)
	// summaryScheduler.StartDailySummary()

	// 启动 HTTP 服务
	addr := fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port)
	log.Printf("🚀 智能客服系统启动中... 监听地址：%s", addr)
	log.Printf("🧠 记忆压缩模块：已加载（方案 A - 轻量级）")

	router := api.SetupRouter(cfg)
	if err := router.Run(addr); err != nil {
		log.Fatalf("启动服务失败：%v", err)
	}
}
