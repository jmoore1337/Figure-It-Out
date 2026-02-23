from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    join_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teacher_users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teacher: Mapped["TeacherUser"] = relationship("TeacherUser", back_populates="classes")
    assignments: Mapped[list["Assignment"]] = relationship("Assignment", back_populates="class_")
