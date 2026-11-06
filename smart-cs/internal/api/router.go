package api

import (
	"smart-cs/pkg/config"

	"github.com/gin-gonic/gin"
)

// SetupRouter 设置路由
func SetupRouter(cfg *config.Config) *gin.Engine {
	router := gin.Default()

	// 健康检查（公开）
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// 企业对接页面（公开）
	router.GET("/join", handleJoinPage)
	router.POST("/join/submit", handleJoinSubmit)

	// 平台回调（公开，需各平台签名校验）
	callbacks := router.Group("/callbacks")
	{
		callbacks.Any("/wechat", handleWechatCallback)
		callbacks.Any("/taobao", handleTaobaoCallback)
		callbacks.Any("/douyin", handleDouyinCallback)
	}

	// ===== 需认证的业务 API =====
	auth := router.Group("/api")
	auth.Use(RequireAuth())
	{
		// 租户管理（仅管理员及以上可写）
		tenants := auth.Group("/tenants")
		{
			tenants.POST("", RequireRole(RoleAdmin), createTenant)
			tenants.GET("/:id", getTenant)
			tenants.PUT("/:id", RequireRole(RoleAdmin), updateTenant)
			tenants.DELETE("/:id", RequireRole(RoleSuperAdmin), deleteTenant)
			tenants.GET("", listTenants)
		}

		// 用户管理（仅管理员及以上可写）
		users := auth.Group("/users")
		{
			users.POST("", RequireRole(RoleAdmin), createUser)
			users.POST("/login", userLogin)
			users.GET("/:id", getUser)
			users.PUT("/:id", RequireRole(RoleAdmin), updateUser)
			users.DELETE("/:id", RequireRole(RoleAdmin), deleteUser)
		}

		// 对话管理（受配额约束）
		conversations := auth.Group("/conversations", enforceQuota())
		{
			conversations.POST("", createConversation)
			conversations.GET("", listConversations)
			conversations.GET("/:id", getConversation)
		}

		// 配额查询
		auth.GET("/quota", handleQuota)
	}

	// AI 测试（开发用，需认证 + 配额）
	api := router.Group("/api")
	api.Use(RequireAuth(), enforceQuota())
	{
		api.POST("/ai/test", handleAITest)
	}

	return router
}
