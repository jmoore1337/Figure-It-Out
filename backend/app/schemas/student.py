from pydantic import BaseModel
from datetime import datetime


class StudentJoin(BaseModel):
    classCode: str
    studentAnonId: str


class StudentOut(BaseModel):
    id: int
    anon_id: str
    class_id: int
    joined_at: datetime

    model_config = {"from_attributes": True}
