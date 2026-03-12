"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { listWorkouts, deleteWorkout } from "@/lib/api";

export default function HistoryPage() {
  const [workouts, setWorkouts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorkouts();
  }, []);

  async function loadWorkouts() {
    const data = await listWorkouts(50, 0);
    setWorkouts(data);
    setLoading(false);
  }

  async function handleDelete(id: number) {
    if (!confirm("Удалить эту тренировку?")) return;
    await deleteWorkout(id);
    loadWorkouts();
  }

  function calcTonnage(w: any) {
    let t = 0;
    for (const ex of w.exercises || []) {
      for (const s of ex.sets || []) {
        if (!s.is_warmup) t += s.weight_kg * s.reps;
      }
    }
    return Math.round(t);
  }

  if (loading) return <div className="text-center py-20 text-text-secondary">Загрузка...</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">История тренировок</h1>

      {workouts.length === 0 && (
        <div className="text-center py-10 text-text-secondary">Тренировок пока нет</div>
      )}

      {workouts.map((w) => {
        const totalSets = w.exercises?.reduce((a: number, e: any) => a + (e.sets?.length || 0), 0) || 0;
        return (
          <div key={w.id} className="bg-surface rounded-2xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <Link href={`/workout/${w.id}`} className="font-semibold">
                {new Date(w.date).toLocaleDateString("ru-RU", {
                  weekday: "short", day: "numeric", month: "short",
                })}
              </Link>
              <button onClick={() => handleDelete(w.id)} className="text-negative/50 text-xs">Удалить</button>
            </div>
            <div className="flex gap-4 text-sm text-text-secondary">
              <span>{w.exercises?.length || 0} упр.</span>
              <span>{totalSets} подх.</span>
              <span>{calcTonnage(w).toLocaleString()} кг</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {w.exercises?.map((ex: any) => (
                <span key={ex.id} className="bg-surface-2 px-2 py-0.5 rounded text-xs">
                  {ex.exercise_name}
                </span>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
