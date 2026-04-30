import axios, { AxiosInstance } from "axios";

const STORAGE_KEY = "healthintel_api_url";

export function getApiBaseUrl(): string {
  const stored = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
  if (stored) return stored;
  // Vite env (preferred) with CRA-style fallback name supported via define-on-window
  // @ts-ignore
  const viteEnv = import.meta.env?.VITE_API_URL as string | undefined;
  // @ts-ignore
  const craEnv = import.meta.env?.REACT_APP_API_URL as string | undefined;
  return viteEnv || craEnv || "http://localhost:8000";
}

export function setApiBaseUrl(url: string) {
  localStorage.setItem(STORAGE_KEY, url);
  api.defaults.baseURL = url;
}

export const api: AxiosInstance = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 60_000,
});

export interface DiseaseConfig {
  id: string;
  name: string;
  icon?: string;
  description?: string;
  available?: boolean;
  category?: string;
}

export interface AnalysisResult {
  prediction_label: string;
  confidence: number;
  severity: { label: string; color: string };
  summary: string;
  details: Record<string, any>;
  disclaimer: string;
}

export interface Hospital {
  name: string;
  distance_km?: number;
  distance?: number;
  address?: string;
  latitude: number;
  longitude: number;
  phone?: string;
  rating?: number;
  specialties?: string[];
}

export const apiClient = {
  status: () => api.get("/api/status").then((r) => r.data),
  diseaseConfig: () =>
    api.get<DiseaseConfig[] | { diseases: DiseaseConfig[] }>("/api/disease-config").then((r) => {
      const data: any = r.data;
      return Array.isArray(data) ? data : data.diseases ?? [];
    }),
  symptoms: () =>
    api.get<string[] | { symptoms: string[] }>("/api/symptoms").then((r) => {
      const data: any = r.data;
      return Array.isArray(data) ? data : data.symptoms ?? [];
    }),
  analyzeHeartFailure: (payload: Record<string, number>) =>
    api.post<AnalysisResult>("/api/analyze/heart-failure", payload).then((r) => r.data),
  analyzeHeartDisease: (payload: Record<string, number>) =>
    api.post<AnalysisResult>("/api/analyze/heart-disease", payload).then((r) => r.data),
  analyzeParkinsons: (payload: Record<string, number>) =>
    api.post<AnalysisResult>("/api/analyze/parkinsons", payload).then((r) => r.data),
  analyzeSymptoms: (symptoms: string[]) =>
    api.post<AnalysisResult>("/api/analyze/symptoms", { symptoms }).then((r) => r.data),
  analyzeAlzheimer: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api
      .post<AnalysisResult>("/api/analyze/alzheimer", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
  analyzeEyeDisease: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api
      .post<AnalysisResult>("/api/analyze/eye-disease", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
  recommendHospitals: (payload: {
    latitude: number;
    longitude: number;
    disease_category: string;
    radius_km: number;
  }) =>
    api.post<Hospital[] | { hospitals: Hospital[] }>("/api/recommend-hospitals", payload).then((r) => {
      const data: any = r.data;
      return (Array.isArray(data) ? data : data.hospitals ?? []) as Hospital[];
    }),
};
