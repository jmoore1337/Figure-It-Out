from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class AssignmentPolicy(BaseModel):
    answer_mode: Literal["NO_ANSWER", "ALLOW_AFTER_MASTERY", "ALLOW"] = "NO_ANSWER"
    hint_ceiling: int = 3
    attempt_required: bool = True
    show_similar_example: bool = False


class AssignmentCreate(BaseModel):
    title: str
    description: str = ""
    policy: AssignmentPolicy = AssignmentPolicy()


class AssignmentOut(BaseModel):
    id: int
    title: str
    description: str
    class_id: int
    policy: dict
    created_at: datetime

    model_config = {"from_attributes": True}
