package api

import (
	"crypto/sha256"
	"encoding/hex"
	"net/http"
	"time"

	"smart-cs/pkg/db"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// User 用户结构
type User struct {
	ID           string    `json:"id"`
	TenantID     string    `json:"tenant_id"`
	Username     string    `json:"username"`
	PasswordHash string    `json:"-"` // 不输出密码
	Role         string    `json:"role"`
	CreatedAt    time.Time `json:"created_at"`
}

// LoginRequest 登录请求
type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// hashPassword 密码哈希
func hashPassword(password string) string {
	hash := sha256.Sum256([]byte(password))
	return hex.EncodeToString(hash[:])
}

// createUser 创建用户
func createUser(c *gin.Context) {
	var req User
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 生成 ID
	if req.ID == "" {
		req.ID = uuid.New().String()
	}

	// 密码哈希
	req.PasswordHash = hashPassword(req.PasswordHash)

	// 插入数据库
	_, err := db.DB.Exec(`INSERT INTO users (id, tenant_id, username, password_hash, role) 
		VALUES (?, ?, ?, ?, ?)`,
		req.ID, req.TenantID, req.Username, req.PasswordHash, req.Role)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": req.ID, "message": "用户创建成功"})
}

// userLogin 用户登录
func userLogin(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	passwordHash := hashPassword(req.Password)

	var user User
	err := db.DB.QueryRow(`SELECT id, tenant_id, username, role, created_at 
		FROM users WHERE username = ? AND password_hash = ?`,
		req.Username, passwordHash).Scan(
		&user.ID, &user.TenantID, &user.Username, &user.Role, &user.CreatedAt)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "用户名或密码错误"})
		return
	}

	// TODO: 生成 JWT token
	token := "mock_jwt_token_" + user.ID

	c.JSON(http.StatusOK, gin.H{
		"user":  user,
		"token": token,
	})
}

// getUser 获取用户
func getUser(c *gin.Context) {
	id := c.Param("id")

	var user User
	err := db.DB.QueryRow(`SELECT id, tenant_id, username, role, created_at 
		FROM users WHERE id = ?`, id).Scan(
		&user.ID, &user.TenantID, &user.Username, &user.Role, &user.CreatedAt)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "用户不存在"})
		return
	}

	c.JSON(http.StatusOK, user)
}

// updateUser 更新用户
func updateUser(c *gin.Context) {
	id := c.Param("id")

	var req User
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	_, err := db.DB.Exec(`UPDATE users SET tenant_id=?, username=?, role=? WHERE id = ?`,
		req.TenantID, req.Username, req.Role, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "用户更新成功"})
}

// deleteUser 删除用户
func deleteUser(c *gin.Context) {
	id := c.Param("id")

	_, err := db.DB.Exec(`DELETE FROM users WHERE id = ?`, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "用户删除成功"})
}
