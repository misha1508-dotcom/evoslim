from sqlalchemy import Column, DateTime, Float, Integer, String, func, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class InBodyScan(Base):
    __tablename__ = "inbody_scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    image_path = Column(String, nullable=True)
    raw_json = Column(JSONB, nullable=True)

    # Body Composition
    weight_kg = Column(Float, nullable=True)
    skeletal_muscle_mass_kg = Column(Float, nullable=True)
    body_fat_mass_kg = Column(Float, nullable=True)
    total_body_water_l = Column(Float, nullable=True)
    protein_kg = Column(Float, nullable=True)
    minerals_kg = Column(Float, nullable=True)

    # Obesity Analysis
    bmi = Column(Float, nullable=True)
    body_fat_percent = Column(Float, nullable=True)

    # Research Parameters
    basal_metabolic_rate_kcal = Column(Integer, nullable=True)
    visceral_fat_level = Column(Integer, nullable=True)
    waist_hip_ratio = Column(Float, nullable=True)
    fat_free_mass_kg = Column(Float, nullable=True)
    obesity_degree_percent = Column(Float, nullable=True)
    inbody_score = Column(Integer, nullable=True)
    ideal_weight_kg = Column(Float, nullable=True)

    # Segmental Lean Mass
    lean_mass_left_arm_kg = Column(Float, nullable=True)
    lean_mass_right_arm_kg = Column(Float, nullable=True)
    lean_mass_trunk_kg = Column(Float, nullable=True)
    lean_mass_left_leg_kg = Column(Float, nullable=True)
    lean_mass_right_leg_kg = Column(Float, nullable=True)

    # Segmental Fat Mass
    fat_mass_left_arm_kg = Column(Float, nullable=True)
    fat_mass_right_arm_kg = Column(Float, nullable=True)
    fat_mass_trunk_kg = Column(Float, nullable=True)
    fat_mass_left_leg_kg = Column(Float, nullable=True)
    fat_mass_right_leg_kg = Column(Float, nullable=True)

    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="inbody_records")
