import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Brain, Eye, HeartPulse, Hospital, Stethoscope, ShieldAlert, Code2 } from "lucide-react";

const STACK = [
  "React 18", "TypeScript", "Vite", "Tailwind CSS", "shadcn/ui",
  "TanStack Query", "Zustand", "React Router", "Leaflet / OpenStreetMap",
  "jsPDF", "FastAPI (backend)",
];

const MODULES = [
  { icon: HeartPulse, title: "Heart Failure / Heart Disease", desc: "Risk prediction from clinical features." },
  { icon: Activity, title: "Parkinson's", desc: "Detection from 22 vocal parameters." },
  { icon: Brain, title: "Alzheimer's", desc: "Classification from Excel data input." },
  { icon: Eye, title: "Eye Disease", desc: "Image-based ocular disease classification." },
  { icon: Stethoscope, title: "Symptom Prediction", desc: "Disease likelihood from selected symptoms." },
  { icon: Hospital, title: "Hospital Recommendations", desc: "Geo-located specialist hospital search." },
];

export default function About() {
  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">About HealthIntel</h1>
        <p className="mt-2 text-muted-foreground">
          A modern frontend for an AI-powered medical analysis backend.
        </p>
      </header>

      <Card className="mb-6 shadow-card">
        <CardHeader>
          <CardTitle className="text-base">What it does</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-foreground/90">
          <p>
            HealthIntel combines clinical data, symptoms, and medical imagery with machine
            learning models to produce explainable risk predictions and severity assessments. It
            also helps you find specialist hospitals near you.
          </p>
          <p>
            Analyses are saved locally to your device (browser localStorage) — nothing leaves
            unless you contact the backend or export a PDF.
          </p>
        </CardContent>
      </Card>

      <Card className="mb-6 shadow-card">
        <CardHeader>
          <CardTitle className="text-base">Modules</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {MODULES.map((m) => (
              <div key={m.title} className="flex items-start gap-3 rounded-lg border bg-card p-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-accent text-accent-foreground">
                  <m.icon className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold">{m.title}</h4>
                  <p className="text-xs text-muted-foreground">{m.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="mb-6 shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Code2 className="h-4 w-4" /> Tech stack
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {STACK.map((s) => (
              <Badge key={s} variant="secondary">{s}</Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-warning/40 bg-warning/5 shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <ShieldAlert className="h-4 w-4 text-warning" /> Medical disclaimer
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            HealthIntel is for <strong>informational and educational purposes only</strong>. It is
            not intended to be a substitute for professional medical advice, diagnosis, or
            treatment.
          </p>
          <p>
            Always seek the advice of a qualified healthcare provider with any questions you may
            have regarding a medical condition. Never disregard professional medical advice or
            delay seeking it because of something you read in this application.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
