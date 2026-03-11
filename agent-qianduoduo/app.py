from flask import Flask, request, jsonify
import logging
import requests
import os
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 从环境变量读取百炼配置（也可以在代码中硬编码，但不安全）
BAILIAN_API_KEY = os.environ.get('BAILIAN_API_KEY', '你的百炼API Key')
BAILIAN_MODEL = os.environ.get('BAILIAN_MODEL', 'qwen-max')  # 默认模型
BAILIAN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 百炼兼容OpenAI的地址

def call_bailian(messages):
    """
    调用百炼模型，返回回复内容
    messages 格式：[
        {"role": "system", "content": "你是一个财务分析助手"},
        {"role": "user", "content": "用户消息"}
    ]
    """
    headers = {
        "Authorization": f"Bearer {BAILIAN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": BAILIAN_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            f"{BAILIAN_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        # 提取回复内容
        reply = result['choices'][0]['message']['content']
        return reply
    except Exception as e:
        logger.error(f"调用百炼失败: {e}")
        return f"【错误】无法获取模型回复：{str(e)}"

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    接收 OpenClaw 转发来的消息，调用百炼处理，返回回复。
    请求体格式示例：
    {
        "text": "用户说的内容",
        "sender": "用户ID",
        "channel": "feishu",
        "session_id": "xxx"
    }
    需要返回的格式：
    {
        "text": "回复内容",
        "type": "text"
    }
    """
    try:
        data = request.get_json()
        logger.info(f"收到来自 OpenClaw 的消息: {data}")

        user_message = data.get('text', '')
        sender = data.get('sender', 'unknown')
        session_id = data.get('session_id', 'default')

        # --- 构建发送给百炼的消息列表 ---
        # 你可以在这里加入 system prompt，定义钱多多的性格和能力
        messages = [
            {
                "role": "system", 
                "content": "你叫钱多多，是一名专业的财务分析助手。你的回答要简洁、准确，善于分析数据。用户可能会问你财务报表、投资建议、税务问题等，请用专业但易懂的语言回答。"
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        # 调用百炼模型
        reply_text = call_bailian(messages)

        # 返回给 OpenClaw
        return jsonify({
            "text": reply_text,
            "type": "text"
        })
    except Exception as e:
        logger.exception("处理 webhook 时出错")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

if __name__ == '__main__':
    # 监听所有网络接口，端口5000
    app.run(host='0.0.0.0', port=5000, debug=False)
