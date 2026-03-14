package api

import (
	"net/http"
	"time"

	"smart-cs/pkg/db"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// Tenant 租户结构
type Tenant struct {
	ID           string    `json:"id"`
	Name         string    `json:"name"`
	Type         string    `json:"type"`
	PlatformID   string    `json:"platform_id"`
	PersonaConfig string   `json:"persona_config"`
	Status       int       `json:"status"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

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

	var tenant Tenant
	err := db.DB.QueryRow(`SELECT id, name, type, platform_id, persona_config, status, created_at, updated_at 
		FROM tenants WHERE id = ?`, id).Scan(
		&tenant.ID, &tenant.Name, &tenant.Type, &tenant.PlatformID, 
		&tenant.PersonaConfig, &tenant.Status, &tenant.CreatedAt, &tenant.UpdatedAt)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "租户不存在"})
		return
	}

	c.JSON(http.StatusOK, tenant)
}

// updateTenant 更新租户
func updateTenant(c *gin.Context) {
	id := c.Param("id")

	var req Tenant
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	_, err := db.DB.Exec(`UPDATE tenants SET name=?, type=?, platform_id=?, persona_config=?, status=? 
		WHERE id = ?`,
		req.Name, req.Type, req.PlatformID, req.PersonaConfig, req.Status, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "租户更新成功"})
}

// deleteTenant 删除租户
func deleteTenant(c *gin.Context) {
	id := c.Param("id")

	_, err := db.DB.Exec(`DELETE FROM tenants WHERE id = ?`, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "租户删除成功"})
}

// listTenants 列出所有租户
func listTenants(c *gin.Context) {
	rows, err := db.DB.Query(`SELECT id, name, type, platform_id, persona_config, status, created_at, updated_at 
		FROM tenants ORDER BY created_at DESC`)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	var tenants []Tenant
	for rows.Next() {
		var t Tenant
		if err := rows.Scan(&t.ID, &t.Name, &t.Type, &t.PlatformID, &t.PersonaConfig, 
			&t.Status, &t.CreatedAt, &t.UpdatedAt); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		tenants = append(tenants, t)
	}

	c.JSON(http.StatusOK, gin.H{"tenants": tenants})
}
