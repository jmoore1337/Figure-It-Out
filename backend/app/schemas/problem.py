from pydantic import BaseModel
from datetime import datetime
from typing import List


class ProblemCreate(BaseModel):
    problem_text: str
    skill_tags: List[str] = []
    order_index: int = 0


class ProblemOut(BaseModel):
    id: int
    assignment_id: int
    problem_text: str
    skill_tags: list
    order_index: int
    created_at: datetime

    model_config = {"from_attributes": True}
