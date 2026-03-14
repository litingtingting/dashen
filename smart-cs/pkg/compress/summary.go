package compress

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

// SummaryConfig 摘要配置
type SummaryConfig struct {
	APIKey     string
	Model      string
	BaseURL    string
	MaxTokens  int
	Timeout    time.Duration
}

// Conversation 对话记录
type Conversation struct {
	Role    string `json:"role"`
	Content string `json:"content"`
	Time    string `json:"time"`
}

// SummaryResult 摘要结果
type SummaryResult struct {
	OriginalCount int      `json:"original_count"` // 原始对话数
	SummaryCount  int      `json:"summary_count"`  // 摘要后对话数
	KeyPoints     []string `json:"key_points"`     // 关键点
	Actions       []string `json:"actions"`        // 待办事项
	Insights      []string `json:"insights"`       // 洞察
	Compression   float64  `json:"compression"`    // 压缩率
}

// NewSummaryConfig 从环境变量创建配置
func NewSummaryConfig() *SummaryConfig {
	return &SummaryConfig{
		APIKey:  os.Getenv("BAILIAN_API_KEY"),
		Model:   "qwen-plus",
		BaseURL: os.Getenv("BAILIAN_BASEURL"),
		MaxTokens: 2000,
		Timeout:   30 * time.Second,
	}
}

// CompressConversations 压缩对话
func (c *SummaryConfig) CompressConversations(conversations []Conversation) (*SummaryResult, error) {
	if len(conversations) == 0 {
		return &SummaryResult{}, nil
	}

	// 构建摘要请求
	prompt := c.buildSummaryPrompt(conversations)

	// 调用百炼 API
	summary, err := c.callAI(prompt)
	if err != nil {
		return nil, err
	}

	// 解析摘要结果
	result := c.parseSummary(summary, len(conversations))

	return result, nil
}

// buildSummaryPrompt 构建摘要提示词
func (c *SummaryConfig) buildSummaryPrompt(conversations []Conversation) string {
	var sb strings.Builder

	sb.WriteString("请对以下客服对话进行摘要压缩，提取关键信息：\n\n")
	sb.WriteString("## 对话记录\n")

	for i, conv := range conversations {
		sb.WriteString(fmt.Sprintf("%d. [%s] %s: %s\n", i+1, conv.Time, conv.Role, conv.Content))
	}

	sb.WriteString("\n## 要求\n")
	sb.WriteString("1. 提取 3-5 个关键点（客户关注的核心问题）\n")
	sb.WriteString("2. 列出所有待办事项\n")
	sb.WriteString("3. 总结客户洞察（需求、偏好、痛点）\n")
	sb.WriteString("4. 保持简洁，每条不超过 50 字\n")
	sb.WriteString("\n请以 JSON 格式返回：\n")
	sb.WriteString(`{"key_points": [], "actions": [], "insights": []}`)

	return sb.String()
}

// callAI 调用百炼 AI
func (c *SummaryConfig) callAI(prompt string) (string, error) {
	// 构建请求体
	reqBody := map[string]interface{}{
		"model": c.Model,
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
		"max_tokens": c.MaxTokens,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	// 创建 HTTP 请求
	req, err := http.NewRequest("POST", c.BaseURL+"/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	// 发送请求
	client := &http.Client{Timeout: c.Timeout}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	// 读取响应
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	// 解析响应
	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return "", err
	}

	// 提取回复内容
	choices, ok := result["choices"].([]interface{})
	if !ok || len(choices) == 0 {
		return "", fmt.Errorf("no choices in response")
	}

	choice := choices[0].(map[string]interface{})
	message := choice["message"].(map[string]interface{})
	content := message["content"].(string)

	return content, nil
}

// parseSummary 解析摘要结果
func (c *SummaryConfig) parseSummary(summary string, originalCount int) *SummaryResult {
	result := &SummaryResult{
		OriginalCount: originalCount,
		SummaryCount:  1, // 压缩为 1 条摘要
	}

	// 尝试解析 JSON
	var parsed map[string]interface{}
	if err := json.Unmarshal([]byte(summary), &parsed); err != nil {
		// 解析失败，返回原始摘要
		result.KeyPoints = []string{summary}
		result.Compression = float64(originalCount) / 1.0
		return result
	}

	// 提取关键点
	if points, ok := parsed["key_points"].([]interface{}); ok {
		for _, p := range points {
			if s, ok := p.(string); ok {
				result.KeyPoints = append(result.KeyPoints, s)
			}
		}
	}

	// 提取待办事项
	if actions, ok := parsed["actions"].([]interface{}); ok {
		for _, a := range actions {
			if s, ok := a.(string); ok {
				result.Actions = append(result.Actions, s)
			}
		}
	}

	// 提取洞察
	if insights, ok := parsed["insights"].([]interface{}); ok {
		for _, i := range insights {
			if s, ok := i.(string); ok {
				result.Insights = append(result.Insights, s)
			}
		}
	}

	// 计算压缩率
	if len(result.KeyPoints)+len(result.Actions)+len(result.Insights) > 0 {
		result.Compression = float64(originalCount) / float64(len(result.KeyPoints)+len(result.Actions)+len(result.Insights))
	}

	return result
}
