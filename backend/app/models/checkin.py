from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="CASCADE"), unique=True, nullable=False)
    sleep_quality = Column(Integer, nullable=False)  # 1-5
    emotional_state = Column(Integer, nullable=False)  # 1-5
    had_breakfast = Column(Boolean, default=False)
    had_coffee = Column(Boolean, default=False)
    notes = Column(String, nullable=True)

    workout = relationship("Workout", back_populates="checkin")
    user = relationship("User", back_populates="checkins")
