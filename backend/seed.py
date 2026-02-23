"""Seed script to create demo data."""
import asyncio
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import Base
from app.models.teacher import TeacherUser
from app.models.class_ import Class
from app.models.assignment import Assignment
from app.models.problem import Problem
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEMO_EMAIL = "teacher@demo.com"
DEMO_PASSWORD = "admin123"


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        from sqlalchemy import select

        # Check if already seeded
        result = await db.execute(select(TeacherUser).where(TeacherUser.email == DEMO_EMAIL))
        if result.scalar_one_or_none():
            print("Already seeded.")
            return

        # Create demo teacher
        teacher = TeacherUser(
            email=DEMO_EMAIL,
            hashed_password=pwd_context.hash(DEMO_PASSWORD),
        )
        db.add(teacher)
        await db.flush()

        # Create demo class
        class_ = Class(
            name="Algebra 1 - Period 3",
            join_code="DEMO01",
            teacher_id=teacher.id,
        )
        db.add(class_)
        await db.flush()

        # Create demo assignment
        policy = {
            "answer_mode": "NO_ANSWER",
            "hint_ceiling": 3,
            "attempt_required": True,
            "show_similar_example": False,
        }
        assignment = Assignment(
            title="Solving Linear Equations",
            description="Practice solving for x in linear equations",
            class_id=class_.id,
            policy=policy,
        )
        db.add(assignment)
        await db.flush()

        # Create demo problems
        problems = [
            Problem(
                assignment_id=assignment.id,
                problem_text="Solve for x: 2x + 5 = 13",
                skill_tags=["linear-equations", "algebra", "inverse-operations"],
                order_index=0,
            ),
            Problem(
                assignment_id=assignment.id,
                problem_text="Solve for x: 3x - 7 = 2x + 4",
                skill_tags=["linear-equations", "algebra", "combining-like-terms"],
                order_index=1,
            ),
        ]
        for p in problems:
            db.add(p)

        await db.commit()
        print("Seed complete!")
        print(f"  Teacher: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"  Class join code: DEMO01")
        print(f"  Assignment: Solving Linear Equations")
        print(f"  Problems: 2")


if __name__ == "__main__":
    asyncio.run(seed())
