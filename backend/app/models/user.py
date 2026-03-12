from sqlalchemy import BigInteger, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    genetic_context = Column(Text, nullable=True)
    allergies_and_risks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_measurements_request = Column(DateTime(timezone=True), nullable=True)

    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    medical_history = relationship("MedicalHistory", back_populates="user", cascade="all, delete-orphan")
    checkins = relationship("CheckIn", back_populates="user", cascade="all, delete-orphan")
    measurements = relationship("BodyMeasurement", back_populates="user", cascade="all, delete-orphan")
    inbody_records = relationship("InBodyScan", back_populates="user", cascade="all, delete-orphan")
