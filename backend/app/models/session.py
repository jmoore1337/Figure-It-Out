from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class TutorSession(Base):
    __tablename__ = "tutor_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_anons.id"))
    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("assignments.id"))
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey("problems.id"))
    started_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_activity: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student: Mapped["StudentAnon"] = relationship("StudentAnon", back_populates="sessions")
    messages: Mapped[list["TutorMessage"]] = relationship("TutorMessage", back_populates="session")
    learning_events: Mapped[list["LearningEvent"]] = relationship("LearningEvent", back_populates="session")


class TutorMessage(Base):
    __tablename__ = "tutor_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("tutor_sessions.id"))
    role: Mapped[str] = mapped_column(String(20))  # "student" or "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["TutorSession"] = relationship("TutorSession", back_populates="messages")
