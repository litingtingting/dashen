# -*- coding: utf-8 -*-
"""
安全输出工具 - 敏感信息零明文输出

核心原则：
- 任何渠道、任何人都不能明文输出敏感信息
- 只显示状态或哈希值，用于验证而非泄露
- 渠道权限只控制操作权限，不控制显示权限

使用方式:
    from permission.secure_output import safe_print, hash_sensitive_value
    
    # 安全打印（自动脱敏，任何渠道都一样）
    safe_print({"token": "abc123"}, context="CONFIG")
    # 输出：{'token': '***'} 或 {'token': '已配置 (哈希：a1b2c3d4...)'}
"""

import os
import re
import hashlib
from typing import Any, Dict, List, Optional, Union


# 敏感信息关键词（不区分大小写）
SENSITIVE_KEYWORDS = [
    'token', 'key', 'secret', 'password', 'passwd', 'pwd',
    'api_key', 'apikey', 'api-key', 'credential', 'auth',
    'ITICK_TOKEN', 'TUSHARE_TOKEN', 'BRAVE_API_KEY',
    '密钥', '密码', '口令', '凭证'
]

# 敏感环境变量前缀
SENSITIVE_ENV_PREFIXES = ['TOKEN', 'KEY', 'SECRET', 'PASSWORD', 'PWD', 'AUTH']

# 渠道列表（仅用于审计，不用于权限判断）
KNOWN_CHANNELS = ['webchat', 'cli', 'feishu', 'wechat', 'telegram', 'xiaohongshu']


def is_sensitive_key(key: str) -> bool:
    """检查键名是否敏感"""
    key_upper = key.upper()
    for keyword in SENSITIVE_KEYWORDS:
        if keyword.upper() in key_upper:
            return True
    for prefix in SENSITIVE_ENV_PREFIXES:
        if key_upper.startswith(prefix) or key_upper.endswith(prefix):
            return True
    return False


def hash_sensitive_value(value: str, length: int = 8) -> str:
    """
    计算敏感值的哈希（用于验证，不可逆）
    
    Args:
        value: 原始值
        length: 哈希显示长度
        
    Returns:
        哈希字符串，如 "a1b2c3d4..."
    """
    if not value:
        return "***"
    hash_hex = hashlib.sha256(value.encode()).hexdigest()
    return f"{hash_hex[:length]}..."


def mask_value(value: str, show_chars: int = 0) -> str:
    """
    脱敏显示值（完全隐藏或部分隐藏）
    
    Args:
        value: 原始值
        show_chars: 显示的字符数（0 表示完全隐藏）
        
    Returns:
        脱敏后的字符串
    """
    if not value or not isinstance(value, str):
        return "***"
    
    if show_chars <= 0:
        return "***"
    
    if len(value) <= show_chars * 2:
        return "***"
    
    return f"{value[:show_chars]}...{value[-show_chars:]}"


def safe_print(data: Any, channel: str = 'unknown', context: str = "") -> None:
    """
    安全打印 - 任何渠道都脱敏敏感信息
    
    Args:
        data: 要打印的数据
        channel: 渠道类型（仅用于审计）
        context: 上下文描述（可选）
    """
    if isinstance(data, dict):
        safe_dict = {}
        for key, value in data.items():
            if is_sensitive_key(key):
                # 任何渠道都脱敏
                safe_dict[key] = "***"
            else:
                safe_dict[key] = value
        print(f"[{context}] " if context else "", end="")
        print(safe_dict)
    elif isinstance(data, str):
        # 检查字符串中是否包含敏感信息
        safe_str = data
        for keyword in SENSITIVE_KEYWORDS:
            pattern = rf'{keyword}\s*[=:]\s*["\']?([a-zA-Z0-9_\-]+)["\']?'
            match = re.search(pattern, safe_str, re.IGNORECASE)
            if match:
                original = match.group(0)
                masked = f'{keyword}=***'
                safe_str = safe_str.replace(original, masked)
        print(f"[{context}] " if context else "", end="")
        print(safe_str)
    else:
        print(f"[{context}] " if context else "", end="")
        print(data)


