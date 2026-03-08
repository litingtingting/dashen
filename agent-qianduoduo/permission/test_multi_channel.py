# -*- coding: utf-8 -*-
from agent_permission_policy import PermissionChecker

# 配置白名单
admin_users = {
    'feishu': ['ou_admin1', 'ou_admin2'],
    'wechat': ['wx_admin1'],
    'telegram': ['tg_admin1'],
    'discord': ['ds_admin1']
}

checker = PermissionChecker(admin_users=admin_users)

# 测试多渠道
test_cases = [
    ('feishu', None, 'COLLEAGUE'),
    ('feishu', 'ou_admin1', 'ADMIN'),
    ('wechat', None, 'COLLEAGUE'),
    ('wechat', 'wx_admin1', 'ADMIN'),
    ('telegram', None, 'COLLEAGUE'),
    ('telegram', 'tg_admin1', 'ADMIN'),
    ('discord', None, 'COLLEAGUE'),
    ('discord', 'ds_admin1', 'ADMIN'),
    ('xiaohongshu', None, 'PUBLIC'),
    ('xiaohongshu', 'any_user', 'PUBLIC'),  # PUBLIC 渠道不可提升
]

print('=' * 70)
print('Multi-Channel Permission Test')
print('=' * 70)

all_passed = True
for channel, user_id, expected in test_cases:
    level = checker.determine_permission_level(channel, user_id)
    passed = level.value == expected
    all_passed = all_passed and passed
    status = 'PASS' if passed else 'FAIL'
    print(f'{status} | {channel:15} + {str(user_id):20} -> {level.value:12} (expected: {expected})')

print('=' * 70)
result = 'ALL PASSED' if all_passed else 'SOME FAILED'
print(f'Result: {result}')
print('=' * 70)
