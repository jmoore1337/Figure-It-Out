from pydantic import BaseModel
from typing import Optional


class TeacherLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TeacherMe(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}
