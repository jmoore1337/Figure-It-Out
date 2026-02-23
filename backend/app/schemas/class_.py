from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClassCreate(BaseModel):
    name: str


class ClassOut(BaseModel):
    id: int
    name: str
    join_code: str
    teacher_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
