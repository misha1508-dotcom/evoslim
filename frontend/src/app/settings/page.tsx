"use client";
import { useEffect, useState } from "react";
import { getUserInfo, updateUserInfo } from "@/lib/api";

export default function SettingsPage() {
  const [genetic, setGenetic] = useState("");
  const [allergies, setAllergies] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const user = await getUserInfo();
        setGenetic(user.genetic_context || "");
        setAllergies(user.allergies_and_risks || "");
      } catch (e) {
        console.error("Failed to fetch user data", e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function handleSave() {
    setSaving(true);
    try {
      await updateUserInfo({
        genetic_context: genetic,
        allergies_and_risks: allergies,
      });
      alert("Настройки сохранены!");
    } catch (e) {
      alert("Ошибка сохранения настроек");
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="p-4 text-center">Загрузка...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Настройки ИИ-Тренера</h1>
      
      <div className="space-y-4 bg-surface p-4 rounded-2xl">
        <div>
          <label className="block text-sm font-medium mb-1">Опыт и контекст (генетика, стаж)</label>
          <textarea
            className="w-full bg-surface-2 p-3 rounded-xl min-h-[100px]"
            placeholder="Опишите ваш опыт тренировок, генетические особенности..."
            value={genetic}
            onChange={(e) => setGenetic(e.target.value)}
          />
        </div>

        <div>
           <label className="block text-sm font-medium mb-1 text-red-500">Противопоказания и аллергии</label>
           <textarea
             className="w-full bg-surface-2 p-3 rounded-xl min-h-[100px] border border-red-500/30 text-red-400 focus:border-red-500"
             placeholder="Укажите травмы, ограничения по здоровью, аллергии на продукты..."
             value={allergies}
             onChange={(e) => setAllergies(e.target.value)}
           />
           <p className="text-xs text-text-secondary mt-1">Эти данные будут строгим правилом для ИИ при составлении программ питания и тренировок.</p>
        </div>
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="w-full bg-primary text-white py-4 rounded-2xl text-lg font-semibold active:bg-primary-dark transition-colors disabled:opacity-50"
      >
        {saving ? "Сохранение..." : "Сохранить настройки"}
      </button>
    </div>
  );
}
