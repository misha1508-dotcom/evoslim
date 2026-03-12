from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from app.database import Base


class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_date = Column(DateTime(timezone=True), server_default=func.now())
    event_description = Column(String, nullable=False)
    ai_decision = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="medical_history")
