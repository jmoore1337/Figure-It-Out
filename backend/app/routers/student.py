from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.class_ import Class
from app.models.assignment import Assignment
from app.models.student import StudentAnon
from app.schemas.student import StudentJoin, StudentOut
from app.schemas.assignment import AssignmentOut

router = APIRouter(prefix="/student", tags=["student"])


@router.post("/join", response_model=StudentOut)
async def student_join(data: StudentJoin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Class).where(Class.join_code == data.classCode))
    class_ = result.scalar_one_or_none()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if student already joined
    result = await db.execute(
        select(StudentAnon).where(
            StudentAnon.anon_id == data.studentAnonId,
            StudentAnon.class_id == class_.id,
        )
    )
    student = result.scalar_one_or_none()

    if not student:
        student = StudentAnon(anon_id=data.studentAnonId, class_id=class_.id)
        db.add(student)
        await db.flush()
        await db.refresh(student)

    return student


@router.get("/classes/{class_code}/assignments", response_model=list[AssignmentOut])
async def get_student_assignments(class_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Class).where(Class.join_code == class_code))
    class_ = result.scalar_one_or_none()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")

    result = await db.execute(
        select(Assignment).where(Assignment.class_id == class_.id)
    )
    return result.scalars().all()
