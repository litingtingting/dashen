package config

import (
	"os"
	"strconv"

	"gopkg.in/yaml.v3"
)

type Config struct {
	System    SystemConfig    `yaml:"system"`
	Server    ServerConfig    `yaml:"server"`
	Database  DatabaseConfig  `yaml:"database"`
	Platforms PlatformConfig  `yaml:"platforms"`
	AI        AIConfig        `yaml:"ai"`
	Admin     AdminConfig     `yaml:"admin"`
	Log       LogConfig       `yaml:"log"`
	Cleanup   CleanupConfig   `yaml:"cleanup"`
}

type SystemConfig struct {
	Name     string `yaml:"name"`
	Version  string `yaml:"version"`
	Env      string `yaml:"env"`
	Timezone string `yaml:"timezone"`
}

type ServerConfig struct {
	Host string    `yaml:"host"`
	Port int       `yaml:"port"`
	Domain string  `yaml:"domain"`
	SSL    SSLConfig `yaml:"ssl"`
}

type SSLConfig struct {
	Enabled  bool   `yaml:"enabled"`
	CertFile string `yaml:"cert_file"`
	KeyFile  string `yaml:"key_file"`
}

type DatabaseConfig struct {
	Type   string       `yaml:"type"`
	SQLite SQLiteConfig `yaml:"sqlite"`
}

type SQLiteConfig struct {
	Path string `yaml:"path"`
}

type PlatformConfig struct {
	Wechat WechatConfig `yaml:"wechat"`
	Taobao TaobaoConfig `yaml:"taobao"`
	Douyin DouyinConfig `yaml:"douyin"`
}

type WechatConfig struct {
	Enabled        bool   `yaml:"enabled"`
	AppID          string `yaml:"app_id"`
	AppSecret      string `yaml:"app_secret"`
	Token          string `yaml:"token"`
	EncodingAESKey string `yaml:"encoding_aes_key"`
	CallbackURL    string `yaml:"callback_url"`
}

type TaobaoConfig struct {
	Enabled     bool   `yaml:"enabled"`
	AppKey      string `yaml:"app_key"`
	AppSecret   string `yaml:"app_secret"`
	CallbackURL string `yaml:"callback_url"`
}

type DouyinConfig struct {
	Enabled     bool   `yaml:"enabled"`
	AppKey      string `yaml:"app_key"`
	AppSecret   string `yaml:"app_secret"`
	CallbackURL string `yaml:"callback_url"`
}

type AIConfig struct {
	Provider string         `yaml:"provider"`
	APIKey   string         `yaml:"api_key"`
	Model    string         `yaml:"model"`
	Filter   FilterConfig   `yaml:"filter"`
}

type FilterConfig struct {
	Enabled            bool   `yaml:"enabled"`
	SensitiveWordsFile string `yaml:"sensitive_words_file"`
	MaxResponseLength  int    `yaml:"max_response_length"`
}

type AdminConfig struct {
	SuperAdmin SuperAdminConfig `yaml:"super_admin"`
}

type SuperAdminConfig struct {
	TenantID     string `yaml:"tenant_id"`
	Username     string `yaml:"username"`
	PasswordHash string `yaml:"password_hash"`
}

type LogConfig struct {
	Level     string `yaml:"level"`
	File      string `yaml:"file"`
	MaxSizeMB int    `yaml:"max_size_mb"`
	MaxDays   int    `yaml:"max_days"`
}

type CleanupConfig struct {
	ConversationRetainDays int    `yaml:"conversation_retain_days"`
	Schedule               string `yaml:"schedule"`
}

func LoadConfig(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}

	// 支持环境变量覆盖配置（优先级：环境变量 > 配置文件）
	cfg.applyEnvOverrides()

	return &cfg, nil
}

// applyEnvOverrides 应用环境变量覆盖
func (c *Config) applyEnvOverrides() {
	// AI API Key 支持环境变量覆盖
	if apiKey := os.Getenv("BAILIAN_API_KEY"); apiKey != "" {
		c.AI.APIKey = apiKey
	}

	// 服务器端口支持环境变量覆盖
	if port := os.Getenv("SERVER_PORT"); port != "" {
		if p, err := strconv.Atoi(port); err == nil {
			c.Server.Port = p
		}
	}

	// 日志级别支持环境变量覆盖
	if level := os.Getenv("LOG_LEVEL"); level != "" {
		c.Log.Level = level
	}
}
