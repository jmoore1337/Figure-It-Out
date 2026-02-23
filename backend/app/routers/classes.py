import random
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.class_ import Class
from app.models.assignment import Assignment
from app.models.problem import Problem
from app.models.teacher import TeacherUser
from app.schemas.class_ import ClassCreate, ClassOut
from app.schemas.assignment import AssignmentCreate, AssignmentOut
from app.schemas.problem import ProblemCreate, ProblemOut
from app.routers.auth import get_current_teacher

router = APIRouter(tags=["classes"])


def generate_join_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


@router.post("/classes", response_model=ClassOut)
async def create_class(
    data: ClassCreate,
    teacher: TeacherUser = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    join_code = generate_join_code()
    # Ensure uniqueness (max 10 attempts)
    for _ in range(10):
        result = await db.execute(select(Class).where(Class.join_code == join_code))
        if not result.scalar_one_or_none():
            break
        join_code = generate_join_code()
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique join code")

    class_ = Class(name=data.name, join_code=join_code, teacher_id=teacher.id)
    db.add(class_)
    await db.flush()
    await db.refresh(class_)
    return class_


@router.get("/classes", response_model=list[ClassOut])
async def list_classes(
    teacher: TeacherUser = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Class).where(Class.teacher_id == teacher.id))
    return result.scalars().all()


@router.post("/classes/{class_id}/assignments", response_model=AssignmentOut)
async def create_assignment(
    class_id: int,
    data: AssignmentCreate,
    teacher: TeacherUser = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Class).where(Class.id == class_id, Class.teacher_id == teacher.id)
    )
    class_ = result.scalar_one_or_none()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")

    assignment = Assignment(
        title=data.title,
        description=data.description,
        class_id=class_id,
        policy=data.policy.model_dump(),
    )
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment


@router.get("/classes/{class_id}/assignments", response_model=list[AssignmentOut])
async def list_assignments(
    class_id: int,
    teacher: TeacherUser = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Class).where(Class.id == class_id, Class.teacher_id == teacher.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Class not found")

    result = await db.execute(
        select(Assignment).where(Assignment.class_id == class_id)
    )
    return result.scalars().all()


@router.post("/assignments/{assignment_id}/problems", response_model=ProblemOut)
async def create_problem(
    assignment_id: int,
    data: ProblemCreate,
    teacher: TeacherUser = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assignment)
        .join(Class)
        .where(Assignment.id == assignment_id, Class.teacher_id == teacher.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Assignment not found")

    problem = Problem(
        assignment_id=assignment_id,
        problem_text=data.problem_text,
        skill_tags=data.skill_tags,
        order_index=data.order_index,
    )
    db.add(problem)
    await db.flush()
    await db.refresh(problem)
    return problem


@router.get("/assignments/{assignment_id}/problems", response_model=list[ProblemOut])
async def list_problems(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint to get problems for an assignment (used by both teachers and students)."""
    result = await db.execute(
        select(Assignment).where(Assignment.id == assignment_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Assignment not found")

    result = await db.execute(
        select(Problem).where(Problem.assignment_id == assignment_id).order_by(Problem.order_index)
    )
    return result.scalars().all()
