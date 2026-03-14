package memory

import (
	"database/sql"
	"encoding/json"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

// MemoryManager 记忆管理器
type MemoryManager struct {
	db *sql.DB
}

// MemoryEntry 记忆条目
type MemoryEntry struct {
	ID        string    `json:"id"`
	TenantID  string    `json:"tenant_id"`
	Type      string    `json:"type"` // core, session, archive
	Content   string    `json:"content"`
	Summary   string    `json:"summary"`
	Tags      []string  `json:"tags"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// NewMemoryManager 创建记忆管理器
func NewMemoryManager(dbPath string) (*MemoryManager, error) {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, err
	}

	mm := &MemoryManager{db: db}
	if err := mm.createTables(); err != nil {
		return nil, err
	}

	return mm, nil
}

// createTables 创建表结构
func (mm *MemoryManager) createTables() error {
	schema := `
	CREATE TABLE IF NOT EXISTS memories (
		id TEXT PRIMARY KEY,
		tenant_id TEXT NOT NULL,
		type TEXT NOT NULL,
		content TEXT,
		summary TEXT,
		tags TEXT,
		created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
		updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_memories_tenant ON memories(tenant_id);
	CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
	CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
	`

	_, err := mm.db.Exec(schema)
	return err
}

// SaveMemory 保存记忆
func (mm *MemoryManager) SaveMemory(entry *MemoryEntry) error {
	tagsJSON, _ := json.Marshal(entry.Tags)

	_, err := mm.db.Exec(`
		INSERT OR REPLACE INTO memories (id, tenant_id, type, content, summary, tags, created_at, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	`, entry.ID, entry.TenantID, entry.Type, entry.Content, entry.Summary, string(tagsJSON), entry.CreatedAt, time.Now())

	return err
}

// GetCoreMemories 获取核心记忆（L0 层）
func (mm *MemoryManager) GetCoreMemories(tenantID string) ([]MemoryEntry, error) {
	rows, err := mm.db.Query(`
		SELECT id, tenant_id, type, content, summary, tags, created_at, updated_at
		FROM memories
		WHERE tenant_id = ? AND type = 'core'
		ORDER BY created_at DESC
	`, tenantID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var entries []MemoryEntry
	for rows.Next() {
		var entry MemoryEntry
		var tagsJSON string
		err := rows.Scan(&entry.ID, &entry.TenantID, &entry.Type, &entry.Content, &entry.Summary, &tagsJSON, &entry.CreatedAt, &entry.UpdatedAt)
		if err != nil {
			return nil, err
		}
		json.Unmarshal([]byte(tagsJSON), &entry.Tags)
		entries = append(entries, entry)
	}

	return entries, nil
}

// GetRecentMemories 获取最近记忆（L1 层）
func (mm *MemoryManager) GetRecentMemories(tenantID string, limit int) ([]MemoryEntry, error) {
	rows, err := mm.db.Query(`
		SELECT id, tenant_id, type, content, summary, tags, created_at, updated_at
		FROM memories
		WHERE tenant_id = ? AND type IN ('session', 'archive')
		ORDER BY created_at DESC
		LIMIT ?
	`, tenantID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var entries []MemoryEntry
	for rows.Next() {
		var entry MemoryEntry
		var tagsJSON string
		err := rows.Scan(&entry.ID, &entry.TenantID, &entry.Type, &entry.Content, &entry.Summary, &tagsJSON, &entry.CreatedAt, &entry.UpdatedAt)
		if err != nil {
			return nil, err
		}
		json.Unmarshal([]byte(tagsJSON), &entry.Tags)
		entries = append(entries, entry)
	}

	return entries, nil
}

// SearchMemories 搜索记忆（L2 层）
func (mm *MemoryManager) SearchMemories(tenantID, keyword string) ([]MemoryEntry, error) {
	rows, err := mm.db.Query(`
		SELECT id, tenant_id, type, content, summary, tags, created_at, updated_at
		FROM memories
		WHERE tenant_id = ? AND (content LIKE ? OR summary LIKE ?)
		ORDER BY created_at DESC
		LIMIT 20
	`, tenantID, "%"+keyword+"%", "%"+keyword+"%")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var entries []MemoryEntry
	for rows.Next() {
		var entry MemoryEntry
		var tagsJSON string
		err := rows.Scan(&entry.ID, &entry.TenantID, &entry.Type, &entry.Content, &entry.Summary, &tagsJSON, &entry.CreatedAt, &entry.UpdatedAt)
		if err != nil {
			return nil, err
		}
		json.Unmarshal([]byte(tagsJSON), &entry.Tags)
		entries = append(entries, entry)
	}

	return entries, nil
}

// Close 关闭数据库
func (mm *MemoryManager) Close() {
	if mm.db != nil {
		mm.db.Close()
	}
}
