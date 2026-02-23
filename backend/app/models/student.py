from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class StudentAnon(Base):
    __tablename__ = "student_anons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    anon_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"))
    joined_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    class_: Mapped["Class"] = relationship("Class")
    sessions: Mapped[list["TutorSession"]] = relationship("TutorSession", back_populates="student")
