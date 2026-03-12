"""Seed data: ~60 popular exercises with classification."""

EXERCISES = [
    # === CHEST ===
    {"name": "Жим штанги лёжа", "name_en": "Barbell Bench Press", "muscle_group": "chest", "secondary_muscles": ["triceps", "shoulders"], "exercise_type": "compound", "effectiveness_coefficient": 1.0, "equipment": "barbell"},
    {"name": "Жим гантелей лёжа", "name_en": "Dumbbell Bench Press", "muscle_group": "chest", "secondary_muscles": ["triceps", "shoulders"], "exercise_type": "compound", "effectiveness_coefficient": 0.9, "equipment": "dumbbell"},
    {"name": "Жим штанги на наклонной скамье", "name_en": "Incline Barbell Press", "muscle_group": "chest", "secondary_muscles": ["triceps", "shoulders"], "exercise_type": "compound", "effectiveness_coefficient": 0.9, "equipment": "barbell"},
    {"name": "Жим гантелей на наклонной скамье", "name_en": "Incline Dumbbell Press", "muscle_group": "chest", "secondary_muscles": ["triceps", "shoulders"], "exercise_type": "compound", "effectiveness_coefficient": 0.85, "equipment": "dumbbell"},
    {"name": "Разводка гантелей лёжа", "name_en": "Dumbbell Flyes", "muscle_group": "chest", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "dumbbell"},
    {"name": "Сведение рук в кроссовере", "name_en": "Cable Crossover", "muscle_group": "chest", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "cable"},
    {"name": "Отжимания на брусьях", "name_en": "Dips", "muscle_group": "chest", "secondary_muscles": ["triceps", "shoulders"], "exercise_type": "compound", "effectiveness_coefficient": 0.85, "equipment": "bodyweight"},

    # === BACK ===
    {"name": "Становая тяга", "name_en": "Deadlift", "muscle_group": "back", "secondary_muscles": ["hamstrings", "glutes", "traps", "forearms"], "exercise_type": "compound", "effectiveness_coefficient": 1.0, "equipment": "barbell"},
    {"name": "Подтягивания", "name_en": "Pull-ups", "muscle_group": "back", "secondary_muscles": ["biceps", "forearms"], "exercise_type": "compound", "effectiveness_coefficient": 0.9, "equipment": "bodyweight"},
    {"name": "Тяга штанги в наклоне", "name_en": "Barbell Row", "muscle_group": "back", "secondary_muscles": ["biceps", "forearms"], "exercise_type": "compound", "effectiveness_coefficient": 0.85, "equipment": "barbell"},
    {"name": "Тяга гантели в наклоне", "name_en": "Dumbbell Row", "muscle_group": "back", "secondary_muscles": ["biceps", "forearms"], "exercise_type": "compound", "effectiveness_coefficient": 0.8, "equipment": "dumbbell"},
    {"name": "Тяга верхнего блока", "name_en": "Lat Pulldown", "muscle_group": "back", "secondary_muscles": ["biceps"], "exercise_type": "compound", "effectiveness_coefficient": 0.75, "equipment": "cable"},
    {"name": "Тяга нижнего блока", "name_en": "Seated Cable Row", "muscle_group": "back", "secondary_muscles": ["biceps"], "exercise_type": "compound", "effectiveness_coefficient": 0.75, "equipment": "cable"},
    {"name": "Тяга Т-грифа", "name_en": "T-Bar Row", "muscle_group": "back", "secondary_muscles": ["biceps", "forearms"], "exercise_type": "compound", "effectiveness_coefficient": 0.85, "equipment": "barbell"},
    {"name": "Гиперэкстензия", "name_en": "Hyperextension", "muscle_group": "back", "secondary_muscles": ["glutes", "hamstrings"], "exercise_type": "isolation", "effectiveness_coefficient": 0.4, "equipment": "bodyweight"},

    # === SHOULDERS ===
    {"name": "Жим штанги стоя", "name_en": "Overhead Press", "muscle_group": "shoulders", "secondary_muscles": ["triceps", "traps"], "exercise_type": "compound", "effectiveness_coefficient": 0.9, "equipment": "barbell"},
    {"name": "Жим гантелей сидя", "name_en": "Seated Dumbbell Press", "muscle_group": "shoulders", "secondary_muscles": ["triceps"], "exercise_type": "compound", "effectiveness_coefficient": 0.85, "equipment": "dumbbell"},
    {"name": "Махи гантелями в стороны", "name_en": "Lateral Raises", "muscle_group": "shoulders", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "dumbbell"},
    {"name": "Махи гантелями перед собой", "name_en": "Front Raises", "muscle_group": "shoulders", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "dumbbell"},
    {"name": "Разведение гантелей в наклоне", "name_en": "Reverse Flyes", "muscle_group": "shoulders", "secondary_muscles": ["traps"], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "dumbbell"},
    {"name": "Тяга штанги к подбородку", "name_en": "Upright Row", "muscle_group": "shoulders", "secondary_muscles": ["traps", "biceps"], "exercise_type": "compound", "effectiveness_coefficient": 0.7, "equipment": "barbell"},

    # === BICEPS ===
    {"name": "Сгибание рук со штангой", "name_en": "Barbell Curl", "muscle_group": "biceps", "secondary_muscles": ["forearms"], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "barbell"},
    {"name": "Сгибание рук с гантелями", "name_en": "Dumbbell Curl", "muscle_group": "biceps", "secondary_muscles": ["forearms"], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "dumbbell"},
    {"name": "Молотки", "name_en": "Hammer Curl", "muscle_group": "biceps", "secondary_muscles": ["forearms"], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "dumbbell"},
    {"name": "Сгибание рук на скамье Скотта", "name_en": "Preacher Curl", "muscle_group": "biceps", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "barbell"},
    {"name": "Сгибание рук на нижнем блоке", "name_en": "Cable Curl", "muscle_group": "biceps", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "cable"},

    # === TRICEPS ===
    {"name": "Жим штанги узким хватом", "name_en": "Close-Grip Bench Press", "muscle_group": "triceps", "secondary_muscles": ["chest", "shoulders"], "exercise_type": "compound", "effectiveness_coefficient": 0.75, "equipment": "barbell"},
    {"name": "Французский жим", "name_en": "Skull Crushers", "muscle_group": "triceps", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "barbell"},
    {"name": "Разгибание рук на верхнем блоке", "name_en": "Tricep Pushdown", "muscle_group": "triceps", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "cable"},
    {"name": "Разгибание руки с гантелей из-за головы", "name_en": "Overhead Tricep Extension", "muscle_group": "triceps", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "dumbbell"},

    # === QUADRICEPS ===
    {"name": "Приседания со штангой", "name_en": "Barbell Squat", "muscle_group": "quadriceps", "secondary_muscles": ["glutes", "hamstrings", "abs"], "exercise_type": "compound", "effectiveness_coefficient": 1.0, "equipment": "barbell"},
    {"name": "Фронтальные приседания", "name_en": "Front Squat", "muscle_group": "quadriceps", "secondary_muscles": ["glutes", "abs"], "exercise_type": "compound", "effectiveness_coefficient": 0.95, "equipment": "barbell"},
    {"name": "Жим ногами", "name_en": "Leg Press", "muscle_group": "quadriceps", "secondary_muscles": ["glutes", "hamstrings"], "exercise_type": "compound", "effectiveness_coefficient": 0.8, "equipment": "machine"},
    {"name": "Разгибание ног в тренажёре", "name_en": "Leg Extension", "muscle_group": "quadriceps", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "machine"},
    {"name": "Выпады с гантелями", "name_en": "Dumbbell Lunges", "muscle_group": "quadriceps", "secondary_muscles": ["glutes", "hamstrings"], "exercise_type": "compound", "effectiveness_coefficient": 0.8, "equipment": "dumbbell"},
    {"name": "Болгарские сплит-приседания", "name_en": "Bulgarian Split Squat", "muscle_group": "quadriceps", "secondary_muscles": ["glutes", "hamstrings"], "exercise_type": "compound", "effectiveness_coefficient": 0.8, "equipment": "dumbbell"},
    {"name": "Гакк-приседания", "name_en": "Hack Squat", "muscle_group": "quadriceps", "secondary_muscles": ["glutes"], "exercise_type": "compound", "effectiveness_coefficient": 0.8, "equipment": "machine"},

    # === HAMSTRINGS ===
    {"name": "Румынская тяга", "name_en": "Romanian Deadlift", "muscle_group": "hamstrings", "secondary_muscles": ["glutes", "back"], "exercise_type": "compound", "effectiveness_coefficient": 0.9, "equipment": "barbell"},
    {"name": "Сгибание ног в тренажёре лёжа", "name_en": "Lying Leg Curl", "muscle_group": "hamstrings", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "machine"},
    {"name": "Сгибание ног в тренажёре сидя", "name_en": "Seated Leg Curl", "muscle_group": "hamstrings", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "machine"},
    {"name": "Мёртвая тяга на прямых ногах", "name_en": "Stiff-Leg Deadlift", "muscle_group": "hamstrings", "secondary_muscles": ["glutes", "back"], "exercise_type": "compound", "effectiveness_coefficient": 0.85, "equipment": "barbell"},

    # === GLUTES ===
    {"name": "Ягодичный мостик со штангой", "name_en": "Barbell Hip Thrust", "muscle_group": "glutes", "secondary_muscles": ["hamstrings"], "exercise_type": "compound", "effectiveness_coefficient": 0.8, "equipment": "barbell"},
    {"name": "Отведение ноги в кроссовере", "name_en": "Cable Kickback", "muscle_group": "glutes", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "cable"},

    # === CALVES ===
    {"name": "Подъём на носки стоя", "name_en": "Standing Calf Raise", "muscle_group": "calves", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "machine"},
    {"name": "Подъём на носки сидя", "name_en": "Seated Calf Raise", "muscle_group": "calves", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "machine"},

    # === ABS ===
    {"name": "Скручивания", "name_en": "Crunches", "muscle_group": "abs", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.3, "equipment": "bodyweight"},
    {"name": "Планка", "name_en": "Plank", "muscle_group": "abs", "secondary_muscles": ["shoulders"], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "bodyweight"},
    {"name": "Подъём ног в висе", "name_en": "Hanging Leg Raise", "muscle_group": "abs", "secondary_muscles": ["forearms"], "exercise_type": "isolation", "effectiveness_coefficient": 0.4, "equipment": "bodyweight"},
    {"name": "Скручивания на верхнем блоке", "name_en": "Cable Crunch", "muscle_group": "abs", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "cable"},
    {"name": "Колесо для пресса", "name_en": "Ab Wheel Rollout", "muscle_group": "abs", "secondary_muscles": ["shoulders"], "exercise_type": "compound", "effectiveness_coefficient": 0.5, "equipment": "other"},

    # === TRAPS ===
    {"name": "Шраги со штангой", "name_en": "Barbell Shrugs", "muscle_group": "traps", "secondary_muscles": ["forearms"], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "barbell"},
    {"name": "Шраги с гантелями", "name_en": "Dumbbell Shrugs", "muscle_group": "traps", "secondary_muscles": ["forearms"], "exercise_type": "isolation", "effectiveness_coefficient": 0.35, "equipment": "dumbbell"},

    # === FOREARMS ===
    {"name": "Сгибание запястий со штангой", "name_en": "Wrist Curl", "muscle_group": "forearms", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.25, "equipment": "barbell"},
    {"name": "Разгибание запястий со штангой", "name_en": "Reverse Wrist Curl", "muscle_group": "forearms", "secondary_muscles": [], "exercise_type": "isolation", "effectiveness_coefficient": 0.25, "equipment": "barbell"},
]
