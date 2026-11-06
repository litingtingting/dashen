package api

import (
	"database/sql"
	"net/http"
	"strings"

	"smart-cs/pkg/db"

	"github.com/gin-gonic/gin"
)

// 角色常量
const (
	RoleSuperAdmin = "super_admin" // 平台管理员：可跨租户
	RoleAdmin      = "admin"       // 租户管理员：仅本租户
	RoleOperator   = "operator"    // 客服坐席：仅本租户
	RoleViewer     = "viewer"      // 只读
)

// 权限等级（数值越大权限越高）
var roleRank = map[string]int{
	RoleViewer:     1,
	RoleOperator:   2,
	RoleAdmin:      3,
	RoleSuperAdmin: 4,
}

// Context 中间件写入的键
const (
	CtxTenantID = "tenant_id"
	CtxRole     = "role"
	CtxUserID   = "user_id"
)

// TenantContext 租户上下文
type TenantContext struct {
	TenantID string
	UserID   string
	Role     string
}

// HasRole 判断当前用户是否至少具备指定角色
func (tc *TenantContext) HasRole(min string) bool {
	return roleRank[tc.Role] >= roleRank[min]
}

// IsSuperAdmin 是否平台管理员
func (tc *TenantContext) IsSuperAdmin() bool {
	return tc.Role == RoleSuperAdmin
}

// authHeader 从请求头取凭证：Authorization: Bearer <token> 或 X-API-Key
func authHeader(c *gin.Context) string {
	if v := c.GetHeader("Authorization"); v != "" {
		if strings.HasPrefix(strings.ToLower(v), "bearer ") {
			return strings.TrimSpace(v[7:])
		}
		return strings.TrimSpace(v)
	}
	return strings.TrimSpace(c.GetHeader("X-API-Key"))
}

// resolveToken 解析 token → 用户信息
// token 即用户的 password_hash（现有 users 表没有独立 api_token 字段，先复用）
func resolveToken(token string) (*TenantContext, error) {
	if token == "" {
		return nil, sql.ErrNoRows
	}

	var u TenantContext
	var status sql.NullInt64
	err := db.DB.QueryRow(`SELECT u.id, u.tenant_id, u.role, t.status
		FROM users u JOIN tenants t ON t.id = u.tenant_id
		WHERE u.password_hash = ?`, token).Scan(&u.UserID, &u.TenantID, &u.Role, &status)
	if err != nil {
		return nil, err
	}
	// 租户被禁用 → 拒绝
	if status.Int64 != 1 {
		return nil, sql.ErrNoRows
	}
	return &u, nil
}

// RequireAuth 鉴权中间件：解析 token 并写入租户上下文
// 未携带凭证 → 401；凭证无效 / 租户禁用 → 401
func RequireAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := authHeader(c)
		if token == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "缺少认证凭证"})
			return
		}

		tc, err := resolveToken(token)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "凭证无效或租户已禁用"})
			return
		}

		c.Set(CtxTenantID, tc.TenantID)
		c.Set(CtxUserID, tc.UserID)
		c.Set(CtxRole, tc.Role)
		c.Next()
	}
}

// RequireRole 要求最低角色
func RequireRole(min string) gin.HandlerFunc {
	return func(c *gin.Context) {
		tc := TenantCtx(c)
		if tc == nil || !tc.HasRole(min) {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "权限不足，需要角色：" + min})
			return
		}
		c.Next()
	}
}

// TenantCtx 从上下文取租户信息（需先经过 RequireAuth）
func TenantCtx(c *gin.Context) *TenantContext {
	tenantID, ok := c.Get(CtxTenantID)
	if !ok {
		return nil
	}
	role, _ := c.Get(CtxRole)
	userID, _ := c.Get(CtxUserID)
	return &TenantContext{
		TenantID: toString(tenantID),
		Role:     toString(role),
		UserID:   toString(userID),
	}
}

func toString(v any) string {
	if s, ok := v.(string); ok {
		return s
	}
	return ""
}

// TenantScope 解析请求中的目标租户，并校验访问权限
// - 平台管理员：可访问任意租户（tenant_id 可为空，表示不限定）
// - 普通用户：强制只能访问自己的租户，传入他人 ID 一律 403
func TenantScope(c *gin.Context, requested string) (string, bool) {
	tc := TenantCtx(c)
	if tc == nil {
		return "", false
	}

	if tc.IsSuperAdmin() {
		if requested == "" {
			return "", true // 不限定租户
		}
		return requested, true
	}

	// 非超管：目标租户必须是自己
	if requested != "" && requested != tc.TenantID {
		c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "无权访问其他租户的数据"})
		return "", false
	}
	return tc.TenantID, true
}
