"use client";
import { useEffect, useState } from "react";
import {
  getTonnage, getExerciseProgress, getMuscleGroupVolume, getCheckinCorrelation, getExercises,
} from "@/lib/api";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, Legend, ScatterChart, Scatter, ZAxis,
} from "recharts";

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4", "#ec4899", "#8b5cf6", "#10b981", "#f97316", "#64748b", "#e11d48", "#14b8a6"];
const MG_LABELS: Record<string, string> = {
  chest: "Грудь", back: "Спина", shoulders: "Плечи", biceps: "Бицепс",
  triceps: "Трицепс", quadriceps: "Квадр.", hamstrings: "Бицепс б.", glutes: "Ягодицы",
  calves: "Икры", abs: "Пресс", forearms: "Предпл.", traps: "Трапеции",
};

export default function AnalyticsPage() {
  const [tab, setTab] = useState<"tonnage" | "progress" | "muscles" | "checkin">("tonnage");
  const [tonnageData, setTonnageData] = useState<any[]>([]);
  const [muscleData, setMuscleData] = useState<any[]>([]);
  const [checkinData, setCheckinData] = useState<any[]>([]);
  const [exercises, setExercises] = useState<any[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<number | null>(null);
  const [progressData, setProgressData] = useState<any[]>([]);

  useEffect(() => {
    getTonnage().then(setTonnageData).catch(() => {});
    getMuscleGroupVolume().then(setMuscleData).catch(() => {});
    getCheckinCorrelation().then(setCheckinData).catch(() => {});
    getExercises().then((data) => {
      setExercises(data.filter((e: any) => e.exercise_type === "compound"));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedExercise) {
      getExerciseProgress(selectedExercise).then(setProgressData).catch(() => {});
    }
  }, [selectedExercise]);

  const tabs = [
    { key: "tonnage", label: "Тоннаж" },
    { key: "progress", label: "Прогресс" },
    { key: "muscles", label: "Мышцы" },
    { key: "checkin", label: "Чек-ин" },
  ] as const;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Аналитика</h1>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-3 py-1.5 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${
              tab === t.key ? "bg-primary text-white" : "bg-surface text-text-secondary"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Тоннаж */}
      {tab === "tonnage" && (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          <h2 className="font-semibold text-sm">Тоннаж по тренировкам</h2>
          {tonnageData.length === 0 ? (
            <p className="text-text-secondary text-sm py-4 text-center">Данных пока нет</p>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={tonnageData.map((d) => ({ ...d, date: d.date?.slice(5, 10) }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "#1e293b", border: "none", borderRadius: 12, fontSize: 12 }}
                  labelStyle={{ color: "#94a3b8" }}
                />
                <Bar dataKey="tonnage" fill="#6366f1" radius={[4, 4, 0, 0]} name="Общий" />
                <Bar dataKey="effective_tonnage" fill="#22c55e" radius={[4, 4, 0, 0]} name="Эффективный" />
                <Legend />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      )}

      {/* Прогресс */}
      {tab === "progress" && (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          <h2 className="font-semibold text-sm">Прогресс силовых (расчётный 1ПМ)</h2>
          <select
            value={selectedExercise ?? ""}
            onChange={(e) => setSelectedExercise(Number(e.target.value) || null)}
            className="w-full bg-surface-2 rounded-xl px-3 py-2 text-sm"
          >
            <option value="">Выберите упражнение</option>
            {exercises.map((ex) => (
              <option key={ex.id} value={ex.id}>{ex.name}</option>
            ))}
          </select>
          {progressData.length > 0 && (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={progressData.map((d) => ({ ...d, date: d.date?.slice(5, 10) }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "none", borderRadius: 12, fontSize: 12 }} />
                <Line type="monotone" dataKey="estimated_1rm" stroke="#6366f1" strokeWidth={2} dot={{ r: 4 }} name="1ПМ (кг)" />
                <Line type="monotone" dataKey="best_weight" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} name="Лучший вес" />
                <Legend />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      )}

      {/* Группы мышц */}
      {tab === "muscles" && (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          <h2 className="font-semibold text-sm">Объём по группам мышц (30 дней)</h2>
          {muscleData.length === 0 ? (
            <p className="text-text-secondary text-sm py-4 text-center">Данных пока нет</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={muscleData.map((d) => ({ ...d, name: MG_LABELS[d.muscle_group] || d.muscle_group }))} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis type="category" dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} width={60} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "none", borderRadius: 12, fontSize: 12 }} />
                <Bar dataKey="volume" radius={[0, 4, 4, 0]}>
                  {muscleData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      )}

      {/* Корреляция чек-ина */}
      {tab === "checkin" && (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          <h2 className="font-semibold text-sm">Чек-ин vs Результаты</h2>
          {checkinData.length === 0 ? (
            <p className="text-text-secondary text-sm py-4 text-center">Данных пока нет</p>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={250}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="sleep_quality" name="Сон" tick={{ fill: "#94a3b8", fontSize: 11 }} type="number" domain={[0, 6]} />
                  <YAxis dataKey="effective_tonnage" name="Эфф. тоннаж" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                  <ZAxis dataKey="emotional_state" range={[40, 200]} name="Настрой" />
                  <Tooltip contentStyle={{ background: "#1e293b", border: "none", borderRadius: 12, fontSize: 12 }} />
                  <Scatter data={checkinData} fill="#6366f1" />
                </ScatterChart>
              </ResponsiveContainer>
              <div className="text-xs text-text-secondary text-center">X: качество сна, Y: эффективный тоннаж, размер: настроение</div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
