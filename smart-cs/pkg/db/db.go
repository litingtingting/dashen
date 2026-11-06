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
			api_token TEXT,
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
			ai_daily_limit INTEGER,
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
		`CREATE UNIQUE INDEX IF NOT EXISTS idx_users_api_token ON users(api_token) WHERE api_token IS NOT NULL`,
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

	// 轻量迁移：给已存在的表补列（CREATE TABLE IF NOT EXISTS 不会加列）
	if err := migrate(); err != nil {
		return err
	}

	// 初始化默认数据
	return initDefaultData()
}

// migrate 幂等的列补齐（SQLite 不支持 ADD COLUMN IF NOT EXISTS，靠先查 PRAGMA 实现幂等）
func migrate() error {
	rows, err := DB.Query(`PRAGMA table_info(plans)`)
	if err != nil {
		return err
	}
	defer rows.Close()

	hasAILimit := false
	for rows.Next() {
		var cid int
		var name string
		var ctype string
		var notnull int
		var dflt any
		var pk int
		if err := rows.Scan(&cid, &name, &ctype, &notnull, &dflt, &pk); err != nil {
			return err
		}
		if name == "ai_daily_limit" {
			hasAILimit = true
		}
	}
	if err := rows.Err(); err != nil {
		return err
	}

	if !hasAILimit {
		if _, err := DB.Exec(`ALTER TABLE plans ADD COLUMN ai_daily_limit INTEGER`); err != nil {
			return err
		}
		log.Println("✅ 迁移：plans.ai_daily_limit 已添加")
	}

	// 回填：已存在的套餐行若为空，按 daily_limit 补齐（保持两个上限一致）
	if _, err := DB.Exec(`UPDATE plans SET ai_daily_limit = daily_limit WHERE ai_daily_limit IS NULL`); err != nil {
		return err
	}

	// users 表补 api_token 列（API 访问令牌，与密码哈希解耦）
	hasAPIToken, err := columnExists("users", "api_token")
	if err != nil {
		return err
	}
	if !hasAPIToken {
		if _, err := DB.Exec(`ALTER TABLE users ADD COLUMN api_token TEXT`); err != nil {
			return err
		}
		log.Println("✅ 迁移：users.api_token 已添加")
	}

	return nil
}

// columnExists 判断表中是否存在指定列（SQLite 无 ADD COLUMN IF NOT EXISTS，只能先查 PRAGMA）
func columnExists(table, column string) (bool, error) {
	rows, err := DB.Query(`PRAGMA table_info(` + table + `)`)
	if err != nil {
		return false, err
	}
	defer rows.Close()

	found := false
	for rows.Next() {
		var cid int
		var name string
		var ctype string
		var notnull int
		var dflt any
		var pk int
		if err := rows.Scan(&cid, &name, &ctype, &notnull, &dflt, &pk); err != nil {
			return false, err
		}
		if name == column {
			found = true
		}
	}
	if err := rows.Err(); err != nil {
		return false, err
	}
	return found, nil
}

// initDefaultData 初始化默认数据
func initDefaultData() error {
	// 创建默认套餐
	plans := []struct {
		id, name     string
		dailyLimit   int
		aiDailyLimit int
		priceMonth   float64
		priceYear    float64
		features     string
	}{
		{"free", "体验版", 50, 50, 0, 0, `{"personas":1,"platforms":1,"accounts":1}`},
		{"standard", "标准版", 500, 500, 99, 999, `{"personas":3,"platforms":2,"accounts":3}`},
		{"pro", "专业版", 2000, 2000, 299, 2999, `{"personas":999,"platforms":5,"accounts":10}`},
		{"enterprise", "企业版", 99999, 99999, 0, 0, `{"personas":999,"platforms":999,"accounts":999}`},
	}

	for _, plan := range plans {
		_, err := DB.Exec(`INSERT OR IGNORE INTO plans (id, name, daily_limit, ai_daily_limit, price_month, price_year, features)
			VALUES (?, ?, ?, ?, ?, ?, ?)`,
			plan.id, plan.name, plan.dailyLimit, plan.aiDailyLimit, plan.priceMonth, plan.priceYear, plan.features)
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
