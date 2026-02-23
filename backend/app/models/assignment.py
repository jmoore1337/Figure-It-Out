from sqlalchemy import String, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


DEFAULT_POLICY = {
    "answer_mode": "NO_ANSWER",
    "hint_ceiling": 3,
    "attempt_required": True,
    "show_similar_example": False,
}


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000), default="")
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"))
    policy: Mapped[dict] = mapped_column(JSON, default=lambda: DEFAULT_POLICY)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    class_: Mapped["Class"] = relationship("Class", back_populates="assignments")
    problems: Mapped[list["Problem"]] = relationship("Problem", back_populates="assignment")
