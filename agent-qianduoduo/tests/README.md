# agent-qianduoduo/test/

## 测试用例目录

### 测试分类
| 测试类型 | 文件 | 说明 |
|---------|------|------|
| 单元测试 | `test_dockerfile.py` | Dockerfile 构建验证 |
| 集成测试 | `test_compose.py` | docker-compose 编排验证 |
| 端到端测试 | `test_e2e.py` | 完整流程验证 |
| 安全测试 | `test_security.py` | 密钥安全验证 |

### 运行方式
```bash
# 在 agent-qianduoduo/ 目录下
python -m pytest tests/ -v

# 运行单独测试
python tests/test_dockerfile.py
python tests/test_compose.py
```

---

*作者：dashen | 时间：2026-03-08*
