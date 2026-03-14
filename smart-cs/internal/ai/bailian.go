package ai

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// BailianClient 百炼 AI 客户端
type BailianClient struct {
	APIKey    string
	Model     string
	BaseURL   string
	Timeout   time.Duration
}

// ChatRequest 聊天请求
type ChatRequest struct {
	Model string `json:"model"`
	Input Input  `json:"input"`
}

// Input 输入结构
type Input struct {
	Prompt string `json:"prompt"`
}

// ChatResponse 聊天响应
type ChatResponse struct {
	Output Output `json:"output"`
}

// Output 输出结构
type Output struct {
	Text string `json:"text"`
}

// NewBailianClient 创建百炼客户端
func NewBailianClient(apiKey, model string) *BailianClient {
	return &BailianClient{
		APIKey:  apiKey,
		Model:   model,
		BaseURL: "https://dashscope.aliyuncs.com/api/v1",
		Timeout: 30 * time.Second,
	}
}

// Chat 发送聊天请求
func (c *BailianClient) Chat(prompt string, persona Persona) (string, error) {
	// 构建带人设的 prompt
	systemPrompt := c.buildSystemPrompt(persona)
	fullPrompt := fmt.Sprintf("%s\n\n用户消息：%s", systemPrompt, prompt)

	// 创建请求
	reqBody := ChatRequest{
		Model: c.Model,
		Input: Input{
			Prompt: fullPrompt,
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	// 创建 HTTP 请求
	req, err := http.NewRequest("POST", c.BaseURL+"/services/aigc/text-generation/generation", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}

	// 设置请求头
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	// 发送请求
	client := &http.Client{
		Timeout: c.Timeout,
	}

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
	var chatResp ChatResponse
	if err := json.Unmarshal(body, &chatResp); err != nil {
		return "", err
	}

	return chatResp.Output.Text, nil
}

// buildSystemPrompt 构建系统提示词（人设）
func (c *BailianClient) buildSystemPrompt(persona Persona) string {
	return fmt.Sprintf(`你是一名智能客服，请按照以下人设回复客户：

客服名称：%s
语气风格：%s
问候语：%s
常用表情：%s
称呼方式：%s

回复规则：
1. 像真人一样聊天，不要用 AI 腔调
2. 回复简洁，不要长篇大论
3. 适当使用表情符号
4. 不确定时引导客户联系人工客服
5. 不要提及自己是 AI 或机器人

请用人设指定的风格回复客户消息。`,
		persona.Name,
		persona.Tone,
		persona.Greeting,
		persona.Emojis,
		persona.AddressStyle,
	)
}

// Persona 人设配置
type Persona struct {
	Name         string `json:"name"`
	Tone         string `json:"tone"`
	Greeting     string `json:"greeting"`
	Emojis       string `json:"emojis"`
	AddressStyle string `json:"address_style"`
}
