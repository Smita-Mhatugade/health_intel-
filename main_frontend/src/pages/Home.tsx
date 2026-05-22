import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Activity, Brain, Eye, HeartPulse, Hospital, Stethoscope,
  ShieldCheck, ArrowRight, Zap, TrendingUp
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const ICONS: Record<string, any> = {
  heart_failure: HeartPulse,
  heart_disease: HeartPulse,
  parkinsons: Activity,
  alzheimer: Brain,
  eye_disease: Eye,
  symptom_prediction: Stethoscope,
};

// Muted clinical icon tints — no rainbow gradients
const MODULE_STYLES: Record<string, { bg: string; text: string; badge: string }> = {
  heart_failure:       { bg: "bg-rose-50 dark:bg-rose-950/30",     text: "text-rose-600 dark:text-rose-400",     badge: "bg-rose-50 text-rose-600 border-rose-200 dark:bg-rose-950/30 dark:text-rose-400 dark:border-rose-800" },
  heart_disease:       { bg: "bg-red-50 dark:bg-red-950/30",       text: "text-red-600 dark:text-red-400",       badge: "bg-red-50 text-red-600 border-red-200 dark:bg-red-950/30 dark:text-red-400 dark:border-red-800" },
  parkinsons:          { bg: "bg-amber-50 dark:bg-amber-950/30",   text: "text-amber-600 dark:text-amber-400",   badge: "bg-amber-50 text-amber-600 border-amber-200 dark:bg-amber-950/30 dark:text-amber-400 dark:border-amber-800" },
  alzheimer:           { bg: "bg-violet-50 dark:bg-violet-950/30", text: "text-violet-600 dark:text-violet-400", badge: "bg-violet-50 text-violet-600 border-violet-200 dark:bg-violet-950/30 dark:text-violet-400 dark:border-violet-800" },
  eye_disease:         { bg: "bg-sky-50 dark:bg-sky-950/30",       text: "text-sky-600 dark:text-sky-400",       badge: "bg-sky-50 text-sky-600 border-sky-200 dark:bg-sky-950/30 dark:text-sky-400 dark:border-sky-800" },
  symptom_prediction:  { bg: "bg-teal-50 dark:bg-teal-950/30",     text: "text-teal-600 dark:text-teal-400",     badge: "bg-teal-50 text-teal-600 border-teal-200 dark:bg-teal-950/30 dark:text-teal-400 dark:border-teal-800" },
};

const FALLBACK_STYLE = { bg: "bg-primary/5", text: "text-primary", badge: "bg-primary/5 text-primary border-primary/20" };

const FALLBACK = [
  { id: "heart_failure",      name: "Heart Failure",       description: "Predict mortality risk from 12 clinical parameters including ejection fraction and serum creatinine.", available: true },
  { id: "heart_disease",      name: "Heart Disease",       description: "Detect presence of coronary artery disease using ECG data, blood pressure, and cholesterol levels.", available: true },
  { id: "parkinsons",         name: "Parkinson's",         description: "Detect Parkinson's Disease from 22 vocal biomedical measurements with XGBoost ensemble.", available: true },
  { id: "alzheimer",          name: "Alzheimer's",         description: "Stage cognitive impairment from MRI and clinical data. Upload Excel or CSV file.", available: true },
  { id: "eye_disease",        name: "Eye Disease",         description: "Classify retinal images into Cataract, Diabetic Retinopathy, Glaucoma or Normal using VGG19.", available: true },
  { id: "symptom_prediction", name: "Symptom Prediction",  description: "Predict 41 possible diseases from reported symptoms using an RF + XGBoost + CatBoost ensemble.", available: true },
];

const STATS = [
  { label: "Diagnostic Models",  value: "6",    icon: Zap },
  { label: "Conditions Covered", value: "41+",  icon: TrendingUp },
  { label: "Hospital Finder",    value: "Fast", icon: Hospital },
];

