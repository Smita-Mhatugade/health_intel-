import { create } from "zustand";
import type { AnalysisResult } from "@/lib/api";

export interface HistoryEntry {
  id: string;
  timestamp: string;
  diseaseCategory: string;
  prediction_label: string;
  confidence: number;
  severity: { label: string; color: string };
  summary: string;
  details: Record<string, any>;
  disclaimer?: string;
}

const HISTORY_KEY = "healthintel_history";
const THEME_KEY = "healthintel_theme";

function loadHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function persistHistory(items: HistoryEntry[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(items));
}

function loadTheme(): "light" | "dark" {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === "dark" || stored === "light") return stored;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

interface StoreState {
  theme: "light" | "dark";
  toggleTheme: () => void;
  setTheme: (t: "light" | "dark") => void;

  history: HistoryEntry[];
  addHistory: (entry: Omit<HistoryEntry, "id" | "timestamp">) => HistoryEntry;
  removeHistory: (id: string) => void;
  clearHistory: () => void;

  currentResult: (AnalysisResult & { diseaseCategory: string }) | null;
  setCurrentResult: (r: (AnalysisResult & { diseaseCategory: string }) | null) => void;
}

export const useStore = create<StoreState>((set, get) => ({
  theme: loadTheme(),
  toggleTheme: () => {
    const next = get().theme === "dark" ? "light" : "dark";
    localStorage.setItem(THEME_KEY, next);
    document.documentElement.classList.toggle("dark", next === "dark");
    set({ theme: next });
  },
  setTheme: (t) => {
    localStorage.setItem(THEME_KEY, t);
    document.documentElement.classList.toggle("dark", t === "dark");
    set({ theme: t });
  },

  history: loadHistory(),
  addHistory: (entry) => {
    const full: HistoryEntry = {
      ...entry,
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      timestamp: new Date().toISOString(),
    };
    const next = [full, ...get().history];
    persistHistory(next);
    set({ history: next });
    return full;
  },
  removeHistory: (id) => {
    const next = get().history.filter((h) => h.id !== id);
    persistHistory(next);
    set({ history: next });
  },
  clearHistory: () => {
    persistHistory([]);
    set({ history: [] });
  },

  currentResult: null,
  setCurrentResult: (r) => set({ currentResult: r }),
}));

// Initialize theme class on html
if (typeof document !== "undefined") {
  document.documentElement.classList.toggle("dark", loadTheme() === "dark");
}
