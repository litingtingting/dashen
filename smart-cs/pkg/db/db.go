package db

import (
	"database/sql"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

var DB *sql.DB

// Init 初始化数据库
func Init(dbPath string) error {
	var err error
	DB, err = sql.Open("sqlite3", dbPath)
	if err != nil {
		return err
	}

	// 测试连接
	if err := DB.Ping(); err != nil {
		return err
	}

	log.Println("✅ 数据库连接成功")

	// 创建表结构
	return createTables()
}

// Close 关闭数据库连接
func Close() {
	if DB != nil {
		DB.Close()
	}
}

// createTables 创建表结构
func createTables() error {
	schemas := []string{
		// 租户表
		`CREATE TABLE IF NOT EXISTS tenants (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			type TEXT NOT NULL,
			platform_id TEXT,
			persona_config TEXT,
			status INTEGER DEFAULT 1,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		// 用户表
		`CREATE TABLE IF NOT EXISTS users (
			id TEXT PRIMARY KEY,
			tenant_id TEXT NOT NULL,
			username TEXT UNIQUE NOT NULL,
			password_hash TEXT NOT NULL,
			role TEXT NOT NULL,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (tenant_id) REFERENCES tenants(id)
		)`,

		// 对话记录表
		`CREATE TABLE IF NOT EXISTS conversations (
			id TEXT PRIMARY KEY,
			tenant_id TEXT NOT NULL,
			customer_id TEXT,
			customer_info TEXT,
			message_type TEXT,
			content TEXT,
			ai_response TEXT,
			filtered INTEGER DEFAULT 0,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		// 使用量统计表
		`CREATE TABLE IF NOT EXISTS usage_stats (
			id TEXT PRIMARY KEY,
			tenant_id TEXT NOT NULL,
			date DATE NOT NULL,
			message_count INTEGER DEFAULT 0,
			ai_call_count INTEGER DEFAULT 0,
			UNIQUE(tenant_id, date)
		)`,

		// 套餐表
		`CREATE TABLE IF NOT EXISTS plans (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			daily_limit INTEGER,
			price_month REAL,
			price_year REAL,
			features TEXT
		)`,

		// 租户订阅表
		`CREATE TABLE IF NOT EXISTS subscriptions (
			id TEXT PRIMARY KEY,
			tenant_id TEXT NOT NULL,
			plan_id TEXT NOT NULL,
			start_date DATETIME,
			end_date DATETIME,
			status TEXT,
			FOREIGN KEY (tenant_id) REFERENCES tenants(id),
			FOREIGN KEY (plan_id) REFERENCES plans(id)
		)`,
	}

	// 创建索引
	indexes := []string{
		`CREATE INDEX IF NOT EXISTS idx_conversations_tenant ON conversations(tenant_id)`,
		`CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at)`,
		`CREATE INDEX IF NOT EXISTS idx_usage_tenant_date ON usage_stats(tenant_id, date)`,
		`CREATE INDEX IF NOT EXISTS idx_users_tenant ON users(tenant_id)`,
	}

	// 执行表创建
	for _, schema := range schemas {
		if _, err := DB.Exec(schema); err != nil {
			return err
		}
	}

	// 执行索引创建
	for _, index := range indexes {
		if _, err := DB.Exec(index); err != nil {
			return err
		}
	}

	log.Println("✅ 数据库表结构创建成功")

	// 初始化默认数据
	return initDefaultData()
}

// initDefaultData 初始化默认数据
func initDefaultData() error {
	// 创建默认套餐
	plans := []struct {
		id, name     string
		dailyLimit   int
		priceMonth   float64
		priceYear    float64
		features     string
	}{
		{"free", "体验版", 50, 0, 0, `{"personas":1,"platforms":1,"accounts":1}`},
		{"standard", "标准版", 500, 99, 999, `{"personas":3,"platforms":2,"accounts":3}`},
		{"pro", "专业版", 2000, 299, 2999, `{"personas":999,"platforms":5,"accounts":10}`},
		{"enterprise", "企业版", 99999, 0, 0, `{"personas":999,"platforms":999,"accounts":999}`},
	}

	for _, plan := range plans {
		_, err := DB.Exec(`INSERT OR IGNORE INTO plans (id, name, daily_limit, price_month, price_year, features) 
			VALUES (?, ?, ?, ?, ?, ?)`,
			plan.id, plan.name, plan.dailyLimit, plan.priceMonth, plan.priceYear, plan.features)
		if err != nil {
			return err
		}
	}

	// 创建超级管理员租户
	_, err := DB.Exec(`INSERT OR IGNORE INTO tenants (id, name, type, status) 
		VALUES (?, ?, ?, ?)`,
		"lishi-feishu", "丽斯飞书", "admin", 1)
	if err != nil {
		return err
	}

	log.Println("✅ 默认数据初始化完成")
	return nil
}
