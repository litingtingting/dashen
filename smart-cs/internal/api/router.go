package api

import (
	"smart-cs/cmd/server"

	"github.com/gin-gonic/gin"
)

// SetupRouter 设置路由
func SetupRouter(cfg *server.Config) *gin.Engine {
	router := gin.Default()

	// 健康检查
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// 企业对接页面
	router.GET("/join", handleJoinPage)
	router.POST("/join/submit", handleJoinSubmit)

	// API 路由组
	api := router.Group("/api")
	{
		// 租户管理
		tenants := api.Group("/tenants")
		{
			tenants.POST("", createTenant)
			tenants.GET("/:id", getTenant)
			tenants.PUT("/:id", updateTenant)
			tenants.DELETE("/:id", deleteTenant)
			tenants.GET("", listTenants)
		}

		// 用户管理
		users := api.Group("/users")
		{
			users.POST("", createUser)
			users.POST("/login", userLogin)
			users.GET("/:id", getUser)
			users.PUT("/:id", updateUser)
			users.DELETE("/:id", deleteUser)
		}

		// 对话管理
		conversations := api.Group("/conversations")
		{
			conversations.POST("", createConversation)
			conversations.GET("", listConversations)
			conversations.GET("/:id", getConversation)
		}

		// 平台回调
		callbacks := api.Group("/callbacks")
		{
			// 微信
			callbacks.Any("/wechat", handleWechatCallback)
			// 淘宝
			callbacks.Any("/taobao", handleTaobaoCallback)
			// 抖音
			callbacks.Any("/douyin", handleDouyinCallback)
		}

		// AI 测试（开发用）
		api.POST("/ai/test", handleAITest)
	}

	return router
}
