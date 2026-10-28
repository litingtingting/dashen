package ai

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

// BailianClient 百炼 AI 客户端
type BailianClient struct {
	APIKey    string
	Model     string
	BaseURL   string
	Timeout   time.Duration
}

// ChatCompletionRequest OpenAI 兼容的聊天请求
type ChatCompletionRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
}

// Message 消息结构
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// ChatCompletionResponse OpenAI 兼容的聊天响应
type ChatCompletionResponse struct {
	Choices []Choice `json:"choices"`
	Usage   Usage   `json:"usage"`
}

// Usage 百炼（OpenAI 兼容）返回的 Token 用量
type Usage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
	PromptTokensDetails struct {
		CachedTokens int `json:"cached_tokens"`
	} `json:"prompt_tokens_details"`
}

// Choice 选择结构
type Choice struct {
	Message Message `json:"message"`
}

// NewBailianClient 创建百炼客户端（OpenAI 兼容模式）
func NewBailianClient(apiKey, model string) *BailianClient {
	// 默认使用 DashScope OpenAI 兼容端点（中国大陆）
	baseURL := "https://dashscope.aliyuncs.com/compatible-mode/v1"
	
	// 支持环境变量覆盖 API 端点（优先级更高）
	if envURL := os.Getenv("BAILIAN_BASEURL"); envURL != "" {
		baseURL = envURL
		fmt.Printf("[DEBUG] Using BAILIAN_BASEURL from env: %s\n", baseURL)
	}
	
	return &BailianClient{
		APIKey:  apiKey,
		Model:   model,
		BaseURL: strings.TrimSuffix(baseURL, "/"),
		Timeout: 30 * time.Second,
	}
}

// Chat 发送聊天请求（OpenAI 兼容格式）
func (c *BailianClient) Chat(prompt string, persona Persona) (string, error) {
	// 构建带人设的 messages
	systemPrompt := c.buildSystemPrompt(persona)
	messages := []Message{
		{Role: "system", Content: systemPrompt},
		{Role: "user", Content: prompt},
	}

	// 创建请求（OpenAI 兼容格式）
	reqBody := ChatCompletionRequest{
		Model:    c.Model,
		Messages: messages,
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

	// 设置请求头
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	// 发送请求
	client := &http.Client{
		Timeout: c.Timeout,
	}

	start := time.Now()
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

	// 调试：打印原始响应
	fmt.Printf("[DEBUG] API Response Status: %d\n", resp.StatusCode)
	fmt.Printf("[DEBUG] API Response Body: %s\n", string(body))

	// 埋点：无论成功失败都记录 Token 用量（失败时 usage 为空/0，便于统计失败调用次数）
	var usageProbe struct {
		Usage Usage `json:"usage"`
	}
	_ = json.Unmarshal(body, &usageProbe)
	logUsage(c.Model, resp.StatusCode, usageProbe.Usage, time.Since(start))

	// 检查 HTTP 状态码
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API request failed with status %d: %s", resp.StatusCode, string(body))
	}

	// 解析响应（OpenAI 兼容格式）
	var completionResp ChatCompletionResponse
	if err := json.Unmarshal(body, &completionResp); err != nil {
		return "", fmt.Errorf("failed to parse response: %v, body: %s", err, string(body))
	}

	// 埋点：输出结构化的 Token 用量行，供 ai_token_stats.py 统计真实 AI 成本

	if len(completionResp.Choices) == 0 {
		return "", fmt.Errorf("no choices in response")
	}

	return completionResp.Choices[0].Message.Content, nil
}

// logUsage 输出一行结构化的 Token 用量埋点。
// 格式：[BAILIAN_USAGE] <RFC3339毫秒> model=... status=... prompt_tokens=... completion_tokens=... total_tokens=... cached_tokens=... latency_ms=...
// 该行是 scripts/ai_token_stats.py 的唯一数据源，请勿随意更改格式。
func logUsage(model string, status int, u Usage, elapsed time.Duration) {
	fmt.Printf(
		"[BAILIAN_USAGE] %s model=%s status=%d prompt_tokens=%d completion_tokens=%d total_tokens=%d cached_tokens=%d latency_ms=%d\n",
		time.Now().Format("2006-01-02T15:04:05.000"),
		model,
		status,
		u.PromptTokens,
		u.CompletionTokens,
		u.TotalTokens,
		u.PromptTokensDetails.CachedTokens,
		elapsed.Milliseconds(),
	)
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
