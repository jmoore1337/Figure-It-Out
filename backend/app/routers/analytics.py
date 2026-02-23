from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import Counter
from typing import Optional

from app.database import get_db
from app.models.class_ import Class
from app.models.assignment import Assignment
from app.models.teacher import TeacherUser
from app.models.session import TutorSession
from app.models.student import StudentAnon
from app.models.learning_event import LearningEvent
from app.schemas.analytics import AnalyticsOut, QuestionCluster
from app.routers.auth import get_current_teacher
from app.services.analytics import get_question_clusters

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/classes/{class_id}/assignments/{assignment_id}", response_model=AnalyticsOut)
async def get_assignment_analytics(
    class_id: int,
    assignment_id: int,
    teacher: TeacherUser = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    result = await db.execute(
        select(Class).where(Class.id == class_id, Class.teacher_id == teacher.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Class not found")

    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.class_id == class_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Get sessions for this assignment
    result = await db.execute(
        select(TutorSession).where(TutorSession.assignment_id == assignment_id)
    )
    sessions = result.scalars().all()
    session_ids = [s.id for s in sessions]
    session_count = len(sessions)

    # Active student count
    student_ids = list({s.student_id for s in sessions})
    active_student_count = len(student_ids)

    if not session_ids:
        return AnalyticsOut(
            session_count=0,
            active_student_count=0,
            avg_hint_level=0.0,
            top_intent_types={},
            top_question_clusters=[],
            most_common_stuck_step=None,
            policy_violations_prevented=0,
        )

    # Get learning events
    result = await db.execute(
        select(LearningEvent).where(LearningEvent.session_id.in_(session_ids))
    )
    events = result.scalars().all()

    avg_hint_level = (
        sum(e.hint_level_served for e in events) / len(events) if events else 0.0
    )

    intent_counter = Counter(e.intent for e in events)
    top_intent_types = dict(intent_counter.most_common(5))

    stuck_step_counter = Counter(e.stuck_step for e in events)
    most_common_stuck_step = stuck_step_counter.most_common(1)[0][0] if stuck_step_counter else None

    policy_violations = sum(1 for e in events if e.policy_violation_prevented)

    student_messages = [e.student_message for e in events if e.student_message]
    clusters_raw = get_question_clusters(student_messages)
    clusters = [QuestionCluster(keyword=c["keyword"], count=c["count"]) for c in clusters_raw]

    return AnalyticsOut(
        session_count=session_count,
        active_student_count=active_student_count,
        avg_hint_level=round(avg_hint_level, 2),
        top_intent_types=top_intent_types,
        top_question_clusters=clusters,
        most_common_stuck_step=most_common_stuck_step,
        policy_violations_prevented=policy_violations,
    )
