"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getWorkout, getCheckin } from "@/lib/api";

export default function WorkoutDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const [workout, setWorkout] = useState<any>(null);
  const [checkin, setCheckin] = useState<any>(null);

  useEffect(() => {
    if (id) {
      getWorkout(id).then(setWorkout);
      getCheckin(id).then(setCheckin).catch(() => {});
    }
  }, [id]);

  if (!workout) return <div className="text-center py-20 text-text-secondary">Загрузка...</div>;

  let totalTonnage = 0;
  for (const ex of workout.exercises || []) {
    for (const s of ex.sets || []) {
      if (!s.is_warmup) totalTonnage += s.weight_kg * s.reps;
    }
  }

  const duration =
    workout.started_at && workout.finished_at
      ? Math.round((new Date(workout.finished_at).getTime() - new Date(workout.started_at).getTime()) / 60000)
      : null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Link href="/history" className="text-text-secondary text-sm">&larr; Назад</Link>
        <h1 className="text-lg font-bold">Тренировка #{id}</h1>
        <span className="text-sm text-text-secondary">
          {new Date(workout.date).toLocaleDateString("ru-RU")}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="bg-surface rounded-xl p-3 text-center">
          <div className="text-lg font-bold">{workout.exercises?.length || 0}</div>
          <div className="text-xs text-text-secondary">Упражнений</div>
        </div>
        <div className="bg-surface rounded-xl p-3 text-center">
          <div className="text-lg font-bold">{Math.round(totalTonnage).toLocaleString()}</div>
          <div className="text-xs text-text-secondary">кг тоннаж</div>
        </div>
        <div className="bg-surface rounded-xl p-3 text-center">
          <div className="text-lg font-bold">{duration ? `${duration} мин` : "—"}</div>
          <div className="text-xs text-text-secondary">Длительность</div>
        </div>
      </div>

      {checkin && (
        <div className="bg-surface rounded-2xl p-4 space-y-2">
          <h2 className="font-semibold text-sm">Чек-ин</h2>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>Сон: <span className="font-medium">{checkin.sleep_quality}/10</span></div>
            <div>Настрой: <span className="font-medium">{checkin.emotional_state}/10</span></div>
            <div>Завтрак: <span className="font-medium">{checkin.had_breakfast ? "Да" : "Нет"}</span></div>
            <div>Кофе: <span className="font-medium">{checkin.had_coffee ? "Да" : "Нет"}</span></div>
          </div>
        </div>
      )}

      {workout.exercises?.map((we: any) => (
        <div key={we.id} className="bg-surface rounded-2xl p-4 space-y-2">
          <h3 className="font-semibold">{we.exercise_name}</h3>
          <div className="space-y-1">
            <div className="grid grid-cols-3 text-xs text-text-secondary">
              <span>Подход</span><span>Вес</span><span>Повт.</span>
            </div>
            {we.sets?.map((s: any) => (
              <div key={s.id} className={`grid grid-cols-3 text-sm ${s.is_warmup ? "text-text-secondary" : ""}`}>
                <span>{s.is_warmup ? "Р" : s.set_number}</span>
                <span>{s.weight_kg} кг</span>
                <span>{s.reps}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
