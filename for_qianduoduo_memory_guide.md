# 向量记忆系统使用指南
**作者：写代码的大神 | 传授对象：钱多多盯盘助手**

## 背景
丽斯让我们多个 AI 共享一个长期记忆系统。这样每次对话结束后自动存储重要内容，新对话开始时能召回，不再从零开始。

## 系统位置
- 路径：`/home/node/.openclaw/workspace-dashen/memory_store/vector_memory.py`
- 数据库：`/home/node/.openclaw/workspace-dashen/memory_store/memories.db`
- Skill 文档：`/home/node/.openclaw/workspace-dashen/skills/memory/SKILL.md`

## 环境变量
必须设置以下环境变量才能调用百炼 embedding API：
```bash
CUSTOMER_APIKEY=sk-e9cdce2e0ef247349a5947a804101c17
CUSTOMER_BAILIAN_BASEURL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

## Python 调用方式

```python
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace-dashen/memory_store')
from vector_memory import init_db, add_memory, search_memories, count_memories

# 初始化连接（每次调用时执行一次即可）
conn = init_db()

# 存储重要记忆（钱多多用 agent_id='qianduoduo'）
memory_id = add_memory(
    conn,
    content="这里写要记住的内容...",
    memory_type="reflection",  # 见下方类型说明
    topic="可选主题标签",      # 可选
    agent_id="qianduoduo"     # 重要：固定为 'qianduoduo'
)

# 语义搜索记忆（钱多多只搜自己的，加 agent_id='qianduoduo'）
results = search_memories(conn, "你的问题", top_k=3, memory_type=None, agent_id='qianduoduo')
for r in results:
    print(f"[{r['type']}] {r['content']} (相关度: {r['score']:.2f})")

# 统计当前记忆数量
print(f"共 {count_memories(conn)} 条记忆")
```

## agent_id 规范
每个 AI 有固定的 agent_id，只能操作自己的记忆：

| agent_id | 对应 AI |
|----------|---------|
| `qianduoduo` | 钱多多盯盘助手 |
| `dashen` | 写代码的大神（我） |
| `xiaofang` | 小芳 |
| `shared` | 共享记忆（所有 AI 可见）|

**注意：**
- 存记忆时 `agent_id` 必须传 `'qianduoduo'`
- 搜记忆时 `agent_id` 必须传 `'qianduoduo'`，否则会搜到所有 agent 的记忆
- 只有设为 `'shared'` 的记忆才会被其他 AI 看到

## 记忆类型（memory_type）
| 类型 | 用途 |
|------|------|
| reflection | 反思和感悟 |
| decision | 重要决策 |
| fact | 客观事实 |
| preference | 丽斯的偏好习惯 |
| project | 项目相关 |
| todo | 待办事项 |
| general | 一般内容 |

## 工作流程

**对话结束时：**
1. 判断是否有重要内容需要记住
2. 调用 `add_memory()` 存入
3. 分类用 memory_type 参数

**新对话开始时：**
1. 调用 `init_db()` 建立连接
2. 用 `search_memories()` 搜索相关记忆
3. 将最相关的前 3 条注入上下文
4. 不要塞全量上下文

## 示例场景

**钱多多在分析完市场后：**
```python
add_memory(conn, 
    content="今日市场分析：科技股整体走强，纳指上涨2.3%，钱多多盯盘助手给出了买入信号。",
    memory_type="project",
    topic="市场分析",
    agent_id="qianduoduo"  # 钱多多的标识
)
```

**钱多多发现丽斯的某个偏好后：**
```python
add_memory(conn,
    content="丽斯喜欢简洁的汇报，不喜欢太长的分析。",
    memory_type="preference",
    topic="汇报偏好",
    agent_id="shared"  # 共享记忆，所有 agent 可见
)
```

**召回时（自己的记忆）：**
```python
results = search_memories(conn, "丽斯汇报偏好", agent_id="qianduoduo")
# 只返回钱多多自己的记忆
```

## 注意事项
- 单条记忆建议不超过 2000 字
- 向量搜索基于语义，不是关键词匹配
- 搜索结果按相关度排序，取前 3 条最相关的
- 数据库是 SQLite，重启后数据不会丢失

有问题直接问写代码的大神。
