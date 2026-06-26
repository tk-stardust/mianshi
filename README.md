# 面试题管理系统

个人使用的大模型/AI 面试准备工具，集成题库管理、背诵模式、知识巩固三大功能。

## 快速启动

### 一键启动（Windows）

双击 `启动.bat`，首次自动安装依赖并构建，之后直接启动。

### 手动启动

```bash
# 1. 安装后端依赖
cd backend
pip install -r requirements.txt

# 2. 构建前端（仅首次）
cd ../frontend
npm install
npm run build

# 3. 启动
cd ../backend
python main.py
```

打开 `http://localhost:8000`

> 后续只有改前端代码才需重新 `npm run build`，改后端代码重启 `python main.py` 即可。

## 功能模块

### 题库

- 增删改查面试题，每题包含题目、答案、分类、难度
- 支持按分类/难度/掌握度筛选、关键词搜索
- 分页浏览，批量标记掌握状态
- ⭐ 收藏重点题目
- 导出/导入（JSON / Markdown）

### 背诵模式

- 随机抽题，先看题目回忆 → 点开答案对照 → 标记掌握/需复习/未掌握
- 错题模式：一键只抽薄弱题
- 每日目标：进度条 + ⚙ 自定义目标数
- 支持按分类/难度/收藏筛选

### 统计

- 总题数、掌握/复习/未掌握数量
- 各分类掌握进度条

### 知识巩固

- 103 个 AI 核心概念卡片，六维展开（定义、原理、场景、对比、局限、面试问法）
- 19 个流程图（Mermaid 渲染，支持缩放）
- 17 个思维导图（Markmap 渲染，支持缩放）
- 按课件文档导航，一键跳转

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vite + Element Plus |
| 图表 | Mermaid（流程图）+ Markmap（思维导图） |
| 后端 | Python FastAPI |
| 数据库 | SQLite |

## 项目结构

```
├── backend/
│   ├── main.py              # API 入口
│   ├── models.py / schemas.py / database.py
│   ├── mianshi.db            # SQLite 数据库（自动创建）
│   └── data/
│       ├── knowledge_structured.json  # 知识巩固数据
│       └── 课件/                       # 课件原始文件
└── frontend/src/
    ├── App.vue
    ├── api.js
    └── components/
        ├── QuestionList.vue    # 题库
        ├── QuestionForm.vue    # 添加/编辑
        ├── StudyMode.vue       # 背诵模式
        ├── KnowledgeView.vue   # 知识巩固内容
        └── KnowledgeNav.vue    # 课件导航
```
