"use client";
import { useEffect, useState } from "react";
import { createMeasurement, listMeasurements } from "@/lib/api";

const FIELDS = [
  { key: "weight_kg", label: "Вес (кг)" },
  { key: "chest_cm", label: "Грудь (см)" },
  { key: "shoulders_cm", label: "Плечи (см)" },
  { key: "waist_cm", label: "Талия (см)" },
  { key: "hips_cm", label: "Бёдра (см)" },
  { key: "left_arm_cm", label: "Л рука (см)" },
  { key: "right_arm_cm", label: "П рука (см)" },
  { key: "left_thigh_cm", label: "Л бедро (см)" },
  { key: "right_thigh_cm", label: "П бедро (см)" },
  { key: "left_calf_cm", label: "Л икра (см)" },
  { key: "right_calf_cm", label: "П икра (см)" },
  { key: "neck_cm", label: "Шея (см)" },
];

function DeltaIndicator({ delta }: { delta: any }) {
  if (!delta) return <span className="text-text-secondary text-xs">—</span>;
  const { diff, direction } = delta;
  const color = direction === "positive" ? "text-positive" : direction === "negative" ? "text-negative" : "text-text-secondary";
  const arrow = diff > 0 ? "↑" : diff < 0 ? "↓" : "→";
  return (
    <span className={`text-xs font-medium ${color}`}>
      {arrow} {Math.abs(diff).toFixed(1)}
    </span>
  );
}

export default function MeasurementsPage() {
  const [measurements, setMeasurements] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    const data = await listMeasurements();
    setMeasurements(data);
    setLoading(false);
  }

  function updateField(key: string, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit() {
    const data: Record<string, number | undefined> = {};
    for (const f of FIELDS) {
      const val = form[f.key];
      if (val && val.trim()) data[f.key] = parseFloat(val);
    }
    await createMeasurement(data);
    setShowForm(false);
    setForm({});
    loadData();
  }

  if (loading) return <div className="text-center py-20 text-text-secondary">Загрузка...</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Замеры тела</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-primary text-white px-3 py-1.5 rounded-xl text-sm font-medium"
        >
          {showForm ? "Отмена" : "+ Новый"}
        </button>
      </div>

      {showForm && (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          <div className="grid grid-cols-2 gap-2">
            {FIELDS.map((f) => (
              <div key={f.key}>
                <label className="text-xs text-text-secondary">{f.label}</label>
                <input
                  type="number"
                  value={form[f.key] || ""}
                  onChange={(e) => updateField(f.key, e.target.value)}
                  className="w-full bg-surface-2 rounded-lg px-2 py-1.5 text-sm mt-0.5"
                  inputMode="decimal"
                  step="0.1"
                />
              </div>
            ))}
          </div>
          <button onClick={handleSubmit} className="w-full bg-primary text-white py-3 rounded-xl font-medium">
            Сохранить
          </button>
        </div>
      )}

      {measurements.length === 0 ? (
        <div className="text-center py-10 text-text-secondary">Замеров пока нет</div>
      ) : (
        measurements.map((m) => (
          <div key={m.id} className="bg-surface rounded-2xl p-4 space-y-2">
            <div className="text-sm font-semibold">
              {new Date(m.date).toLocaleDateString("ru-RU", { day: "numeric", month: "short", year: "numeric" })}
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1">
              {FIELDS.map((f) => {
                const val = m[f.key];
                if (val == null) return null;
                return (
                  <div key={f.key} className="flex items-center justify-between text-sm">
                    <span className="text-text-secondary">{f.label}</span>
                    <span className="flex items-center gap-1.5">
                      <span className="font-medium">{val}</span>
                      <DeltaIndicator delta={m.deltas?.[f.key]} />
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
