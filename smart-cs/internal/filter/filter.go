package filter

import (
	"regexp"
	"strings"
)

// Filter 内容过滤器
type Filter struct {
	sensitiveWords []string
	maxLength      int
}

// NewFilter 创建过滤器
func NewFilter(sensitiveWords []string, maxLength int) *Filter {
	return &Filter{
		sensitiveWords: sensitiveWords,
		maxLength:      maxLength,
	}
}

// FilterSensitiveWords 过滤敏感词
func (f *Filter) FilterSensitiveWords(text string) string {
	result := text
	for _, word := range f.sensitiveWords {
		result = strings.ReplaceAll(result, word, "**")
	}
	return result
}

// HumanizeResponse 人味化处理（去 AI 腔调）
func (f *Filter) HumanizeResponse(aiText string) string {
	// 去掉常见的 AI 腔调
	patterns := []struct {
		pattern     string
		replacement string
	}{
		{`作为 (一名 | 个)?(AI|人工智能) 助手`, ""},
		{`我是一个 (AI|人工智能)`, ""},
		{`根据我的了解`, ""},
		{`总的来说`, ""},
		{`首先`, ""},
		{`其次`, ""},
		{`最后`, ""},
		{`希望以上信息对您有帮助`, ""},
		{`如果您还有其他问题`, "有问题随时问我～"},
		{`请问还有什么可以帮您`, "还有啥能帮你的？"},
	}

	result := aiText
	for _, p := range patterns {
		re := regexp.MustCompile(p.pattern)
		result = re.ReplaceAllString(result, p.replacement)
	}

	// 缩短过长的回复
	if len(result) > f.maxLength {
		result = result[:f.maxLength] + "..."
	}

	// 清理多余的空行
	result = strings.TrimSpace(result)

	return result
}

// CheckCompliance 合规检查
func (f *Filter) CheckCompliance(text string) (bool, string) {
	// 检查敏感词
	for _, word := range f.sensitiveWords {
		if strings.Contains(text, word) {
			return false, "包含敏感词：" + word
		}
	}

	// 检查广告法违禁词
	forbiddenWords := []string{
		"最", "第一", "顶级", "绝对", "100%", "永久",
	}

	for _, word := range forbiddenWords {
		if strings.Contains(text, word) {
			return false, "包含广告法违禁词：" + word
		}
	}

	return true, ""
}

// ProcessResponse 完整处理 AI 响应
func (f *Filter) ProcessResponse(aiText string) (string, error) {
	// 1. 敏感词过滤
	text := f.FilterSensitiveWords(aiText)

	// 2. 合规检查
	passed, reason := f.CheckCompliance(text)
	if !passed {
		// 记录但不阻断，仅标记
		text = "[待审核] " + text
	}

	// 3. 人味化处理
	text = f.HumanizeResponse(text)

	return text, nil
}

// DefaultSensitiveWords 默认敏感词库
var DefaultSensitiveWords = []string{
	// 政治敏感
	"政治敏感词 1", "政治敏感词 2",
	// 违法违规
	"赌博", "色情", "诈骗",
	// 竞品（可配置）
	"竞争对手名称",
}