export default function Home() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["disease-config"],
    queryFn: apiClient.diseaseConfig,
  });

  const list = (data && (data as any[]).length ? data : FALLBACK) as any[];

  return (
    <div className="mx-auto w-full max-w-full px-4 py-10 sm:px-6 lg:px-8">

      {/* ── Hero Section ──────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-hero p-8 text-white shadow-elegant md:p-14">

        <div className="relative grid items-center gap-10 md:grid-cols-2">
          {/* Left — copy */}
          <div>
            <div className="mb-5 inline-flex items-center gap-2 rounded-md border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium backdrop-blur-sm">
              <Stethoscope className="h-3.5 w-3.5" />
              Clinical Decision Support
            </div>
            <h1 className="text-balance text-4xl font-bold leading-tight md:text-5xl lg:text-6xl">
              Precision Health
              <br />
              <span className="text-teal-300">Analytics.</span>
            </h1>
            <p className="mt-5 max-w-lg text-base text-white/75 md:text-lg">
              Analyze clinical parameters, symptoms, and medical images. Get clear
              risk assessments and find nearby specialist hospitals — all in one place.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg"
                className="gap-2 rounded-lg bg-white text-primary hover:bg-white/90 font-semibold shadow-sm">
                <Link to="/analyze">
                  <Stethoscope className="h-4 w-4" />
                  Start Analysis
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline"
                className="gap-2 rounded-lg border-white/30 bg-white/10 text-white hover:bg-white/20">
                <Link to="/hospitals">
                  <Hospital className="h-4 w-4" />
                  Find Hospitals
                </Link>
              </Button>
            </div>
          </div>

          {/* Right — stats */}
          <div className="grid grid-cols-3 gap-4 md:justify-items-center">
            {STATS.map(({ label, value, icon: Icon }) => (
              <div key={label} className="flex flex-col items-center gap-2 rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/10">
                  <Icon className="h-5 w-5 text-white" />
                </div>
                <span className="text-3xl font-bold">{value}</span>
                <span className="text-xs text-white/60">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Module Grid ───────────────────────────────────────────── */}
      <section className="mt-14">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <h2 className="text-3xl font-bold text-foreground">Diagnostic Modules</h2>
            <p className="mt-1 text-sm text-muted-foreground">Select a diagnostic module to begin.</p>
          </div>
        </div>

        {isError && (
          <div className="mb-6 rounded-lg border border-warning/30 bg-warning/5 p-4 text-sm text-warning-foreground flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-warning shrink-0" />
            Backend offline — showing default modules. Start the FastAPI server at{" "}
            <code className="font-mono text-xs">localhost:8000</code>.
          </div>
        )}

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading
            ? Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-52 rounded-xl" />
              ))
            : list.map((d: any, idx: number) => {
                const id = d.id || d.category || d.name;
                const Icon = ICONS[id] || Stethoscope;
                const styles = MODULE_STYLES[id] || FALLBACK_STYLE;
                return (
                  <div
                    key={id}
                    className={cn(
                      "module-card group flex flex-col rounded-xl border border-border bg-card p-6 shadow-card",
                      `animate-fade-up stagger-${Math.min(idx + 1, 6)}`
                    )}
                  >
                    {/* Icon */}
                    <div className={cn(
                      "mb-4 flex h-12 w-12 items-center justify-center rounded-lg",
                      styles.bg, styles.text
                    )}>
                      <Icon className="h-6 w-6" />
                    </div>

                    {/* Content */}
                    <h3 className="text-lg font-bold">{d.name || id}</h3>
                    <p className="mt-2 flex-1 text-sm text-muted-foreground line-clamp-3">
                      {d.description || "Run analysis on this module."}
                    </p>

                    {/* Badge */}
                    <div className="mt-4 flex items-center justify-between">
                      <span className={cn("rounded-md border px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide", styles.badge)}>
                        {d.available !== false ? "Available" : "Unavailable"}
                      </span>
                      <Button asChild variant="ghost" size="sm"
                        className="gap-1 rounded-lg text-xs font-semibold text-primary hover:bg-primary/10 group-hover:translate-x-1 transition-transform">
                        <Link to={`/analyze?category=${id}`}>
                          Open <ArrowRight className="h-3.5 w-3.5" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                );
              })}
        </div>
      </section>

      {/* ── Disclaimer ────────────────────────────────────────────── */}
      <section className="mt-14 rounded-xl border border-border bg-card p-6 shadow-card">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-semibold">Important Disclaimer</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              HealthIntel is an experimental tool intended for informational and educational purposes only.
              It is <strong>not</strong> a substitute for professional medical advice, diagnosis, or treatment.
              Always consult a qualified healthcare provider for medical decisions.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
