package api

import (
	"database/sql"
	"net/http"
	"time"

	"smart-cs/pkg/db"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// Tenant 租户结构
type Tenant struct {
	ID            string    `json:"id"`
	Name          string    `json:"name"`
	Type          string    `json:"type"`
	PlatformID    string    `json:"platform_id"`
	PersonaConfig string    `json:"persona_config"`
	Status        int       `json:"status"`
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
}

// tenantRow 用于扫描 tenants 表，兼容可空字段（platform_id / persona_config 可能为 NULL）
type tenantRow struct {
	ID            string
	Name          string
	Type          string
	PlatformID    sql.NullString
	PersonaConfig sql.NullString
	Status        sql.NullInt64
	CreatedAt     sql.NullTime
	UpdatedAt     sql.NullTime
}

// toTenant 将扫描结果转换为对外结构，NULL 一律归一化为零值
func (r tenantRow) toTenant() Tenant {
	return Tenant{
		ID:            r.ID,
		Name:          r.Name,
		Type:          r.Type,
		PlatformID:    r.PlatformID.String,
		PersonaConfig: r.PersonaConfig.String,
		Status:        int(r.Status.Int64),
		CreatedAt:     r.CreatedAt.Time,
		UpdatedAt:     r.UpdatedAt.Time,
	}
}

const tenantColumns = `id, name, type, platform_id, persona_config, status, created_at, updated_at`

// createTenant 创建租户
func createTenant(c *gin.Context) {
	var req Tenant
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 生成 ID
	if req.ID == "" {
		req.ID = uuid.New().String()
	}

	// 插入数据库
	_, err := db.DB.Exec(`INSERT INTO tenants (id, name, type, platform_id, persona_config, status)
		VALUES (?, ?, ?, ?, ?, ?)`,
		req.ID, req.Name, req.Type, req.PlatformID, req.PersonaConfig, req.Status)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": req.ID, "message": "租户创建成功"})
}

// getTenant 获取租户
func getTenant(c *gin.Context) {
	id := c.Param("id")

	var row tenantRow
	err := db.DB.QueryRow(`SELECT `+tenantColumns+` FROM tenants WHERE id = ?`, id).Scan(
		&row.ID, &row.Name, &row.Type, &row.PlatformID,
		&row.PersonaConfig, &row.Status, &row.CreatedAt, &row.UpdatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "租户不存在"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, row.toTenant())
}

// updateTenant 更新租户
func updateTenant(c *gin.Context) {
	id := c.Param("id")

	var req Tenant
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	res, err := db.DB.Exec(`UPDATE tenants SET name=?, type=?, platform_id=?, persona_config=?, status=?
		WHERE id = ?`,
		req.Name, req.Type, req.PlatformID, req.PersonaConfig, req.Status, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if n, _ := res.RowsAffected(); n == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "租户不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "租户更新成功"})
}

// deleteTenant 删除租户
func deleteTenant(c *gin.Context) {
	id := c.Param("id")

	res, err := db.DB.Exec(`DELETE FROM tenants WHERE id = ?`, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if n, _ := res.RowsAffected(); n == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "租户不存在"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "租户删除成功"})
}

// listTenants 列出所有租户
func listTenants(c *gin.Context) {
	rows, err := db.DB.Query(`SELECT ` + tenantColumns + ` FROM tenants ORDER BY created_at DESC`)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	tenants := make([]Tenant, 0)
	for rows.Next() {
		var row tenantRow
		if err := rows.Scan(&row.ID, &row.Name, &row.Type, &row.PlatformID,
			&row.PersonaConfig, &row.Status, &row.CreatedAt, &row.UpdatedAt); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		tenants = append(tenants, row.toTenant())
	}
	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"tenants": tenants})
}
