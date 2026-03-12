"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { listWorkouts, seedExercises } from "@/lib/api";

export default function Dashboard() {
  const [lastWorkout, setLastWorkout] = useState<any>(null);
  const [seeded, setSeeded] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const workouts = await listWorkouts(1, 0);
      if (workouts.length > 0) setLastWorkout(workouts[0]);
    } catch {}
    setLoading(false);
  }

  async function handleSeed() {
    const res = await seedExercises();
    setSeeded(true);
    alert(`Добавлено ${res.added} упражнений`);
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Дневник тренировок</h1>
        {!seeded && (
          <button onClick={handleSeed} className="text-xs bg-surface-2 px-3 py-1.5 rounded-lg text-text-secondary">
            Загрузить базу
          </button>
        )}
      </div>

      <Link
        href="/workout"
        className="block bg-primary text-white text-center py-4 rounded-2xl text-lg font-semibold active:bg-primary-dark transition-colors"
      >
        Начать тренировку
      </Link>

      {lastWorkout && (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          <div className="flex justify-between items-center">
            <h2 className="font-semibold">Последняя тренировка</h2>
            <span className="text-sm text-text-secondary">
              {new Date(lastWorkout.date).toLocaleDateString("ru-RU")}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="bg-surface-2 rounded-xl p-3">
              <div className="text-xl font-bold">{lastWorkout.exercises?.length || 0}</div>
              <div className="text-xs text-text-secondary">Упражнений</div>
            </div>
            <div className="bg-surface-2 rounded-xl p-3">
              <div className="text-xl font-bold">
                {lastWorkout.exercises?.reduce((a: number, e: any) => a + (e.sets?.length || 0), 0) || 0}
              </div>
              <div className="text-xs text-text-secondary">Подходов</div>
            </div>
            <div className="bg-surface-2 rounded-xl p-3">
              <div className="text-xl font-bold">{calcTonnage(lastWorkout).toLocaleString()}</div>
              <div className="text-xs text-text-secondary">кг тоннаж</div>
            </div>
          </div>
          <Link href={`/workout/${lastWorkout.id}`} className="block text-center text-sm text-primary">
            Подробнее
          </Link>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <Link href="/analytics" className="bg-surface rounded-2xl p-4 text-center">
          <div className="text-2xl mb-1">📊</div>
          <div className="font-medium">Аналитика</div>
        </Link>
        <Link href="/measurements" className="bg-surface rounded-2xl p-4 text-center">
          <div className="text-2xl mb-1">📏</div>
          <div className="font-medium">Замеры тела</div>
        </Link>
        <Link href="/inbody" className="bg-surface rounded-2xl p-4 text-center">
          <div className="text-2xl mb-1">🔬</div>
          <div className="font-medium">InBody</div>
        </Link>
        <Link href="/exercises" className="bg-surface rounded-2xl p-4 text-center">
          <div className="text-2xl mb-1">💪</div>
          <div className="font-medium">Упражнения</div>
        </Link>
        <Link href="/settings" className="bg-surface rounded-2xl p-4 text-center col-span-2 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20">
          <div className="text-2xl mb-1">🤖</div>
          <div className="font-medium text-purple-400">Настройки ИИ</div>
        </Link>
      </div>
    </div>
  );
}
