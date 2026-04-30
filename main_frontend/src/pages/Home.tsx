import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Activity, Brain, Eye, HeartPulse, Hospital, Stethoscope, Sparkles, ShieldCheck } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

const ICONS: Record<string, any> = {
  heart_failure: HeartPulse,
  heart_disease: HeartPulse,
  parkinsons: Activity,
  alzheimer: Brain,
  eye_disease: Eye,
  symptom_prediction: Stethoscope,
};

const FALLBACK = [
  { id: "heart_failure", name: "Heart Failure", description: "Risk prediction from clinical parameters", available: true },
  { id: "heart_disease", name: "Heart Disease", description: "13 clinical features-based risk", available: true },
  { id: "parkinsons", name: "Parkinson's", description: "Vocal parameter analysis", available: true },
  { id: "alzheimer", name: "Alzheimer's", description: "Detection from Excel input", available: true },
  { id: "eye_disease", name: "Eye Disease", description: "Image classification", available: true },
  { id: "symptom_prediction", name: "Symptom Prediction", description: "Disease from symptoms", available: true },
];

export default function Home() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["disease-config"],
    queryFn: apiClient.diseaseConfig,
  });

  const list = (data && data.length ? data : FALLBACK) as any[];

  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-10">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-hero p-10 text-primary-foreground shadow-elegant">
        <div className="absolute -right-20 -top-20 h-72 w-72 rounded-full bg-primary-glow/30 blur-3xl" />
        <div className="absolute -bottom-24 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-white/10 blur-3xl" />
        <div className="relative max-w-2xl">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs backdrop-blur">
            <Sparkles className="h-3.5 w-3.5" />
            AI-powered medical insight
          </div>
          <h1 className="text-balance text-4xl font-bold leading-tight md:text-5xl">
            HealthIntel — your AI-assisted second opinion.
          </h1>
          <p className="mt-4 text-base text-white/80 md:text-lg">
            Analyze clinical parameters, symptoms, and medical images. Get clear risk
            assessments and find nearby specialist hospitals — all in one place.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button asChild size="lg" variant="secondary" className="gap-2">
              <Link to="/analyze">
                <Stethoscope className="h-4 w-4" />
                Start Analysis
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="gap-2 border-white/30 bg-white/10 text-white hover:bg-white/20 hover:text-white">
              <Link to="/hospitals">
                <Hospital className="h-4 w-4" />
                Find Hospitals
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Disease modules */}
      <section className="mt-12">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <h2 className="text-2xl font-bold">Available analyses</h2>
            <p className="text-sm text-muted-foreground">Pick a module to begin.</p>
          </div>
        </div>

        {isError && (
          <p className="mb-4 rounded-md border border-warning/40 bg-warning/10 p-3 text-sm">
            Backend offline — showing default modules. Start the FastAPI server at{" "}
            <code className="font-mono">localhost:8000</code>.
          </p>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {isLoading
            ? Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-44 rounded-xl" />
              ))
            : list.map((d: any) => {
                const id = d.id || d.category || d.name;
                const Icon = ICONS[id] || Stethoscope;
                return (
                  <Card key={id} className="group relative overflow-hidden shadow-card transition-all hover:-translate-y-0.5 hover:shadow-elegant">
                    <div className="absolute inset-x-0 top-0 h-1 bg-gradient-primary opacity-0 transition-opacity group-hover:opacity-100" />
                    <CardHeader>
                      <div className="mb-2 flex h-11 w-11 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                        <Icon className="h-5 w-5" />
                      </div>
                      <CardTitle className="text-lg">{d.name || id}</CardTitle>
                      <CardDescription className="line-clamp-2">
                        {d.description || "Run AI analysis on this module."}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button asChild variant="outline" className="w-full">
                        <Link to={`/analyze?category=${id}`}>Open</Link>
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
        </div>
      </section>

      {/* Disclaimer card */}
      <section className="mt-12 rounded-2xl border bg-card p-6 shadow-card">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-0.5 h-5 w-5 text-primary" />
          <div>
            <h3 className="font-semibold">Important disclaimer</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              HealthIntel is an experimental AI tool intended for informational and educational
              purposes only. It is <strong>not</strong> a substitute for professional medical
              advice, diagnosis, or treatment. Always consult a qualified healthcare provider for
              medical decisions.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
