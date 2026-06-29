import random, os
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, SessionLocal, Base
from models import Question
from schemas import QuestionCreate, QuestionUpdate, QuestionOut, QuestionListOut, StatsOut, CategoryStat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="面试题管理系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/questions", response_model=QuestionOut)
def create_question(q: QuestionCreate, db: Session = Depends(get_db)):
    data = q.model_dump()
    if not data.get("domain") and data.get("category"):
        data["domain"] = data["category"].split("-")[0] if "-" in data["category"] else ""
    question = Question(**data)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@app.put("/api/questions/{qid}", response_model=QuestionOut)
def update_question(qid: int, q: QuestionUpdate, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == qid).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    for key, val in q.model_dump(exclude_unset=True).items():
        setattr(question, key, val)
    db.commit()
    db.refresh(question)
    return question


@app.delete("/api/questions/{qid}")
def delete_question(qid: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == qid).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.delete(question)
    db.commit()
    return {"ok": True}


@app.get("/api/questions", response_model=QuestionListOut)
def list_questions(
    keyword: str = Query(default=""),
    domain: str = Query(default=""),
    category: str = Query(default=""),
    level: str = Query(default=""),
    status: str = Query(default=""),
    favorite: bool = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Question)
    if keyword:
        q = q.filter(Question.title.contains(keyword) | Question.answer.contains(keyword))
    if domain:
        q = q.filter(Question.domain == domain)
    if category:
        q = q.filter(Question.category == category)
    if level:
        q = q.filter(Question.level == level)
    if status:
        q = q.filter(Question.status == status)
    if favorite is not None:
        q = q.filter(Question.favorite == favorite)

    total = q.count()
    items = q.order_by(Question.domain, Question.category, Question.id).offset((page - 1) * page_size).limit(page_size).all()
    return QuestionListOut(total=total, items=items)


@app.get("/api/questions/{qid}", response_model=QuestionOut)
def get_question(qid: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == qid).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question


