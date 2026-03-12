import enum
from sqlalchemy import Boolean, Column, Enum, Float, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base


class MuscleGroup(str, enum.Enum):
    chest = "chest"
    back = "back"
    shoulders = "shoulders"
    biceps = "biceps"
    triceps = "triceps"
    quadriceps = "quadriceps"
    hamstrings = "hamstrings"
    glutes = "glutes"
    calves = "calves"
    abs = "abs"
    forearms = "forearms"
    traps = "traps"


class ExerciseType(str, enum.Enum):
    compound = "compound"
    isolation = "isolation"


class Equipment(str, enum.Enum):
    barbell = "barbell"
    dumbbell = "dumbbell"
    machine = "machine"
    cable = "cable"
    bodyweight = "bodyweight"
    kettlebell = "kettlebell"
    other = "other"


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=True)
    muscle_group = Column(Enum(MuscleGroup), nullable=False)
    secondary_muscles = Column(ARRAY(String), default=[])
    exercise_type = Column(Enum(ExerciseType), nullable=False)
    effectiveness_coefficient = Column(Float, default=0.5)
    equipment = Column(Enum(Equipment), default=Equipment.barbell)
    is_custom = Column(Boolean, default=False)
