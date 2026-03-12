"use client";
import { useEffect, useState, useRef } from "react";
import { uploadInBody, listInBody, compareInBody } from "@/lib/api";

const MAIN_FIELDS = [
  { key: "weight_kg", label: "Вес", unit: "кг" },
  { key: "skeletal_muscle_mass_kg", label: "Скелетные мышцы", unit: "кг" },
  { key: "body_fat_mass_kg", label: "Жировая масса", unit: "кг" },
  { key: "body_fat_percent", label: "% жира", unit: "%" },
  { key: "bmi", label: "ИМТ", unit: "" },
  { key: "total_body_water_l", label: "Вода общая", unit: "л" },
  { key: "protein_kg", label: "Белок", unit: "кг" },
  { key: "minerals_kg", label: "Минералы", unit: "кг" },
  { key: "fat_free_mass_kg", label: "Безжировая масса", unit: "кг" },
  { key: "basal_metabolic_rate_kcal", label: "Базовый метаболизм", unit: "ккал" },
  { key: "visceral_fat_level", label: "Висц. жир", unit: "ур" },
  { key: "inbody_score", label: "Балл InBody", unit: "/100" },
  { key: "ideal_weight_kg", label: "Идеал. вес", unit: "кг" },
];

const SEGMENTS_LEAN = [
  { key: "lean_mass_left_arm_kg", label: "Л рука" },
  { key: "lean_mass_right_arm_kg", label: "П рука" },
  { key: "lean_mass_trunk_kg", label: "Корпус" },
  { key: "lean_mass_left_leg_kg", label: "Л нога" },
  { key: "lean_mass_right_leg_kg", label: "П нога" },
];

const SEGMENTS_FAT = [
  { key: "fat_mass_left_arm_kg", label: "Л рука" },
  { key: "fat_mass_right_arm_kg", label: "П рука" },
  { key: "fat_mass_trunk_kg", label: "Корпус" },
  { key: "fat_mass_left_leg_kg", label: "Л нога" },
  { key: "fat_mass_right_leg_kg", label: "П нога" },
];

export default function InBodyPage() {
  const [scans, setScans] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [comparison, setComparison] = useState<any>(null);
  const [selectedScan, setSelectedScan] = useState<any>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadScans();
  }, []);

  async function loadScans() {
    const data = await listInBody();
    setScans(data);
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadInBody(file);
      await loadScans();
    } catch (err) {
      alert("Ошибка загрузки: " + (err as Error).message);
    }
    setUploading(false);
    if (fileRef.current) fileRef.current.value = "";
  }

  async function handleCompare() {
    if (scans.length < 2) return;
    const data = await compareInBody(scans[0].id, scans[1].id);
    setComparison(data);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">InBody сканы</h1>
        <label className="bg-primary text-white px-3 py-1.5 rounded-xl text-sm font-medium cursor-pointer">
          {uploading ? "Обработка..." : "+ Загрузить"}
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleUpload}
            className="hidden"
            disabled={uploading}
          />
        </label>
      </div>

      {scans.length >= 2 && !comparison && (
        <button
          onClick={handleCompare}
          className="w-full bg-surface text-primary py-3 rounded-2xl text-sm font-medium border border-primary/30"
        >
          Сравнить последние 2 скана
        </button>
      )}

      {/* Сравнение */}
      {comparison && (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-sm">Сравнение</h2>
            <button onClick={() => setComparison(null)} className="text-text-secondary text-xs">Закрыть</button>
          </div>
          <div className="space-y-1">
            {Object.entries(comparison.comparison).map(([key, val]: [string, any]) => {
              const label = MAIN_FIELDS.find((f) => f.key === key)?.label || key;
              const color = val.direction === "positive" ? "text-positive" : val.direction === "negative" ? "text-negative" : "text-text-secondary";
              const arrow = val.diff > 0 ? "↑" : val.diff < 0 ? "↓" : "→";
              return (
                <div key={key} className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">{label}</span>
                  <span className="flex items-center gap-2">
                    <span>{val.scan2}</span>
                    <span className={`font-medium ${color}`}>{arrow} {Math.abs(val.diff)}</span>
                    <span>{val.scan1}</span>
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Детали скана */}
      {selectedScan && (
        <div className="bg-surface rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-sm">
              Скан {new Date(selectedScan.date).toLocaleDateString("ru-RU")}
            </h2>
            <button onClick={() => setSelectedScan(null)} className="text-text-secondary text-xs">Закрыть</button>
          </div>

          <div className="grid grid-cols-2 gap-x-4 gap-y-1">
            {MAIN_FIELDS.map((f) => {
              const val = selectedScan[f.key];
              if (val == null) return null;
              return (
                <div key={f.key} className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">{f.label}</span>
                  <span className="font-medium">{val} {f.unit}</span>
                </div>
              );
            })}
          </div>

          <div>
            <h3 className="text-xs text-text-secondary mb-1">Сегм. мышечная масса</h3>
            <div className="grid grid-cols-5 gap-1 text-center">
              {SEGMENTS_LEAN.map((s) => (
                <div key={s.key} className="bg-surface-2 rounded-lg p-1.5">
                  <div className="text-xs text-text-secondary">{s.label}</div>
                  <div className="text-sm font-medium">{selectedScan[s.key] ?? "—"}</div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-xs text-text-secondary mb-1">Сегм. жировая масса</h3>
            <div className="grid grid-cols-5 gap-1 text-center">
              {SEGMENTS_FAT.map((s) => (
                <div key={s.key} className="bg-surface-2 rounded-lg p-1.5">
                  <div className="text-xs text-text-secondary">{s.label}</div>
                  <div className="text-sm font-medium">{selectedScan[s.key] ?? "—"}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Список сканов */}
      {scans.length === 0 ? (
        <div className="text-center py-10 text-text-secondary">
          <p>Сканов пока нет</p>
          <p className="text-xs mt-1">Загрузите фото вашего результата InBody</p>
        </div>
      ) : (
        scans.map((s) => (
          <button
            key={s.id}
            onClick={() => setSelectedScan(s)}
            className="w-full bg-surface rounded-2xl p-4 text-left space-y-2"
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold text-sm">
                {new Date(s.date).toLocaleDateString("ru-RU", { day: "numeric", month: "short", year: "numeric" })}
              </span>
              {s.inbody_score && (
                <span className="bg-primary/20 text-primary px-2 py-0.5 rounded text-xs font-medium">
                  Балл: {s.inbody_score}
                </span>
              )}
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <div className="text-xs text-text-secondary">Вес</div>
                <div className="text-sm font-medium">{s.weight_kg} кг</div>
              </div>
              <div>
                <div className="text-xs text-text-secondary">Мышцы</div>
                <div className="text-sm font-medium">{s.skeletal_muscle_mass_kg} кг</div>
              </div>
              <div>
                <div className="text-xs text-text-secondary">Жир</div>
                <div className="text-sm font-medium">{s.body_fat_percent}%</div>
              </div>
            </div>
          </button>
        ))
      )}
    </div>
  );
}
