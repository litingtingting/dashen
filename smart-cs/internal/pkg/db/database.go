package db

import (
	"database/sql"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

// InitDB 初始化 SQLite 数据库（WAL 模式）
func InitDB(dbPath string) (*sql.DB, error) {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, err
	}

	// 启用 WAL 模式（支持并发读写）
	_, err = db.Exec(`
		PRAGMA journal_mode=WAL;
		PRAGMA synchronous=NORMAL;
		PRAGMA cache_size=10000;
	`)
	if err != nil {
		return nil, err
	}

	log.Println("✅ 数据库初始化成功（WAL 模式）")
	return db, nil
}

// CreateTables 创建数据库表结构
func CreateTables(db *sql.DB) error {
	schemas := []string{
		// 租户表
		`CREATE TABLE IF NOT EXISTS tenants (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			type TEXT NOT NULL,
			platform_id TEXT,
			api_key TEXT,
			api_secret TEXT,
			persona_config TEXT,
			status INTEGER DEFAULT 1,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)`,

		// 对话记录表
		`CREATE TABLE IF NOT EXISTS conversations (
			id TEXT PRIMARY KEY,
			tenant_id TEXT NOT NULL,
			customer_id TEXT NOT NULL,
			customer_info TEXT,
			message_type TEXT NOT NULL,
			content TEXT NOT NULL,
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
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(tenant_id, date)
		)`,
	}

	for _, schema := range schemas {
		_, err := db.Exec(schema)
		if err != nil {
			return err
		}
	}

	log.Println("✅ 数据库表结构创建成功")
	return nil
}
