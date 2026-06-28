# 批量导入题目模板
# 使用方法：复制此文件 → 修改 questions 里的题目数据 → 运行 python 此文件
# 每个 batch 建议不超过 15 题，超过分多个文件
#
# 关键规则（避免编码问题）：
#   1. 字符串用英文双引号 """"""（三引号）
#   2. 答案中的引号用中文全角「」代替半角 ""
#   3. 每个答案末尾都要有关键记忆点

import sqlite3
from datetime import datetime

# === 修改这里：数据库路径 ===
DB_PATH = "D:/myproject/MianShi/backend/mianshi.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

items = []

def add(domain, category, title, level, answer):
    """添加一道题。
    domain:   领域，如 Prompt, LM, RAG, 工程, MM, Agent, Python 等
    category: 子分类，格式如 Prompt-C1 基础原理
    title:    题目标题，格式如 Prompt Q1.1 xxx
    level:    难度：必会 / 重点 / 了解
    answer:   答案文本，首行不缩进，段落间用 \n\n 分隔
    """
    items.append((title, answer, domain, category, level, "未掌握", now, now, False))

# ============================================================
# === 在下面添加题目（可复制 add(...) 行修改） ===
# ============================================================

# --- 示例（取消注释并修改）---
# add("Python", "Python-C1 基础", "Python Q1.1 示例题目",
#     "必会",
#     "第一段写概述，引出问题的核心价值。\n\n"
#     "第二段展开讲细节，用「第一」「第二」串联逻辑。可以配合具体例子帮助理解。\n\n"
#     "后面段落继续深入。关键术语首次出现时在括号里简要释义，比如 RoPE（旋转位置编码，让模型学习相对位置关系）。\n\n"
#     "最后一段是记忆点总结。\n\n"
#     "关键记忆点：几个关键词 = 一句话总结。记住最核心的要点。")

# ============================================================
# === 写入数据库（不要修改下面） ===
# ============================================================

for item in items:
    cur.execute(
        "INSERT INTO questions (title,answer,domain,category,level,status,created_at,updated_at,favorite) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        item
    )

conn.commit()
c = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
print(f"新增 {len(items)} 题，数据库共 {c} 题")
conn.close()
