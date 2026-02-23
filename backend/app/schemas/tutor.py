from pydantic import BaseModel
from typing import List, Optional, Literal


class ConversationMessage(BaseModel):
    role: Literal["student", "assistant"]
    content: str


class TutorRequest(BaseModel):
    studentAnonId: str
    classCode: str
    assignmentId: int
    problemId: int
    conversationHistory: List[ConversationMessage] = []
    studentMessage: str


class TutorTelemetry(BaseModel):
    intent: Literal["ask_for_hint", "ask_for_answer", "ask_for_check", "concept_question", "other"] = "other"
    skill_tags: List[str] = []
    stuck_step: int = 1
    hint_level_served: int = 0
    misconception_code: Optional[str] = None
    policy_violation_prevented: bool = False


class TutorResponse(BaseModel):
    student_message: str
    check_question: str
    next_action: str
    telemetry: TutorTelemetry
