# -*- coding: utf-8 -*-
from agent_permission_policy import PermissionChecker

# 配置白名单
admin_users = {
    'feishu': ['ou_0b40a1bc54925401528eb3f4c788e05c'],  # 丽斯的飞书 ID
    'wechat': ['wx_admin1']
}

checker = PermissionChecker(admin_users=admin_users)

print('=' * 70)
print('Test: Admin whitelist users in COLLEAGUE channels')
print('=' * 70)

test_cases = [
    ('feishu', None, 'Normal Feishu user (no user ID)'),
    ('feishu', 'ou_0b40a1bc54925401528eb3f4c788e05c', 'Lisi (Admin in whitelist)'),
    ('feishu', 'ou_other_user', 'Other Feishu user'),
    ('wechat', None, 'Normal WeChat user (no user ID)'),
    ('wechat', 'wx_admin1', 'WeChat Admin'),
    ('wechat', 'wx_other_user', 'Other WeChat user'),
]

for channel, user_id, description in test_cases:
    level = checker.determine_permission_level(channel, user_id)
    can_answer_secrets = (level.value == 'ADMIN')
    
    print(f'{description}')
    print(f'  Channel: {channel} | User ID: {user_id}')
    print(f'  Permission Level: {level.value}')
    status = 'YES' if can_answer_secrets else 'NO'
    print(f'  Can answer secrets/positions: {status}')
    print()

print('=' * 70)
