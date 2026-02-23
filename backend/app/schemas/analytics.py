from pydantic import BaseModel
from typing import List, Dict, Optional


class QuestionCluster(BaseModel):
    keyword: str
    count: int


class AnalyticsOut(BaseModel):
    session_count: int
    active_student_count: int
    avg_hint_level: float
    top_intent_types: Dict[str, int]
    top_question_clusters: List[QuestionCluster]
    most_common_stuck_step: Optional[int]
    policy_violations_prevented: int
