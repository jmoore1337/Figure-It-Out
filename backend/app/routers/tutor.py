import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.class_ import Class
from app.models.assignment import Assignment
from app.models.problem import Problem
from app.models.student import StudentAnon
from app.models.session import TutorSession, TutorMessage
from app.models.learning_event import LearningEvent
from app.schemas.tutor import TutorRequest, TutorResponse, TutorTelemetry
from app.llm.provider import get_provider
from app.prompts.tutor_system import get_system_prompt
from app.services.leakage import check_leakage, rewrite_to_safe_hint

router = APIRouter(prefix="/tutor", tags=["tutor"])


def parse_llm_response(raw: str) -> dict:
    """Parse LLM response JSON, with fallback."""
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1]) if len(lines) > 2 else raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "student_message": raw,
            "check_question": "Does that help?",
            "next_action": "hint",
            "telemetry": {
                "intent": "other",
                "skill_tags": [],
                "stuck_step": 1,
                "hint_level_served": 0,
                "misconception_code": None,
                "policy_violation_prevented": False,
            },
        }


@router.post("/next", response_model=TutorResponse)
async def tutor_next(data: TutorRequest, db: AsyncSession = Depends(get_db)):
    # Validate class
    result = await db.execute(select(Class).where(Class.join_code == data.classCode))
    class_ = result.scalar_one_or_none()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")

    # Validate assignment
    result = await db.execute(
        select(Assignment).where(
            Assignment.id == data.assignmentId,
            Assignment.class_id == class_.id,
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Validate problem
    result = await db.execute(
        select(Problem).where(
            Problem.id == data.problemId,
            Problem.assignment_id == assignment.id,
        )
    )
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Get or create student
    result = await db.execute(
        select(StudentAnon).where(StudentAnon.anon_id == data.studentAnonId)
    )
    student = result.scalar_one_or_none()
    if not student:
        student = StudentAnon(anon_id=data.studentAnonId, class_id=class_.id)
        db.add(student)
        await db.flush()
        await db.refresh(student)

    # Get or create session
    result = await db.execute(
        select(TutorSession).where(
            TutorSession.student_id == student.id,
            TutorSession.problem_id == problem.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        session = TutorSession(
            student_id=student.id,
            assignment_id=assignment.id,
            problem_id=problem.id,
        )
        db.add(session)
        await db.flush()
        await db.refresh(session)

    # Determine current hint level from conversation
    hint_level = sum(
        1 for m in data.conversationHistory if m.role == "assistant"
    )
    policy = assignment.policy or {}
    hint_ceiling = policy.get("hint_ceiling", 3)
    hint_level = min(hint_level, hint_ceiling)

    # Build messages for LLM
    system_prompt = get_system_prompt(problem.problem_text, policy, hint_level)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in data.conversationHistory:
        role = "user" if msg.role == "student" else "assistant"
        messages.append({"role": role, "content": msg.content})
    messages.append({"role": "user", "content": data.studentMessage})

    # Generate response
    provider = get_provider()
    raw_response = await provider.generate(messages)
    parsed = parse_llm_response(raw_response)

    # Leakage check
    answer_mode = policy.get("answer_mode", "NO_ANSWER")
    if answer_mode == "NO_ANSWER":
        student_msg_text = parsed.get("student_message", "")
        if check_leakage(student_msg_text):
            original_telemetry = parsed.get("telemetry", {})
            parsed = rewrite_to_safe_hint(original_telemetry)

    # Store messages
    db_message = TutorMessage(
        session_id=session.id,
        role="student",
        content=data.studentMessage,
    )
    db.add(db_message)

    assistant_msg = TutorMessage(
        session_id=session.id,
        role="assistant",
        content=parsed.get("student_message", ""),
    )
    db.add(assistant_msg)

    # Store learning event
    telemetry_data = parsed.get("telemetry", {})
    event = LearningEvent(
        session_id=session.id,
        intent=telemetry_data.get("intent", "other"),
        hint_level_served=telemetry_data.get("hint_level_served", 0),
        stuck_step=telemetry_data.get("stuck_step", 1),
        misconception_code=telemetry_data.get("misconception_code"),
        policy_violation_prevented=telemetry_data.get("policy_violation_prevented", False),
        student_message=data.studentMessage,
    )
    db.add(event)

    telemetry = TutorTelemetry(
        intent=telemetry_data.get("intent", "other"),
        skill_tags=telemetry_data.get("skill_tags", []),
        stuck_step=telemetry_data.get("stuck_step", 1),
        hint_level_served=telemetry_data.get("hint_level_served", 0),
        misconception_code=telemetry_data.get("misconception_code"),
        policy_violation_prevented=telemetry_data.get("policy_violation_prevented", False),
    )

    return TutorResponse(
        student_message=parsed.get("student_message", ""),
        check_question=parsed.get("check_question", ""),
        next_action=parsed.get("next_action", "hint"),
        telemetry=telemetry,
    )
