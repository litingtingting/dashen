package main

import (
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
)

func main() {
	// 加载环境变量
	if err := godotenv.Load(); err != nil {
		log.Println("未找到.env 文件，使用系统环境变量")
	}

	// 验证必要的环境变量
	apiKey := os.Getenv("CUSTOMER_APIKEY")
	baseURL := os.Getenv("CUSTOMER_BAILIAN_BASEURL")

	if apiKey == "" || baseURL == "" {
		log.Fatal("错误：缺少必要的环境变量 CUSTOMER_APIKEY 或 CUSTOMER_BAILIAN_BASEURL")
	}

	fmt.Println("✅ 智能客服系统启动中...")
	fmt.Printf("📡 百炼 API: %s\n", maskKey(baseURL))
	fmt.Printf("🔑 API Key: %s\n", maskKey(apiKey))
	fmt.Println("🚀 服务监听：http://0.0.0.0:80")
	
	// TODO: 启动 HTTP 服务
}

// maskKey 脱敏显示密钥（只显示前 6 位）
func maskKey(key string) string {
	if len(key) <= 6 {
		return key + "..."
	}
	return key[:6] + "..."
}