def get_sensitive_value(key: str) -> Optional[str]:
    """
    获取敏感值 - 仅供内部使用，不直接输出
    
    Args:
        key: 环境变量名
        
    Returns:
        敏感值（用于内部操作，不应用于输出）
    """
    return os.environ.get(key)


def check_env_safety() -> Dict[str, str]:
    """
    检查环境变量中的敏感信息（只显示状态和哈希）
    
    Returns:
        字典，键为变量名，值为状态和哈希
    """
    result = {}
    sensitive_vars = [
        'ITICK_TOKEN',
        'TUSHARE_TOKEN',
        'BRAVE_API_KEY',
        'API_KEY',
        'SECRET_KEY',
        'PASSWORD'
    ]
    
    for var in sensitive_vars:
        value = os.environ.get(var)
        if value:
            # 显示状态和哈希（用于验证，不可逆）
            result[var] = f"已配置 (SHA256: {hash_sensitive_value(value, 8)})"
        else:
            result[var] = "未配置"
    
    return result


def safe_config_display(config: Dict) -> Dict:
    """
    安全显示配置 - 脱敏所有敏感字段
    
    Args:
        config: 配置字典
        
    Returns:
        脱敏后的配置字典
    """
    safe_config = {}
    for key, value in config.items():
        if is_sensitive_key(key):
            safe_config[key] = "***"
        elif isinstance(value, dict):
            safe_config[key] = safe_config_display(value)
        else:
            safe_config[key] = value
    return safe_config


def verify_token(token: str, expected_hash: str) -> bool:
    """
    验证 Token 是否匹配预期哈希
    
    Args:
        token: 待验证的 Token
        expected_hash: 预期的哈希值（如之前存储的）
        
    Returns:
        bool: 是否匹配
    """
    if not token or not expected_hash:
        return False
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token_hash == expected_hash


def log_audit(channel: str, user_id: str, action: str, sensitive: bool = False, result: str = "success") -> None:
    """
    记录审计日志
    
    Args:
        channel: 渠道类型
        user_id: 用户 ID（应脱敏）
        action: 操作类型
        sensitive: 是否涉及敏感信息
        result: 操作结果
    """
    # 脱敏用户 ID
    masked_user_id = f"{user_id[:6]}***" if user_id and len(user_id) > 6 else user_id
    
    timestamp = __import__('datetime').datetime.now().isoformat()
    log_entry = f"[{timestamp}] channel={channel} user={masked_user_id} action={action} sensitive={sensitive} result={result}"
    
    # 输出审计日志（不包含敏感信息）
    print(f"[AUDIT] {log_entry}")


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("安全输出工具 - 测试（零明文输出）")
    print("=" * 60)
    
    # 测试数据
    test_dict = {
        'username': 'qianduoduo',
        'itick_token': '45e58053174b44afa9149798341e4e036cb31e9edfda4a899ed7f5906dcee7ff',
        'password': 'secret123',
        'watchlist': ['510300.SH', '159915.SZ']
    }
    
    # 测试 1: ADMIN 渠道（仍然脱敏）
    print("\n[测试 1] ADMIN 渠道 (webchat) - 仍然脱敏:")
    safe_print(test_dict, channel='webchat', context="ADMIN")
    
    # 测试 2: COLLEAGUE 渠道（脱敏）
    print("\n[测试 2] COLLEAGUE 渠道 (feishu) - 脱敏:")
    safe_print(test_dict, channel='feishu', context="COLLEAGUE")
    
    # 测试 3: PUBLIC 渠道（脱敏）
    print("\n[测试 3] PUBLIC 渠道 (xiaohongshu) - 脱敏:")
    safe_print(test_dict, channel='xiaohongshu', context="PUBLIC")
    
    # 测试 4: 环境变量检查（显示哈希）
    print("\n[测试 4] 环境变量状态（显示哈希，用于验证）:")
    env_status = check_env_safety()
    for k, v in env_status.items():
        print(f"  {k}: {v}")
    
    # 测试 5: 审计日志
    print("\n[测试 5] 审计日志示例:")
    log_audit('webchat', 'ou_0b40a1bc54925401528eb3f4c788e05c', 'query_token', sensitive=True)
    
    print("\n" + "=" * 60)
    print("测试完成 - 所有敏感信息已脱敏（包括 ADMIN 渠道）")
    print("=" * 60)
