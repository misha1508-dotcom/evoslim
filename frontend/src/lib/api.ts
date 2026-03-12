const BASE = (typeof window !== "undefined" && window.location.pathname.startsWith("/training"))
  ? "/training/api"
  : "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json", ...(options?.headers as any) };
  
  if (typeof window !== "undefined" && (window as any).Telegram?.WebApp?.initData) {
    headers["Authorization"] = `tma ${(window as any).Telegram.WebApp.initData}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    headers,
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Exercises
export const getExercises = (muscleGroup?: string) =>
  request<any[]>(`/exercises${muscleGroup ? `?muscle_group=${muscleGroup}` : ""}`);
export const searchExercises = (q: string) => request<any[]>(`/exercises/search?q=${encodeURIComponent(q)}`);
export const createExercise = (data: { name: string; muscle_group: string; exercise_type: string; equipment: string; effectiveness_coefficient?: number }) =>
  request<any>("/exercises", { method: "POST", body: JSON.stringify(data) });
export const getExerciseLastSets = (exerciseId: number, excludeWorkout?: number) =>
  request<any[]>(`/exercises/${exerciseId}/last-sets${excludeWorkout ? `?exclude_workout=${excludeWorkout}` : ""}`);
export const seedExercises = () => request<any>("/exercises/seed", { method: "POST" });

// Workouts
export const startWorkout = (notes?: string) =>
  request<any>("/workouts", { method: "POST", body: JSON.stringify({ notes }) });
export const startPlannedWorkout = (id: number) =>
  request<any>(`/workouts/${id}/start`, { method: "POST" });
export const listWorkouts = (limit = 20, offset = 0) =>
  request<any[]>(`/workouts?limit=${limit}&offset=${offset}`);
export const getWorkout = (id: number) => request<any>(`/workouts/${id}`);
export const finishWorkout = (id: number) =>
  request<any>(`/workouts/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ finished_at: new Date().toISOString() }),
  });
export const deleteWorkout = (id: number) =>
  request<void>(`/workouts/${id}`, { method: "DELETE" });

// Workout exercises
export const addExerciseToWorkout = (workoutId: number, exerciseId: number, orderIndex: number) =>
  request<any>(`/workouts/${workoutId}/exercises`, {
    method: "POST",
    body: JSON.stringify({ exercise_id: exerciseId, order_index: orderIndex }),
  });
export const removeExerciseFromWorkout = (workoutId: number, weId: number) =>
  request<void>(`/workouts/${workoutId}/exercises/${weId}`, { method: "DELETE" });

// Sets
export const addSet = (workoutId: number, weId: number, data: { weight_kg: number; reps: number; is_warmup?: boolean }) =>
  request<any>(`/workouts/${workoutId}/exercises/${weId}/sets`, {
    method: "POST",
    body: JSON.stringify(data),
  });
export const deleteSet = (workoutId: number, weId: number, setId: number) =>
  request<void>(`/workouts/${workoutId}/exercises/${weId}/sets/${setId}`, { method: "DELETE" });

// Checkins
export const createCheckin = (data: any) =>
  request<any>("/checkins", { method: "POST", body: JSON.stringify(data) });
export const getCheckin = (workoutId: number) => request<any>(`/checkins/${workoutId}`);

// Measurements
export const createMeasurement = (data: any) =>
  request<any>("/measurements", { method: "POST", body: JSON.stringify(data) });
export const listMeasurements = () => request<any[]>("/measurements");
export const getLatestMeasurement = () => request<any>("/measurements/latest");

// InBody
export const uploadInBody = async (file: File) => {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/inbody/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
};
export const listInBody = () => request<any[]>("/inbody");
export const getInBody = (id: number) => request<any>(`/inbody/${id}`);
export const compareInBody = (id1: number, id2: number) => request<any>(`/inbody/compare/${id1}/${id2}`);

// Analytics
export const getTonnage = (from?: string, to?: string) => {
  const params = new URLSearchParams();
  if (from) params.set("date_from", from);
  if (to) params.set("date_to", to);
  return request<any[]>(`/analytics/tonnage?${params}`);
};
export const getEffectiveTonnage = (from?: string, to?: string) => {
  const params = new URLSearchParams();
  if (from) params.set("date_from", from);
  if (to) params.set("date_to", to);
  return request<any[]>(`/analytics/effective-tonnage?${params}`);
};
export const getExerciseProgress = (exerciseId: number) =>
  request<any[]>(`/analytics/exercise-progress/${exerciseId}`);
export const getMuscleGroupVolume = (from?: string, to?: string) => {
  const params = new URLSearchParams();
  if (from) params.set("date_from", from);
  if (to) params.set("date_to", to);
  return request<any[]>(`/analytics/muscle-group-volume?${params}`);
};
export const getCheckinCorrelation = () => request<any[]>("/analytics/checkin-correlation");

// Users
export const getUserInfo = () => request<any>("/users/me");
export const updateUserInfo = (data: { genetic_context?: string; allergies_and_risks?: string }) =>
  request<any>("/users/me", { method: "PATCH", body: JSON.stringify(data) });
