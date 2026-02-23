from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.database import get_db
from app.models.teacher import TeacherUser
from app.schemas.auth import TeacherLogin, Token, TeacherMe
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_teacher(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> TeacherUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        teacher_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(TeacherUser).where(TeacherUser.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=401, detail="Teacher not found")
    return teacher


@router.post("/teacher/login", response_model=Token)
async def teacher_login(data: TeacherLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeacherUser).where(TeacherUser.email == data.email))
    teacher = result.scalar_one_or_none()

    if not teacher:
        if data.password == settings.TEACHER_ADMIN_PASSWORD:
            hashed = pwd_context.hash(data.password)
            teacher = TeacherUser(email=data.email, hashed_password=hashed)
            db.add(teacher)
            await db.flush()
            await db.refresh(teacher)
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        if not pwd_context.verify(data.password, teacher.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(teacher.id), "email": teacher.email})
    return Token(access_token=token)


@router.get("/me", response_model=TeacherMe)
async def get_me(teacher: TeacherUser = Depends(get_current_teacher)):
    return TeacherMe(id=teacher.id, email=teacher.email)
