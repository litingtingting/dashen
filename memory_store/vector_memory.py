#!/usr/bin/env python3
"""
向量记忆系统 - Vector Memory System
使用百炼 API 做 embedding，SQLite 存储，实现语义搜索
"""
import sqlite3
import json
import os
import math
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

DB_PATH = "/home/node/.openclaw/workspace-dashen/memory_store/memories.db"
EMBEDDING_DIM = 1024  # text-embedding-v3 dimension

# 百炼 API 配置
BAILIAN_APIKEY = os.environ.get("CUSTOMER_APIKEY", "")
BAILIAN_BASEURL = os.environ.get("CUSTOMER_BAILIAN_BASEURL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

def get_embedding(text: str) -> list[float]:
    """调用百炼 API 获取文本 embedding"""
    if not BAILIAN_APIKEY:
        raise ValueError("BAILIAN_APIKEY not set")
    
    url = f"{BAILIAN_BASEURL}/embeddings"
    headers = {
        "Authorization": f"Bearer {BAILIAN_APIKEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "text-embedding-v3",
        "input": text
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP {e.code}: {e.read().decode()}")
    return result["data"][0]["embedding"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算两个向量的余弦相似度"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def init_db():
    """初始化数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 记忆表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'general',
            topic TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # 向量表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id INTEGER NOT NULL,
            vector TEXT NOT NULL,
            FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
        )
    """)
    
    # FTS5 全文搜索
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
            content, topic, content=memories, content_rowid=id
        )
    """)
    
    # 向量索引（简化版：用 memory_id 关联）
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_embeddings_memory_id ON embeddings(memory_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_topic ON memories(topic)
    """)
    
    conn.commit()
    return conn


def add_memory(conn: sqlite3.Connection, content: str, memory_type: str = "general", topic: str = None) -> int:
    """添加记忆并生成向量"""
    now = datetime.now().isoformat()
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (content, type, topic, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (content, memory_type, topic, now, now)
    )
    memory_id = cursor.lastrowid
    
    # 生成 embedding
    try:
        vector = get_embedding(content)
        vector_json = json.dumps(vector)
        cursor.execute(
            "INSERT INTO embeddings (memory_id, vector) VALUES (?, ?)",
            (memory_id, vector_json)
        )
    except Exception as e:
        print(f"Warning: Failed to generate embedding: {e}")
    
    # 更新 FTS
    cursor.execute("INSERT INTO memories_fts(rowid, content, topic) VALUES (?, ?, ?)",
                   (memory_id, content, topic or ""))
    
    conn.commit()
    return memory_id


def search_memories(conn: sqlite3.Connection, query: str, top_k: int = 5, memory_type: str = None) -> list[dict]:
    """语义搜索记忆 - 使用 LIKE + 向量相似度混合"""
    cursor = conn.cursor()
    
    # 构造候选查询（中文 FTS 有分词问题，改用 LIKE）
    like_pattern = f"%{query}%"
    if memory_type:
        cursor.execute("""
            SELECT m.id, m.content, m.type, m.topic, m.created_at,
                   (SELECT vector FROM embeddings WHERE memory_id = m.id LIMIT 1) as vector
            FROM memories m
            WHERE m.content LIKE ? AND m.type = ?
            ORDER BY m.created_at DESC
            LIMIT 100
        """, (like_pattern, memory_type))
    else:
        cursor.execute("""
            SELECT m.id, m.content, m.type, m.topic, m.created_at,
                   (SELECT vector FROM embeddings WHERE memory_id = m.id LIMIT 1) as vector
            FROM memories m
            WHERE m.content LIKE ?
            ORDER BY m.created_at DESC
            LIMIT 100
        """, (like_pattern,))
    
    candidates = cursor.fetchall()
    
    if not candidates:
        return []
    
    # 获取查询向量
    try:
        query_vector = get_embedding(query)
    except Exception as e:
        print(f"Warning: Failed to get query embedding: {e}")
        # 降级：返回 LIKE 结果
        return [{
            "id": row[0], "content": row[1], "type": row[2],
            "topic": row[3], "created_at": row[4], "score": 0.0
        } for row in candidates[:top_k]]
    
    # 计算余弦相似度
    results = []
    for row in candidates:
        memory_id, content, memory_type, topic, created_at, vector_json = row
        if not vector_json:
            continue
        try:
            vector = json.loads(vector_json)
            score = cosine_similarity(query_vector, vector)
            results.append({
                "id": memory_id,
                "content": content,
                "type": memory_type,
                "topic": topic,
                "created_at": created_at,
                "score": score
            })
        except Exception:
            continue
    
    # 排序返回 top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def get_memory_by_id(conn: sqlite3.Connection, memory_id: int) -> dict:
    """获取单条记忆"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, type, topic, created_at, updated_at FROM memories WHERE id = ?", (memory_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return {"id": row[0], "content": row[1], "type": row[2], "topic": row[3], "created_at": row[4], "updated_at": row[5]}


def delete_memory(conn: sqlite3.Connection, memory_id: int):
    """删除记忆"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM embeddings WHERE memory_id = ?", (memory_id,))
    cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    # FTS 中删除需要通过 content_rowid
    cursor.execute("DELETE FROM memories_fts WHERE rowid = ?", (memory_id,))
    conn.commit()


def count_memories(conn: sqlite3.Connection) -> int:
    """统计记忆数量"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM memories")
    return cursor.fetchone()[0]


if __name__ == "__main__":
    # 测试
    conn = init_db()
    print(f"Database initialized. Total memories: {count_memories(conn)}")
    
    # 测试添加
    test_id = add_memory(conn, "这是一个测试记忆，用于验证向量搜索系统", "test", "系统验证")
    print(f"Added memory with id: {test_id}")
    
    # 测试搜索
    results = search_memories(conn, "验证向量搜索")
    print(f"Search results: {len(results)} found")
    for r in results:
        print(f"  - [{r['type']}] {r['content'][:50]}... (score: {r['score']:.4f})")
    
    # 清理测试数据
    delete_memory(conn, test_id)
    conn.close()
    print("Test complete.")
