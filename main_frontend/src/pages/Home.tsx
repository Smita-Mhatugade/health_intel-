import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Activity, Brain, Eye, HeartPulse, Hospital, Stethoscope,
  Sparkles, ShieldCheck, ArrowRight, Zap, TrendingUp
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

// Each card gets its own unique colour gradient
const MODULE_COLORS: Record<string, { gradient: string; glow: string; badge: string }> = {
  heart_failure:       { gradient: "from-red-500 to-pink-600",    glow: "shadow-red-500/30",   badge: "bg-red-500/10 text-red-500 border-red-500/20" },
  heart_disease:       { gradient: "from-rose-500 to-orange-500", glow: "shadow-rose-500/30",  badge: "bg-rose-500/10 text-rose-500 border-rose-500/20" },
  parkinsons:          { gradient: "from-amber-500 to-yellow-400",glow: "shadow-amber-500/30", badge: "bg-amber-500/10 text-amber-600 border-amber-500/20" },
  alzheimer:           { gradient: "from-violet-600 to-purple-700",glow: "shadow-violet-500/30",badge: "bg-violet-500/10 text-violet-600 border-violet-500/20" },
  eye_disease:         { gradient: "from-cyan-500 to-blue-600",   glow: "shadow-cyan-500/30",  badge: "bg-cyan-500/10 text-cyan-600 border-cyan-500/20" },
  symptom_prediction:  { gradient: "from-emerald-500 to-teal-600",glow: "shadow-emerald-500/30",badge: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20" },
};

const FALLBACK = [
  { id: "heart_failure",      name: "Heart Failure",       description: "Predict mortality risk from 12 clinical parameters including ejection fraction and serum creatinine.", available: true },
  { id: "heart_disease",      name: "Heart Disease",       description: "Detect presence of coronary artery disease using ECG data, blood pressure, and cholesterol levels.", available: true },
  { id: "parkinsons",         name: "Parkinson's",         description: "Detect Parkinson's Disease from 22 vocal biomedical measurements with XGBoost ensemble.", available: true },
  { id: "alzheimer",          name: "Alzheimer's",         description: "Stage cognitive impairment from MRI and clinical data. Upload Excel or CSV file.", available: true },
  { id: "eye_disease",        name: "Eye Disease",         description: "Classify retinal images into Cataract, Diabetic Retinopathy, Glaucoma or Normal using VGG19.", available: true },
  { id: "symptom_prediction", name: "Symptom Prediction",  description: "Predict 41 possible diseases from reported symptoms using an RF + XGBoost + CatBoost ensemble.", available: true },
];

const STATS = [
  { label: "AI Models",       value: "6",    icon: Zap },
  { label: "Conditions",      value: "41+",  icon: TrendingUp },
  { label: "Hospitals Found", value: "Fast", icon: Hospital },
];

export default function Home() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["disease-config"],
    queryFn: apiClient.diseaseConfig,
  });

  const list = (data && (data as any[]).length ? data : FALLBACK) as any[];

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8">

      {/* ── Hero Section ──────────────────────────────────────────── */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-hero p-8 text-white shadow-elegant md:p-14">
        {/* Decorative orbs */}
        <div className="pointer-events-none absolute -right-24 -top-24 h-80 w-80 rounded-full bg-white/5 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 left-1/3 h-64 w-64 rounded-full bg-purple-300/10 blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 right-1/4 h-40 w-40 rounded-full bg-pink-300/10 blur-2xl" />

        <div className="relative grid items-center gap-10 md:grid-cols-2">
          {/* Left — copy */}
          <div>
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-xs font-medium backdrop-blur-sm">
              <Sparkles className="h-3.5 w-3.5 text-yellow-300" />
              AI-powered medical insight platform
            </div>
            <h1 className="text-balance text-4xl font-bold leading-tight md:text-5xl lg:text-6xl">
              Your AI-assisted
              <br />
              <span className="text-yellow-300">second opinion.</span>
            </h1>
            <p className="mt-5 max-w-lg text-base text-white/75 md:text-lg">
              Analyze clinical parameters, symptoms, and medical images. Get clear
              risk assessments and find nearby specialist hospitals — all in one place.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg"
                className="gap-2 rounded-xl bg-white text-violet-700 hover:bg-white/90 font-semibold shadow-glow">
                <Link to="/analyze">
                  <Stethoscope className="h-4 w-4" />
                  Start Analysis
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline"
                className="gap-2 rounded-xl border-white/30 bg-white/10 text-white hover:bg-white/20">
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
              <div key={label} className="flex flex-col items-center gap-2 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
                  <Icon className="h-5 w-5 text-yellow-300" />
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
            <h2 className="text-3xl font-bold gradient-text">Diagnostic Modules</h2>
            <p className="mt-1 text-sm text-muted-foreground">Choose a module to begin your AI-powered analysis.</p>
          </div>
        </div>

        {isError && (
          <div className="mb-6 rounded-xl border border-warning/30 bg-warning/5 p-4 text-sm text-warning-foreground">
            ⚠️ Backend offline — showing default modules. Start the FastAPI server at{" "}
            <code className="font-mono text-xs">localhost:8000</code>.
          </div>
        )}

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading
            ? Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-52 rounded-2xl" />
              ))
            : list.map((d: any, idx: number) => {
                const id = d.id || d.category || d.name;
                const Icon = ICONS[id] || Stethoscope;
                const colors = MODULE_COLORS[id] || {
                  gradient: "from-violet-600 to-indigo-600",
                  glow: "shadow-violet-500/30",
                  badge: "bg-violet-500/10 text-violet-600 border-violet-500/20",
                };
                return (
                  <div
                    key={id}
                    className={cn(
                      "module-card glass-card group flex flex-col rounded-2xl p-6",
                      `animate-fade-up stagger-${Math.min(idx + 1, 6)}`
                    )}
                  >
                    {/* Icon */}
                    <div className={cn(
                      "mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br text-white shadow-lg",
                      colors.gradient, colors.glow
                    )}>
                      <Icon className="h-6 w-6" />
                    </div>

                    {/* Content */}
                    <h3 className="text-lg font-bold">{d.name || id}</h3>
                    <p className="mt-2 flex-1 text-sm text-muted-foreground line-clamp-3">
                      {d.description || "Run AI analysis on this module."}
                    </p>

                    {/* Badge */}
                    <div className="mt-4 flex items-center justify-between">
                      <span className={cn("rounded-full border px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide", colors.badge)}>
                        {d.available !== false ? "Available" : "Unavailable"}
                      </span>
                      <Button asChild variant="ghost" size="sm"
                        className="gap-1 rounded-xl text-xs font-semibold text-primary hover:bg-primary/10 group-hover:translate-x-1 transition-transform">
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
      <section className="mt-14 rounded-2xl border border-border/40 bg-card/50 p-6 backdrop-blur-sm shadow-card">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-primary">
            <ShieldCheck className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold">Important Disclaimer</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              HealthIntel is an experimental AI tool intended for informational and educational purposes only.
              It is <strong>not</strong> a substitute for professional medical advice, diagnosis, or treatment.
              Always consult a qualified healthcare provider for medical decisions.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
