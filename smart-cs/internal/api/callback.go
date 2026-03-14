package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// handleWechatCallback 微信回调
func handleWechatCallback(c *gin.Context) {
	// 微信验证
	if c.Request.Method == "GET" {
		handleWechatVerify(c)
		return
	}

	// 接收消息
	handleWechatMessage(c)
}

// handleWechatVerify 微信服务器验证
func handleWechatVerify(c *gin.Context) {
	echostr := c.Query("echostr")
	// TODO: 验证 signature
	c.String(http.StatusOK, echostr)
}

// handleWechatMessage 处理微信消息
func handleWechatMessage(c *gin.Context) {
	// TODO: 解析 XML 消息
	// TODO: 调用 AI 生成回复
	// TODO: 返回 XML 响应
	c.String(http.StatusOK, "success")
}

// handleTaobaoCallback 淘宝回调
func handleTaobaoCallback(c *gin.Context) {
	// TODO: 解析淘宝消息
	// TODO: 调用 AI 生成回复
	c.String(http.StatusOK, "success")
}

// handleDouyinCallback 抖音回调
func handleDouyinCallback(c *gin.Context) {
	// TODO: 解析抖音消息
	// TODO: 调用 AI 生成回复
	c.String(http.StatusOK, "success")
}

// handleJoinPage 企业对接页面
func handleJoinPage(c *gin.Context) {
	html := `
<!DOCTYPE html>
<html>
<head>
    <title>智能客服系统 - 企业接入申请</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; box-sizing: border-box; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>🤖 智能客服系统 - 企业接入申请</h1>
    <form action="/api/join/submit" method="POST">
        <div class="form-group">
            <label>企业名称 *</label>
            <input type="text" name="company_name" required>
        </div>
        <div class="form-group">
            <label>联系人 *</label>
            <input type="text" name="contact_name" required>
        </div>
        <div class="form-group">
            <label>手机号 *</label>
            <input type="tel" name="phone" required pattern="[0-9]{11}">
        </div>
        <div class="form-group">
            <label>邮箱 *</label>
            <input type="email" name="email" required>
        </div>
        <div class="form-group">
            <label>接入平台 *</label>
            <select name="platforms" multiple>
                <option value="wechat">微信公众号</option>
                <option value="taobao">淘宝店铺</option>
                <option value="douyin">抖音企业号</option>
            </select>
        </div>
        <div class="form-group">
            <label>选择套餐 *</label>
            <select name="plan">
                <option value="free">体验版（免费）</option>
                <option value="standard">标准版（¥99/月）</option>
                <option value="pro">专业版（¥299/月）</option>
                <option value="enterprise">企业版（面议）</option>
            </select>
        </div>
        <button type="submit">提交申请</button>
    </form>
</body>
</html>
`
	c.Data(http.StatusOK, "text/html; charset=utf-8", []byte(html))
}

// handleJoinSubmit 处理企业对接提交
func handleJoinSubmit(c *gin.Context) {
	// TODO: 保存到数据库
	// TODO: 通知管理员
	c.String(http.StatusOK, "提交成功！我们会尽快联系您～")
}
