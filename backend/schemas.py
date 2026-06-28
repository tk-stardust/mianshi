from datetime import datetime
from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    title: str
    answer: str
    domain: str = ""
    category: str = "未分类"
    level: str = "重点"


class QuestionUpdate(BaseModel):
    title: str | None = None
    answer: str | None = None
    domain: str | None = None
    category: str | None = None
    level: str | None = None
    status: str | None = None
    favorite: bool | None = None


class QuestionOut(BaseModel):
    id: int
    title: str
    answer: str
    domain: str = ""
    category: str
    level: str
    status: str
    favorite: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionListOut(BaseModel):
    total: int
    items: list[QuestionOut]


class CategoryStat(BaseModel):
    category: str
    total: int
    mastered: int

    model_config = {"from_attributes": True}


class StatsOut(BaseModel):
    total: int
    mastered: int
    need_review: int
    unmastered: int
    by_category: list[CategoryStat]