@app.get("/api/study")
def study_questions(
    domain: str = Query(default=""),
    category: str = Query(default=""),
    level: str = Query(default=""),
    status: str = Query(default=""),
    favorite: bool = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """随机抽取题目用于背诵，status 支持逗号分隔多值"""
    q = db.query(Question)
    if domain:
        q = q.filter(Question.domain == domain)
    if category:
        q = q.filter(Question.category == category)
    if level:
        q = q.filter(Question.level == level)
    if status:
        statuses = [s.strip() for s in status.split(",") if s.strip()]
        if len(statuses) == 1:
            q = q.filter(Question.status == statuses[0])
        else:
            q = q.filter(Question.status.in_(statuses))
    if favorite is not None:
        q = q.filter(Question.favorite == favorite)

    all_ids = [row[0] for row in q.with_entities(Question.id).all()]
    if not all_ids:
        return []
    sample_ids = random.sample(all_ids, min(limit, len(all_ids)))
    questions = db.query(Question).filter(Question.id.in_(sample_ids)).all()
    return [QuestionOut.model_validate(q) for q in questions]


@app.get("/api/filters")
def get_filters(db: Session = Depends(get_db)):
    domains = [row[0] for row in db.query(Question.domain).distinct().order_by(Question.domain).all() if row[0]]
    cats_by_domain = {}
    for d in domains:
        cats = [row[0] for row in db.query(Question.category).filter(Question.domain == d).distinct().order_by(Question.category).all()]
        cats_by_domain[d] = cats
    levels = [row[0] for row in db.query(Question.level).distinct().all()]
    statuses = ["未掌握", "需复习", "已掌握"]
    return {"domains": domains, "categories": cats_by_domain, "levels": levels, "statuses": statuses}


@app.get("/api/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Question).count()
    mastered = db.query(Question).filter(Question.status == "已掌握").count()
    need_review = db.query(Question).filter(Question.status == "需复习").count()
    unmastered = db.query(Question).filter(Question.status == "未掌握").count()

    cats = (
        db.query(Question.category, func.count(Question.id))
        .group_by(Question.category)
        .all()
    )
    by_category = []
    for c, cnt in cats:
        m = db.query(Question).filter(Question.category == c, Question.status == "已掌握").count()
        by_category.append(CategoryStat(category=c, total=cnt, mastered=m))

    return StatsOut(
        total=total,
        mastered=mastered,
        need_review=need_review,
        unmastered=unmastered,
        by_category=by_category,
    )


@app.get("/api/export")
def export_questions(
    domain: str = Query(default=""),
    category: str = Query(default=""),
    level: str = Query(default=""),
    status: str = Query(default=""),
    favorite: bool = Query(default=None),
    db: Session = Depends(get_db),
):
    """导出题目为 JSON"""
    q = db.query(Question)
    if domain:
        q = q.filter(Question.domain == domain)
    if category:
        q = q.filter(Question.category == category)
    if level:
        q = q.filter(Question.level == level)
    if status:
        statuses = [s.strip() for s in status.split(",") if s.strip()]
        q = q.filter(Question.status.in_(statuses))
    if favorite is not None:
        q = q.filter(Question.favorite == favorite)

    items = [QuestionOut.model_validate(x).model_dump(mode="json") for x in q.all()]
    return {"version": 1, "count": len(items), "items": items}


@app.get("/api/export/md")
def export_questions_md(
    domain: str = Query(default=""),
    category: str = Query(default=""),
    level: str = Query(default=""),
    status: str = Query(default=""),
    favorite: bool = Query(default=None),
    db: Session = Depends(get_db),
):
    """导出题目为 Markdown"""
    from fastapi.responses import PlainTextResponse
    q = db.query(Question)
    if domain:
        q = q.filter(Question.domain == domain)
    if category:
        q = q.filter(Question.category == category)
    if level:
        q = q.filter(Question.level == level)
    if status:
        statuses = [s.strip() for s in status.split(",") if s.strip()]
        q = q.filter(Question.status.in_(statuses))
    if favorite is not None:
        q = q.filter(Question.favorite == favorite)

    items = q.order_by(Question.domain, Question.category, Question.id).all()
    lines = []
    cur_cat = None
    for item in items:
        if item.category != cur_cat:
            cur_cat = item.category
            lines.append(f"\n# {cur_cat}\n")
        status_map = {"已掌握": "✅", "需复习": "🟡", "未掌握": "❌"}
        star = "⭐" if item.favorite else ""
        lines.append(f"## {item.title}  {star}{status_map.get(item.status, '')}")
        lines.append(f"\n**难度**: {item.level}\n")
        lines.append(f"{item.answer}\n")
        lines.append("---\n")

    content = "\n".join(lines)
    return PlainTextResponse(content, media_type="text/markdown; charset=utf-8")


@app.post("/api/import")
def import_questions(data: dict, db: Session = Depends(get_db)):
    """导入题目 JSON，重复 title 跳过"""
    items = data.get("items", [])
    added, skipped = 0, 0
    for item in items:
        exist = db.query(Question).filter(Question.title == item.get("title")).first()
        if exist:
            skipped += 1
            continue
        cat = item.get("category", "未分类")
        dom = item.get("domain", "")
        if not dom and cat and "-" in cat:
            dom = cat.split("-")[0]
        q = Question(
            title=item.get("title", ""),
            answer=item.get("answer", ""),
            domain=dom,
            category=cat,
            level=item.get("level", "重点"),
            status=item.get("status", "未掌握"),
            favorite=item.get("favorite", False),
        )
        db.add(q)
        added += 1
    db.commit()
    return {"ok": True, "added": added, "skipped": skipped}


@app.get("/api/knowledge")
def get_knowledge():
    """返回知识巩固 JSON 数据"""
    import json, os
    path = os.path.join(os.path.dirname(__file__), "data", "knowledge_structured.json")
    if not os.path.exists(path):
        return {"concepts": [], "flowcharts": [], "mindmaps": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# === 静态文件服务（前端打包后的 dist 目录）===
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    @app.get("/")
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str = ""):
        """SPA 回退：非 API 路径返回 index.html"""
        file_path = os.path.join(frontend_dist, full_path) if full_path else ""
        if file_path and os.path.isfile(file_path) and not full_path.startswith("api"):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
