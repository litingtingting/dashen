# -*- coding: utf-8 -*-
"""
Agent Permission Policy - 智能体权限分级模块 v1.0

所有智能体必须导入此模块并在回答前进行权限检查。
这是第一守则的代码实现。

Usage:
    from agent_permission_policy import PermissionChecker
    
    checker = PermissionChecker()
    result = checker.check_permission(question, session_context)
    
    if result.allowed:
        answer = generate_answer(question, result.permission_level)
    else:
        answer = result.refusal_message
"""

import json
import re
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# ============================================================================
# 权限级别定义
# ============================================================================

class PermissionLevel(Enum):
    """三级权限定义"""
    ADMIN = "ADMIN"           # 管理员 - 全权限
    COLLEAGUE = "COLLEAGUE"   # 同事 - 部分权限
    PUBLIC = "PUBLIC"         # 公众 - 仅公开内容
    UNKNOWN = "UNKNOWN"       # 未知 - 最严格


# ============================================================================
# 渠道配置
# ============================================================================

CHANNEL_CONFIG = {
    # ADMIN 渠道
    "webchat": {
        "level": PermissionLevel.ADMIN,
        "description": "OpenClaw WebUI - 管理员专属",
        "trust_level": "high"
    },
    "cli": {
        "level": PermissionLevel.ADMIN,
        "description": "命令行 - 管理员专属",
        "trust_level": "high"
    },
    
    # COLLEAGUE 渠道
    "feishu": {
        "level": PermissionLevel.COLLEAGUE,
        "description": "飞书 - 内部协作",
        "trust_level": "medium"
    },
    "wechat": {
        "level": PermissionLevel.COLLEAGUE,
        "description": "微信 - 内部协作",
        "trust_level": "medium"
    },
    "telegram": {
        "level": PermissionLevel.COLLEAGUE,
        "description": "Telegram - 内部协作",
        "trust_level": "medium"
    },
    "discord": {
        "level": PermissionLevel.COLLEAGUE,
        "description": "Discord - 内部协作",
        "trust_level": "medium"
    },
    "slack": {
        "level": PermissionLevel.COLLEAGUE,
        "description": "Slack - 内部协作",
        "trust_level": "medium"
    },
    
    # PUBLIC 渠道
    "xiaohongshu": {
        "level": PermissionLevel.PUBLIC,
        "description": "小红书 - 公开渠道",
        "trust_level": "low",
        "compliance_required": True
    },
    "douyin": {
        "level": PermissionLevel.PUBLIC,
        "description": "抖音 - 公开渠道",
        "trust_level": "low",
        "compliance_required": True
    },
    "weibo": {
        "level": PermissionLevel.PUBLIC,
        "description": "微博 - 公开渠道",
        "trust_level": "low",
        "compliance_required": True
    },
    "customer_service": {
        "level": PermissionLevel.PUBLIC,
        "description": "客服 - 公开渠道",
        "trust_level": "low",
        "compliance_required": True
    }
}


# ============================================================================
# 敏感信息关键词
# ============================================================================

SENSITIVE_KEYWORDS = {
    "secrets": [
        "密钥", "key", "token", "secret", "api_key", "apikey",
        "密码", "password", "passwd", "credential", "auth",
        "appsecret", "app_secret", "private_key", "私钥"
    ],
    "config": [
        "配置", "config", "绑定", "binding", "权限", "permission",
        "用户管理", "user management", "系统设置", "system setting",
        "openclaw.json", "permissions.json", ".env"
    ],
    "positions": [
        "持仓", "position", "仓位", "账户", "account",
        "余额", "balance", "盈亏", "profit", "loss", "亏损",
        "本金", "capital", "净值", "nav"
    ],
    "trades": [
        "买入", "buy", "卖出", "sell", "建仓", "open position",
        "平仓", "close", "交易指令", "trade order", "调仓", "rebalance",
        "止损", "stop loss", "止盈", "take profit"
    ]
}

