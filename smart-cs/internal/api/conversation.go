package api

import (
	"net/http"
	"time"

	"smart-cs/internal/ai"
	"smart-cs/internal/filter"
	"smart-cs/pkg/db"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// ConversationRequest 对话请求
type ConversationRequest struct {
	TenantID   string `json:"tenant_id"`
	CustomerID string `json:"customer_id"`
	Content    string `json:"content"`
}

// Conversation 对话记录
type Conversation struct {
	ID           string    `json:"id"`
	TenantID     string    `json:"tenant_id"`
	CustomerID   string    `json:"customer_id"`
	CustomerInfo string    `json:"customer_info"`
	MessageType  string    `json:"message_type"`
	Content      string    `json:"content"`
	AIResponse   string    `json:"ai_response"`
	Filtered     int       `json:"filtered"`
	CreatedAt    time.Time `json:"created_at"`
}

// createConversation 创建对话（发送消息）
func createConversation(c *gin.Context) {
	var req ConversationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 验证租户是否存在
	var tenantExists int
	err := db.DB.QueryRow(`SELECT COUNT(*) FROM tenants WHERE id = ? AND status = 1`, req.TenantID).Scan(&tenantExists)
	if err != nil || tenantExists == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "租户不存在或已禁用"})
		return
	}

	// 生成对话 ID
	conversationID := uuid.New().String()

	// 保存用户消息
	_, err = db.DB.Exec(`INSERT INTO conversations (id, tenant_id, customer_id, message_type, content) 
		VALUES (?, ?, ?, ?, ?)`,
		conversationID, req.TenantID, req.CustomerID, "inbound", req.Content)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 调用 AI 生成回复
	// TODO: 从配置加载 API Key 和人设
	f := filter.NewFilter(filter.DefaultSensitiveWords, 500)
	
	// 模拟 AI 回复（实际项目中调用百炼 API）
	aiResponse := "您好！收到您的消息了，有什么可以帮您的吗？😊"
	
	// 过滤和人味化处理
	processedResponse, err := f.ProcessResponse(aiResponse)
	if err != nil {
		processedResponse = aiResponse
	}

	// 保存 AI 回复
	_, err = db.DB.Exec(`INSERT INTO conversations (id, tenant_id, customer_id, message_type, content, ai_response, filtered) 
		VALUES (?, ?, ?, ?, ?, ?, ?)`,
		uuid.New().String(), req.TenantID, req.CustomerID, "outbound", processedResponse, processedResponse, 1)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 更新使用量统计
	today := time.Now().Format("2006-01-02")
	_, err = db.DB.Exec(`INSERT INTO usage_stats (id, tenant_id, date, message_count, ai_call_count) 
		VALUES (?, ?, ?, ?, ?)
		ON CONFLICT(tenant_id, date) DO UPDATE SET message_count = message_count + 1, ai_call_count = ai_call_count + 1`,
		uuid.New().String(), req.TenantID, today, 1, 1)
	if err != nil {
		// 非致命错误，继续
	}

	c.JSON(http.StatusOK, gin.H{
		"conversation_id": conversationID,
		"response":        processedResponse,
	})
}

// listConversations 列出对话
func listConversations(c *gin.Context) {
	tenantID := c.Query("tenant_id")
	limit := c.DefaultQuery("limit", "20")

	rows, err := db.DB.Query(`SELECT id, tenant_id, customer_id, customer_info, message_type, content, ai_response, filtered, created_at 
		FROM conversations WHERE tenant_id = ? ORDER BY created_at DESC LIMIT ?`,
		tenantID, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	var conversations []Conversation
	for rows.Next() {
		var conv Conversation
		if err := rows.Scan(&conv.ID, &conv.TenantID, &conv.CustomerID, &conv.CustomerInfo,
			&conv.MessageType, &conv.Content, &conv.AIResponse, &conv.Filtered, &conv.CreatedAt); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		conversations = append(conversations, conv)
	}

	c.JSON(http.StatusOK, gin.H{"conversations": conversations})
}

// getConversation 获取单条对话
func getConversation(c *gin.Context) {
	id := c.Param("id")

	var conv Conversation
	err := db.DB.QueryRow(`SELECT id, tenant_id, customer_id, customer_info, message_type, content, ai_response, filtered, created_at 
		FROM conversations WHERE id = ?`, id).Scan(
		&conv.ID, &conv.TenantID, &conv.CustomerID, &conv.CustomerInfo,
		&conv.MessageType, &conv.Content, &conv.AIResponse, &conv.Filtered, &conv.CreatedAt)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "对话不存在"})
		return
	}

	c.JSON(http.StatusOK, conv)
}

// handleAITest AI 测试接口（开发用）
func handleAITest(c *gin.Context) {
	var req struct {
		Prompt string `json:"prompt"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// TODO: 实际调用百炼 API
	// client := ai.NewBailianClient(apiKey, model)
	// response, err := client.Chat(req.Prompt, persona)

	// 临时模拟
	response := "测试回复：" + req.Prompt

	c.JSON(http.StatusOK, gin.H{"response": response})
}
