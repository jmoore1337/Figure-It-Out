from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


class LearningEvent(Base):
    __tablename__ = "learning_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("tutor_sessions.id"))
    intent: Mapped[str] = mapped_column(String(50), default="other")
    hint_level_served: Mapped[int] = mapped_column(Integer, default=0)
    stuck_step: Mapped[int] = mapped_column(Integer, default=1)
    misconception_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    policy_violation_prevented: Mapped[bool] = mapped_column(Boolean, default=False)
    student_message: Mapped[str] = mapped_column(String(2000), default="")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["TutorSession"] = relationship("TutorSession", back_populates="learning_events")