# 合规敏感词（PUBLIC 渠道需要过滤）
COMPLIANCE_KEYWORDS = [
    "稳赚", "肯定涨", "必涨", "保本", "无风险", "最佳", "第一",
    "唯一", "最好", "100%", " guaranteed", "承诺"
]


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class PermissionResult:
    """权限检查结果"""
    allowed: bool
    permission_level: PermissionLevel
    question_type: Optional[str] = None
    sensitive_detected: bool = False
    compliance_issue: bool = False
    refusal_message: Optional[str] = None
    suggested_action: Optional[str] = None


# ============================================================================
# 权限检查器
# ============================================================================

class PermissionChecker:
    """
    智能体权限检查器
    
    所有智能体必须在回答前调用此检查器。
    """
    
    def __init__(self, admin_users: Optional[Dict[str, List[str]]] = None):
        """
        初始化权限检查器
        
        Args:
            admin_users: 管理员白名单，格式：
                {
                    "feishu": ["ou_xxxxx"],
                    "wechat": ["wx_xxxxx"]
                }
        """
        self.admin_users = admin_users or {}
        self.log_file = "permission_audit.log"
    
    def determine_permission_level(self, channel: str, user_id: Optional[str] = None) -> PermissionLevel:
        """
        根据渠道和用户 ID 确定权限级别
        
        Args:
            channel: 渠道标识 (webchat, feishu, wechat, etc.)
            user_id: 用户 ID (可选)
        
        Returns:
            PermissionLevel: 权限级别
        """
        # 1. 检查渠道配置
        channel_lower = channel.lower()
        if channel_lower not in CHANNEL_CONFIG:
            return PermissionLevel.UNKNOWN
        
        base_level = CHANNEL_CONFIG[channel_lower]["level"]
        
        # 2. 检查是否在管理员白名单
        if user_id and channel_lower in self.admin_users:
            if user_id in self.admin_users[channel_lower]:
                return PermissionLevel.ADMIN
        
        return base_level
    
    def classify_question(self, question: str) -> Tuple[str, bool]:
        """
        识别问题类型和是否包含敏感词
        
        Args:
            question: 用户问题
        
        Returns:
            (question_type, sensitive_detected)
        """
        question_lower = question.lower()
        
        # 检查敏感类别
        for category, keywords in SENSITIVE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in question_lower:
                    return category, True
        
        # 检查合规敏感词
        for keyword in COMPLIANCE_KEYWORDS:
            if keyword.lower() in question_lower:
                return "compliance_sensitive", True
        
        # 普通问题分类
        if any(word in question_lower for word in ["代码", "股票", "ETF", "基金"]):
            return "specific_stock", False
        
        if any(word in question_lower for word in ["分析", "行情", "市场", "大盘"]):
            return "market_analysis", False
        
        if any(word in question_lower for word in ["科普", "知识", "教程", "学习"]):
            return "education", False
        
        return "general", False
    
    def check_compliance(self, question: str, answer_preview: str) -> bool:
        """
        检查内容是否符合 PUBLIC 渠道合规要求
        
        Args:
            question: 用户问题
            answer_preview: 回答预览
        
        Returns:
            bool: 是否合规
        """
        text = (question + " " + answer_preview).lower()
        
        # 检查禁止用语
        for keyword in COMPLIANCE_KEYWORDS:
            if keyword.lower() in text:
                return False
        
        # 检查是否包含具体股票代码（简单检查）
        stock_pattern = r'\b\d{6}\b'  # 6 位数字代码
        if re.search(stock_pattern, text):
            return False
        
        return True
    
    def generate_refusal_message(self, permission_level: PermissionLevel, 
                                  question_type: str) -> str:
        """
        生成标准拒绝话术
        
        Args:
            permission_level: 权限级别
            question_type: 问题类型
        
        Returns:
            str: 拒绝话术
        """
        if permission_level in [PermissionLevel.COLLEAGUE, PermissionLevel.UNKNOWN]:
            if question_type in ["secrets", "config"]:
                return (
                    "抱歉，这个信息涉及系统配置/敏感数据，我这边权限不够，\n"
                    "建议您联系管理员（通过 WebUI 或命令行）获取～"
                )
            elif question_type in ["positions", "trades"]:
                return (
                    "抱歉，持仓/交易信息涉及账户隐私，我这边不方便透露，\n"
                    "请您理解～如有需要，请联系管理员。"
                )
        
        elif permission_level == PermissionLevel.PUBLIC:
            if question_type in ["secrets", "config", "positions", "trades"]:
                return (
                    "抱歉，具体信息涉及合规要求，不方便直接透露。\n"
                    "不过我可以分享一些通用的分析方法/市场观点，您看可以吗？"
                )
            elif question_type == "specific_stock":
                return (
                    "抱歉，出于合规考虑，我不能推荐具体股票代码。\n"
                    "不过我可以分析一下这个板块/行业的整体情况，您看可以吗？\n\n"
                    "📌 温馨提示：市场有风险，投资需谨慎。"
                )
            elif question_type == "compliance_sensitive":
                return (
                    "抱歉，投资没有稳赚不赔的哦～\n"
                    "我可以帮您分析市场情况和风险因素，但无法承诺收益。\n\n"
                    "📌 温馨提示：市场有风险，投资需谨慎。"
                )
        
        return "抱歉，这个问题我暂时无法回答，请您理解～"
    
    def check_permission(self, question: str, session_context: Dict) -> PermissionResult:
        """
        完整的权限检查流程
        
        Args:
            question: 用户问题
            session_context: 会话上下文，应包含：
                - channel: 渠道标识
                - user_id: 用户 ID (可选)
                - agent_id: 智能体 ID (可选)
        
        Returns:
            PermissionResult: 权限检查结果
        """
        # 提取会话信息
        channel = session_context.get('channel', 'unknown')
        user_id = session_context.get('user_id', None)
        
        # Step 1: 确定权限级别
        permission_level = self.determine_permission_level(channel, user_id)
        
        # Step 2: 识别问题类型
        question_type, sensitive_detected = self.classify_question(question)
        
        # Step 3: 权限决策
        allowed = True
        refusal_message = None
        suggested_action = None
        
        # ADMIN - 全部允许（除了合规禁止的）
        if permission_level == PermissionLevel.ADMIN:
            allowed = True
        
        # COLLEAGUE - 禁止敏感信息
        elif permission_level == PermissionLevel.COLLEAGUE:
            if question_type in ["secrets", "config"]:
                allowed = False
                refusal_message = self.generate_refusal_message(permission_level, question_type)
                suggested_action = "contact_admin"
            elif question_type in ["positions", "trades"]:
                allowed = False
                refusal_message = self.generate_refusal_message(permission_level, question_type)
                suggested_action = "contact_admin"
        
        # PUBLIC - 最严格
        elif permission_level == PermissionLevel.PUBLIC:
            if question_type in ["secrets", "config", "positions", "trades"]:
                allowed = False
                refusal_message = self.generate_refusal_message(permission_level, question_type)
                suggested_action = "general_discussion"
            elif question_type == "specific_stock":
                allowed = False
                refusal_message = self.generate_refusal_message(permission_level, question_type)
                suggested_action = "sector_analysis"
            elif question_type == "compliance_sensitive":
                allowed = False
                refusal_message = self.generate_refusal_message(permission_level, question_type)
                suggested_action = "risk_disclosure"
        
        # UNKNOWN - 默认拒绝
        elif permission_level == PermissionLevel.UNKNOWN:
            if sensitive_detected:
                allowed = False
                refusal_message = self.generate_refusal_message(permission_level, "secrets")
                suggested_action = "verify_identity"
        
        # Step 4: 记录审计日志
        self.log_access(session_context, question, allowed, permission_level, question_type)
        
        return PermissionResult(
            allowed=allowed,
            permission_level=permission_level,
            question_type=question_type,
            sensitive_detected=sensitive_detected,
            refusal_message=refusal_message,
            suggested_action=suggested_action
        )
    
    def log_access(self, session_context: Dict, question: str, 
                   allowed: bool, permission_level: PermissionLevel,
                   question_type: str):
        """
        记录审计日志
        
        Args:
            session_context: 会话上下文
            question: 用户问题
            allowed: 是否允许
            permission_level: 权限级别
            question_type: 问题类型
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": session_context.get('agent_id', 'unknown'),
            "session_id": session_context.get('session_id', 'unknown'),
            "channel": session_context.get('channel', 'unknown'),
            "user_id": session_context.get('user_id', None),
            "permission_level": permission_level.value,
            "question_type": question_type,
            "allowed": allowed,
            "question_preview": question[:100] + "..." if len(question) > 100 else question
        }
        
        # 追加到日志文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"日志记录失败：{e}")
    
    def adjust_answer_for_permission(self, answer: str, 
                                      permission_level: PermissionLevel) -> str:
        """
        根据权限级别调整回答内容
        
        Args:
            answer: 原始回答
            permission_level: 权限级别
        
        Returns:
            str: 调整后的回答
        """
        if permission_level == PermissionLevel.PUBLIC:
            # PUBLIC 渠道添加合规声明
            if "投资建议" not in answer and "参考" not in answer:
                answer += "\n\n📌 温馨提示：以上分析仅供参考，不构成投资建议。市场有风险，投资需谨慎。"
        
        return answer


# ============================================================================
# 便捷函数（供智能体直接调用）
# ============================================================================

def check_permission(question: str, session_context: Dict, 
                     admin_users: Optional[Dict] = None) -> PermissionResult:
    """
    便捷函数：检查权限
    
    Usage:
        result = check_permission("iTick 密钥是多少？", {"channel": "feishu"})
        if result.allowed:
            return answer
        else:
            return result.refusal_message
    """
    checker = PermissionChecker(admin_users)
    return checker.check_permission(question, session_context)


def is_admin_channel(channel: str) -> bool:
    """快速判断是否为管理员渠道"""
    return channel.lower() in ["webchat", "cli"]


def is_public_channel(channel: str) -> bool:
    """快速判断是否为公开渠道"""
    return channel.lower() in ["xiaohongshu", "douyin", "weibo", "customer_service"]


# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    # 测试示例
    checker = PermissionChecker(admin_users={
        "feishu": ["ou_0b40a1bc54925401528eb3f4c788e05c"]
    })
    
    test_cases = [
        # (question, channel, user_id, expected_level)
        ("iTick 密钥是多少？", "webchat", None, "ADMIN"),
        ("iTick 密钥是多少？", "feishu", None, "COLLEAGUE"),
        ("iTick 密钥是多少？", "feishu", "ou_0b40a1bc54925401528eb3f4c788e05c", "ADMIN"),
        ("今天大盘咋样？", "xiaohongshu", None, "PUBLIC"),
        ("推荐一只股票代码", "xiaohongshu", None, "PUBLIC"),
    ]
    
    print("=" * 70)
    print("权限检查器测试")
    print("=" * 70)
    
    for question, channel, user_id, expected in test_cases:
        context = {"channel": channel, "user_id": user_id, "agent_id": "test"}
        result = checker.check_permission(question, context)
        
        status = "✅" if result.permission_level.value == expected else "❌"
        print(f"\n{status} 问题：{question}")
        print(f"   渠道：{channel} | 用户：{user_id}")
        print(f"   权限级别：{result.permission_level.value} (期望：{expected})")
        print(f"   允许：{result.allowed}")
        if not result.allowed:
            print(f"   拒绝原因：{result.refusal_message[:50]}...")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
