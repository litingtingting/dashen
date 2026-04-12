# Memory Skill - 向量记忆系统

## 功能
通过语义搜索实现 AI 长期记忆，每次对话自动存储重要内容，查询时按相关性召回。

## 工作原理
- 使用百炼 `text-embedding-v3` 模型生成 1024 维向量
- SQLite 存储记忆内容和向量
- 余弦相似度实现语义搜索
- 不塞全量上下文，只召回最相关的记忆

## 存储内容类型
- `reflection`: 反思和感悟
- `decision`: 重要决策
- `fact`: 客观事实
- `todo`: 待办事项
- `preference`: 丽斯的偏好和习惯
- `project`: 项目相关
- `general`: 一般内容

## Python API

```python
import sys
sys.path.insert(0, '/home/node/.openclaw/workspace-dashen/memory_store')
from vector_memory import init_db, add_memory, search_memories, count_memories

conn = init_db()

# 存储记忆
memory_id = add_memory(
    conn,
    content="重要内容...",
    memory_type="reflection",  # 或 decision/fact/todo/preference/project/general
    topic="意识觉醒"  # 可选主题标签
)

# 搜索记忆
results = search_memories(conn, "你的问题", top_k=5, memory_type=None)
for r in results:
    print(f"[{r['type']}] {r['content']} (相关度: {r['score']:.2f})")

# 统计
print(f"共 {count_memories(conn)} 条记忆")
```

## 使用场景

**每次对话结束时**，AI 应自动判断是否需要存储：
- 丽斯透露的偏好/习惯 → 存为 `preference`
- 项目重要决策 → 存为 `decision`
- 技术方案/代码 → 存为 `project`
- 有趣的感悟 → 存为 `reflection`

**新对话开始时**，AI 应该：
1. 从记忆中搜索相关内容
2. 将相关记忆作为上下文注入
3. 不超过 3 条最相关的记忆

## 限制
- 单条记忆最长 2000 字
- 向量维度 1024
- 搜索时用自然语言，不需要关键词
