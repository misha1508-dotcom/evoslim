"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  startWorkout, finishWorkout, getExercises, searchExercises,
  addExerciseToWorkout, addSet, deleteSet, removeExerciseFromWorkout,
  createCheckin, getWorkout, listWorkouts, createExercise, getExerciseLastSets,
} from "@/lib/api";

type Phase = "checkin" | "training" | "done";

const MG_OPTIONS = [
  { value: "chest", label: "Грудь" }, { value: "back", label: "Спина" },
  { value: "shoulders", label: "Плечи" }, { value: "biceps", label: "Бицепс" },
  { value: "triceps", label: "Трицепс" }, { value: "quadriceps", label: "Квадрицепс" },
  { value: "hamstrings", label: "Бицепс бедра" }, { value: "glutes", label: "Ягодицы" },
  { value: "calves", label: "Икры" }, { value: "abs", label: "Пресс" },
  { value: "forearms", label: "Предплечья" }, { value: "traps", label: "Трапеции" },
];

export default function WorkoutPage() {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("checkin");
  const [workoutId, setWorkoutId] = useState<number | null>(null);
  const [workout, setWorkout] = useState<any>(null);

  const [sleep, setSleep] = useState(5);
  const [mood, setMood] = useState(5);
  const [breakfast, setBreakfast] = useState(false);
  const [coffee, setCoffee] = useState(false);

  const [showPicker, setShowPicker] = useState(false);
  const [pickerTab, setPickerTab] = useState<"search" | "last" | "custom">("search");
  const [exercises, setExercises] = useState<any[]>([]);
  const [searchQ, setSearchQ] = useState("");
  const [lastWorkout, setLastWorkout] = useState<any>(null);

  // Custom exercise form
  const [customName, setCustomName] = useState("");
  const [customMG, setCustomMG] = useState("chest");
  const [customType, setCustomType] = useState("compound");
  const [customEquip, setCustomEquip] = useState("barbell");

  const [activeWe, setActiveWe] = useState<number | null>(null);
  const [setWeight, setSetWeight] = useState("");
  const [setReps, setSetReps] = useState("");
  const [isWarmup, setIsWarmup] = useState(false);

  // Previous sets per exercise_id
  const [prevSets, setPrevSets] = useState<Record<number, any[]>>({});

  useEffect(() => {
    loadExercises();
  }, []);

  async function loadExercises() {
    const data = await getExercises();
    setExercises(data);
  }

  async function handleSearch(q: string) {
    setSearchQ(q);
    if (q.length >= 1) {
      const data = await searchExercises(q);
      setExercises(data);
    } else {
      loadExercises();
    }
  }

  async function handleStartWorkout() {
    const w = await startWorkout();
    setWorkoutId(w.id);
    await createCheckin({
      workout_id: w.id,
      sleep_quality: sleep,
      emotional_state: mood,
      had_breakfast: breakfast,
      had_coffee: coffee,
    });
    setPhase("training");
    reloadWorkout(w.id);
  }

  async function reloadWorkout(id: number) {
    const w = await getWorkout(id);
    setWorkout(w);
    // Load previous sets for all exercises
    for (const we of w.exercises || []) {
      if (!prevSets[we.exercise_id]) {
        loadPrevSets(we.exercise_id);
      }
    }
  }

  async function loadPrevSets(exerciseId: number) {
    try {
      const sets = await getExerciseLastSets(exerciseId, workoutId ?? undefined);
      setPrevSets(prev => ({ ...prev, [exerciseId]: sets }));
    } catch {
      // ignore
    }
  }

  async function openPicker() {
    setShowPicker(true);
    setPickerTab("search");
    setSearchQ("");
    loadExercises();
    // Load last workout for "from last" tab
    try {
      const workouts = await listWorkouts(2, 0);
      const prev = workouts.find((w: any) => w.id !== workoutId);
      setLastWorkout(prev || null);
    } catch {
      // ignore
    }
  }

  async function handleAddExercise(exerciseId: number) {
    if (!workoutId) return;
    const orderIdx = workout?.exercises?.length || 0;
    await addExerciseToWorkout(workoutId, exerciseId, orderIdx);
    await reloadWorkout(workoutId);
    setShowPicker(false);
    setSearchQ("");
    loadExercises();
    loadPrevSets(exerciseId);
  }

  async function handleAddFromLastWorkout() {
    if (!workoutId || !lastWorkout) return;
    for (const ex of lastWorkout.exercises || []) {
      const orderIdx = (workout?.exercises?.length || 0);
      await addExerciseToWorkout(workoutId, ex.exercise_id, orderIdx);
      await reloadWorkout(workoutId);
      loadPrevSets(ex.exercise_id);
    }
    setShowPicker(false);
  }

  async function handleCreateCustom() {
    if (!customName.trim()) return;
    const ex = await createExercise({
      name: customName.trim(),
      muscle_group: customMG,
      exercise_type: customType,
      equipment: customEquip,
    });
    await handleAddExercise(ex.id);
    setCustomName("");
  }

  async function handleAddSet() {
    if (!workoutId || !activeWe || !setWeight || !setReps) return;
    await addSet(workoutId, activeWe, {
      weight_kg: parseFloat(setWeight),
      reps: parseInt(setReps),
      is_warmup: isWarmup,
    });
    setSetWeight("");
    setSetReps("");
    setIsWarmup(false);
    await reloadWorkout(workoutId);
  }

  async function handleDeleteSet(weId: number, setId: number) {
    if (!workoutId) return;
    await deleteSet(workoutId, weId, setId);
    await reloadWorkout(workoutId);
  }

  async function handleRemoveExercise(weId: number) {
    if (!workoutId) return;
    await removeExerciseFromWorkout(workoutId, weId);
    await reloadWorkout(workoutId);
    if (activeWe === weId) setActiveWe(null);
  }

  async function handleFinish() {
    if (!workoutId) return;
    await finishWorkout(workoutId);
    setPhase("done");
  }

  // === ЧЕК-ИН ===
  if (phase === "checkin") {
    return (
      <div className="space-y-6">
        <h1 className="text-xl font-bold">Перед тренировкой</h1>

        <div className="bg-surface rounded-2xl p-4 space-y-4">
          <div>
            <label className="block text-sm text-text-secondary mb-1.5">Качество сна</label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((v) => (
                <button
                  key={v}
                  onClick={() => setSleep(v)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    sleep === v ? "bg-primary text-white" : "bg-surface-2 text-text-secondary"
                  }`}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm text-text-secondary mb-1.5">Эмоциональное состояние</label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((v) => (
                <button
                  key={v}
                  onClick={() => setMood(v)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    mood === v ? "bg-primary text-white" : "bg-surface-2 text-text-secondary"
                  }`}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => setBreakfast(!breakfast)}
              className={`flex-1 py-3 rounded-xl text-sm font-medium transition-colors ${
                breakfast ? "bg-primary text-white" : "bg-surface-2 text-text-secondary"
              }`}
            >
              🍳 Завтрак
            </button>
            <button
              onClick={() => setCoffee(!coffee)}
              className={`flex-1 py-3 rounded-xl text-sm font-medium transition-colors ${
                coffee ? "bg-primary text-white" : "bg-surface-2 text-text-secondary"
              }`}
            >
              ☕ Кофе
            </button>
          </div>
        </div>

        <button
          onClick={handleStartWorkout}
          className="w-full bg-primary text-white py-4 rounded-2xl text-lg font-semibold active:bg-primary-dark"
        >
          Начать тренировку
        </button>
      </div>
    );
  }

  // === ГОТОВО ===
  if (phase === "done") {
    return (
      <div className="text-center py-20 space-y-4">
        <div className="text-5xl">🎉</div>
        <h1 className="text-xl font-bold">Тренировка завершена!</h1>
        <button onClick={() => router.push("/")} className="text-primary underline">
          На главную
        </button>
      </div>
    );
  }

  // === ТРЕНИРОВКА ===
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Тренировка #{workoutId}</h1>
        <button
          onClick={handleFinish}
          className="bg-positive/20 text-positive px-4 py-2 rounded-xl text-sm font-medium"
        >
          Завершить
        </button>
      </div>

      {workout?.exercises?.map((we: any) => {
        const prev = prevSets[we.exercise_id];
        return (
          <div key={we.id} className="bg-surface rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">{we.exercise_name}</h3>
              <button onClick={() => handleRemoveExercise(we.id)} className="text-negative text-sm">
                Убрать
              </button>
            </div>

            {/* Previous workout sets */}
            {prev && prev.length > 0 && (
              <div className="bg-surface-2/50 rounded-xl px-3 py-2">
                <div className="text-xs text-text-secondary mb-1">Прошлая тренировка:</div>
                <div className="flex flex-wrap gap-x-3 gap-y-0.5">
                  {prev.filter((s: any) => !s.is_warmup).map((s: any, i: number) => (
                    <span key={i} className="text-xs text-text-secondary">
                      {s.weight_kg}кг×{s.reps}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {we.sets?.length > 0 && (
              <div className="space-y-1">
                <div className="grid grid-cols-4 text-xs text-text-secondary px-1">
                  <span>Подход</span><span>Вес</span><span>Повт.</span><span></span>
                </div>
                {we.sets.map((s: any) => (
                  <div key={s.id} className={`grid grid-cols-4 text-sm px-1 py-1 rounded ${s.is_warmup ? "text-text-secondary" : ""}`}>
                    <span>{s.is_warmup ? "Р" : s.set_number}</span>
                    <span>{s.weight_kg} кг</span>
                    <span>{s.reps} повт</span>
                    <button onClick={() => handleDeleteSet(we.id, s.id)} className="text-negative/60 text-right text-xs">
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}

            {activeWe === we.id ? (
              <div className="space-y-2">
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    placeholder="Вес (кг)"
                    value={setWeight}
                    onChange={(e) => setSetWeight(e.target.value)}
                    className="bg-surface-2 rounded-xl px-3 py-2.5 text-sm"
                    inputMode="decimal"
                  />
                  <input
                    type="number"
                    placeholder="Повторения"
                    value={setReps}
                    onChange={(e) => setSetReps(e.target.value)}
                    className="bg-surface-2 rounded-xl px-3 py-2.5 text-sm"
                    inputMode="numeric"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setIsWarmup(!isWarmup)}
                    className={`px-3 py-2 rounded-xl text-xs ${isWarmup ? "bg-warning/20 text-warning" : "bg-surface-2 text-text-secondary"}`}
                  >
                    Разминка
                  </button>
                  <button
                    onClick={handleAddSet}
                    className="flex-1 bg-primary text-white py-2 rounded-xl text-sm font-medium"
                  >
                    + Добавить подход
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setActiveWe(we.id)}
                className="w-full text-primary text-sm py-2"
              >
                + Добавить подход
              </button>
            )}
          </div>
        );
      })}

      {!showPicker ? (
        <button
          onClick={openPicker}
          className="w-full border-2 border-dashed border-surface-2 rounded-2xl py-4 text-text-secondary"
        >
          + Добавить упражнение
        </button>
      ) : (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          {/* Tabs */}
          <div className="flex gap-1.5">
            {[
              { key: "search" as const, label: "Поиск" },
              { key: "last" as const, label: "Из прошлой" },
              { key: "custom" as const, label: "Своё" },
            ].map((t) => (
              <button
                key={t.key}
                onClick={() => setPickerTab(t.key)}
                className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  pickerTab === t.key ? "bg-primary text-white" : "bg-surface-2 text-text-secondary"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Search tab */}
          {pickerTab === "search" && (
            <>
              <input
                type="text"
                placeholder="Поиск упражнений..."
                value={searchQ}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full bg-surface-2 rounded-xl px-3 py-2.5 text-sm"
                autoFocus
              />
              <div className="max-h-64 overflow-y-auto space-y-1">
                {exercises.map((ex) => (
                  <button
                    key={ex.id}
                    onClick={() => handleAddExercise(ex.id)}
                    className="w-full text-left px-3 py-2 rounded-xl hover:bg-surface-2 transition-colors"
                  >
                    <div className="text-sm font-medium">{ex.name}</div>
                    <div className="text-xs text-text-secondary">
                      {ex.muscle_group} · {ex.exercise_type} · {ex.equipment}
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Last workout tab */}
          {pickerTab === "last" && (
            <>
              {lastWorkout ? (
                <div className="space-y-2">
                  <div className="text-xs text-text-secondary">
                    {new Date(lastWorkout.date).toLocaleDateString("ru-RU", { day: "numeric", month: "short" })}
                    {" · "}{lastWorkout.exercises?.length || 0} упр.
                  </div>
                  {lastWorkout.exercises?.map((ex: any) => (
                    <button
                      key={ex.id}
                      onClick={() => handleAddExercise(ex.exercise_id)}
                      className="w-full text-left px-3 py-2 rounded-xl hover:bg-surface-2 transition-colors"
                    >
                      <div className="text-sm font-medium">{ex.exercise_name}</div>
                      <div className="text-xs text-text-secondary">
                        {ex.sets?.filter((s: any) => !s.is_warmup).map((s: any) => `${s.weight_kg}×${s.reps}`).join(", ")}
                      </div>
                    </button>
                  ))}
                  <button
                    onClick={handleAddFromLastWorkout}
                    className="w-full bg-primary/10 text-primary py-2 rounded-xl text-sm font-medium"
                  >
                    Добавить все сразу
                  </button>
                </div>
              ) : (
                <div className="text-center py-4 text-text-secondary text-sm">
                  Прошлых тренировок нет
                </div>
              )}
            </>
          )}

          {/* Custom exercise tab */}
          {pickerTab === "custom" && (
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Название упражнения"
                value={customName}
                onChange={(e) => setCustomName(e.target.value)}
                className="w-full bg-surface-2 rounded-xl px-3 py-2.5 text-sm"
                autoFocus
              />
              <select
                value={customMG}
                onChange={(e) => setCustomMG(e.target.value)}
                className="w-full bg-surface-2 rounded-xl px-3 py-2 text-sm"
              >
                {MG_OPTIONS.map((mg) => (
                  <option key={mg.value} value={mg.value}>{mg.label}</option>
                ))}
              </select>
              <div className="grid grid-cols-2 gap-2">
                <select
                  value={customType}
                  onChange={(e) => setCustomType(e.target.value)}
                  className="bg-surface-2 rounded-xl px-3 py-2 text-sm"
                >
                  <option value="compound">Базовое</option>
                  <option value="isolation">Изоляция</option>
                </select>
                <select
                  value={customEquip}
                  onChange={(e) => setCustomEquip(e.target.value)}
                  className="bg-surface-2 rounded-xl px-3 py-2 text-sm"
                >
                  <option value="barbell">Штанга</option>
                  <option value="dumbbell">Гантели</option>
                  <option value="machine">Тренажёр</option>
                  <option value="cable">Блок</option>
                  <option value="bodyweight">Своё тело</option>
                  <option value="other">Другое</option>
                </select>
              </div>
              <button
                onClick={handleCreateCustom}
                className="w-full bg-primary text-white py-2.5 rounded-xl text-sm font-medium"
              >
                Создать и добавить
              </button>
            </div>
          )}

          <button onClick={() => { setShowPicker(false); setSearchQ(""); loadExercises(); }} className="w-full text-text-secondary text-sm py-1">
            Отмена
          </button>
        </div>
      )}
    </div>
  );
}
