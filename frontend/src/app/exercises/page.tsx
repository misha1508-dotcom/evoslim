"use client";
import { useEffect, useState } from "react";
import { getExercises } from "@/lib/api";

const MG_LABELS: Record<string, string> = {
  chest: "Грудь", back: "Спина", shoulders: "Плечи", biceps: "Бицепс",
  triceps: "Трицепс", quadriceps: "Квадрицепсы", hamstrings: "Бицепс бедра", glutes: "Ягодицы",
  calves: "Икры", abs: "Пресс", forearms: "Предплечья", traps: "Трапеции",
};

const ALL_GROUPS = Object.keys(MG_LABELS);

export default function ExercisesPage() {
  const [exercises, setExercises] = useState<any[]>([]);
  const [filter, setFilter] = useState<string | null>(null);

  useEffect(() => {
    loadExercises();
  }, [filter]);

  async function loadExercises() {
    const data = await getExercises(filter ?? undefined);
    setExercises(data);
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Каталог упражнений</h1>

      <div className="flex gap-1.5 overflow-x-auto pb-1">
        <button
          onClick={() => setFilter(null)}
          className={`px-3 py-1 rounded-lg text-xs font-medium whitespace-nowrap ${!filter ? "bg-primary text-white" : "bg-surface text-text-secondary"}`}
        >
          Все
        </button>
        {ALL_GROUPS.map((g) => (
          <button
            key={g}
            onClick={() => setFilter(g)}
            className={`px-3 py-1 rounded-lg text-xs font-medium whitespace-nowrap ${filter === g ? "bg-primary text-white" : "bg-surface text-text-secondary"}`}
          >
            {MG_LABELS[g]}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {exercises.map((ex) => (
          <div key={ex.id} className="bg-surface rounded-xl p-3 flex items-center justify-between">
            <div>
              <div className="font-medium text-sm">{ex.name}</div>
              <div className="text-xs text-text-secondary">
                {MG_LABELS[ex.muscle_group] || ex.muscle_group} · {ex.exercise_type} · {ex.equipment}
              </div>
            </div>
            <div className="text-right">
              <div className={`text-xs font-medium ${ex.effectiveness_coefficient >= 0.8 ? "text-positive" : ex.effectiveness_coefficient >= 0.5 ? "text-warning" : "text-text-secondary"}`}>
                {(ex.effectiveness_coefficient * 100).toFixed(0)}%
              </div>
              <div className="text-[10px] text-text-secondary">эфф.</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
