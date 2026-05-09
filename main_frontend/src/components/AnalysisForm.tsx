import { useEffect, useMemo, useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { apiClient, AnalysisResult } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Loader2, Upload, X } from "lucide-react";
import { toast } from "sonner";

export const CATEGORY_LABELS: Record<string, string> = {
  heart_failure: "Heart Failure",
  heart_disease: "Heart Disease",
  parkinsons: "Parkinson's",
  alzheimer: "Alzheimer's",
  eye_disease: "Eye Disease",
  symptom_prediction: "Symptom-Based Prediction",
};

export const HEART_FAILURE_FIELDS = [
  { key: "age", label: "Age", default: 60, type: "number" },
  { key: "anaemia", label: "Anaemia", default: 0, type: "switch" },
  { key: "creatinine_phosphokinase", label: "Creatinine Phosphokinase", default: 250, type: "number" },
  { key: "diabetes", label: "Diabetes", default: 0, type: "switch" },
  { key: "ejection_fraction", label: "Ejection Fraction (%)", default: 38, type: "number" },
  { key: "high_blood_pressure", label: "High Blood Pressure", default: 0, type: "switch" },
  { key: "platelets", label: "Platelets", default: 250000, type: "number" },
  { key: "serum_creatinine", label: "Serum Creatinine", default: 1.2, type: "number", step: 0.1 },
  { key: "serum_sodium", label: "Serum Sodium", default: 137, type: "number" },
  { key: "sex", label: "Sex (1=Male, 0=Female)", default: 1, type: "switch" },
  { key: "smoking", label: "Smoking", default: 0, type: "switch" },
  { key: "time", label: "Follow-up (days)", default: 130, type: "number" },
];

export const HEART_DISEASE_FIELDS = [
  { key: "age", label: "Age", default: 55, type: "number" },
  { key: "sex", label: "Sex (1=Male)", default: 1, type: "switch" },
  { key: "cp", label: "Chest Pain Type (0-3)", default: 0, type: "number" },
  { key: "trestbps", label: "Resting BP", default: 130, type: "number" },
  { key: "chol", label: "Cholesterol", default: 240, type: "number" },
  { key: "fbs", label: "Fasting Blood Sugar > 120", default: 0, type: "switch" },
  { key: "restecg", label: "Resting ECG (0-2)", default: 0, type: "number" },
  { key: "thalach", label: "Max Heart Rate", default: 150, type: "number" },
  { key: "exang", label: "Exercise Angina", default: 0, type: "switch" },
  { key: "oldpeak", label: "ST Depression", default: 1.0, type: "number", step: 0.1 },
  { key: "slope", label: "Slope (0-2)", default: 1, type: "number" },
  { key: "ca", label: "Major Vessels (0-4)", default: 0, type: "number" },
  { key: "thal", label: "Thal (0-3)", default: 2, type: "number" },
];

export const PARKINSONS_FIELDS = [
  "MDVP:Fo(Hz)","MDVP:Fhi(Hz)","MDVP:Flo(Hz)","MDVP:Jitter(%)","MDVP:Jitter(Abs)",
  "MDVP:RAP","MDVP:PPQ","Jitter:DDP","MDVP:Shimmer","MDVP:Shimmer(dB)",
  "Shimmer:APQ3","Shimmer:APQ5","MDVP:APQ","Shimmer:DDA","NHR","HNR",
  "RPDE","DFA","spread1","spread2","D2","PPE",
].map((k) => ({ key: k, label: k, default: 0, type: "number", step: 0.0001 }));

interface Props {
  category: string;
  initialValues?: Record<string, any>;
  onResult: (r: AnalysisResult, category: string) => void;
}

export function AnalysisForm({ category, initialValues, onResult }: Props) {
  const [values, setValues] = useState<Record<string, any>>({});
  const [file, setFile] = useState<File | null>(null);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const { data: symptomsList = [] } = useQuery({
    queryKey: ["symptoms"],
    queryFn: apiClient.symptoms,
    enabled: category === "symptom_prediction",
  });

  const fields = useMemo(() => {
    if (category === "heart_failure") return HEART_FAILURE_FIELDS;
    if (category === "heart_disease") return HEART_DISEASE_FIELDS;
    if (category === "parkinsons") return PARKINSONS_FIELDS;
    return [];
  }, [category]);

  useEffect(() => {
    const next: Record<string, any> = {};
    fields.forEach((f) => {
      next[f.key] = initialValues?.[f.key] ?? f.default;
    });
    setValues(next);
    setFile(null);
    if (initialValues?.symptoms?.length) setSelectedSymptoms(initialValues.symptoms);
  }, [category, fields, initialValues]);

  const setField = (k: string, v: any) => setValues((s) => ({ ...s, [k]: v }));

  const submit = async () => {
    setLoading(true);
    try {
      let result: AnalysisResult;
      if (category === "heart_failure") {
        result = await apiClient.analyzeHeartFailure(numberify(values));
      } else if (category === "heart_disease") {
        result = await apiClient.analyzeHeartDisease(numberify(values));
      } else if (category === "parkinsons") {
        result = await apiClient.analyzeParkinsons(numberify(values));
      } else if (category === "symptom_prediction") {
        if (selectedSymptoms.length === 0) {
          toast.error("Pick at least one symptom");
          return;
        }
        result = await apiClient.analyzeSymptoms(selectedSymptoms);
      } else if (category === "alzheimer") {
        if (!file) return toast.error("Upload an Excel file");
        result = await apiClient.analyzeAlzheimer(file);
      } else if (category === "eye_disease") {
        if (!file) return toast.error("Upload an eye image");
        result = await apiClient.analyzeEyeDisease(file);
      } else {
        toast.error("Unsupported category");
        return;
      }
      onResult(result, category);
      toast.success("Analysis complete");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || e?.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const isFile = category === "alzheimer" || category === "eye_disease";
  const isSymptoms = category === "symptom_prediction";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="secondary">{CATEGORY_LABELS[category] ?? category}</Badge>
        <span className="text-xs text-muted-foreground">
          Fill in the parameters and run analysis.
        </span>
      </div>

      {isFile && (
        <div className="rounded-lg border border-dashed border-border p-6 text-center">
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept={category === "alzheimer" ? ".xlsx,.xls,.csv" : "image/*"}
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <label
            htmlFor="file-upload"
            className="flex cursor-pointer flex-col items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
          >
            <Upload className="h-6 w-6" />
            {file ? (
              <span className="font-medium text-foreground">{file.name}</span>
            ) : (
              <span>
                Click to upload {category === "alzheimer" ? "Excel file" : "eye image"}
              </span>
            )}
          </label>
        </div>
      )}

      {isSymptoms && (
        <div className="space-y-2">
          <Label>Select symptoms</Label>
          <div className="flex max-h-56 flex-wrap gap-1.5 overflow-y-auto rounded-md border bg-muted/30 p-3">
            {(symptomsList as string[]).length === 0 && (
              <p className="text-xs text-muted-foreground">
                No symptoms loaded — backend may be offline. You can still type symptoms below.
              </p>
            )}
            {(symptomsList as string[]).map((s) => {
              const active = selectedSymptoms.includes(s);
              return (
                <button
                  key={s}
                  type="button"
                  onClick={() =>
                    setSelectedSymptoms((cur) =>
                      cur.includes(s) ? cur.filter((x) => x !== s) : [...cur, s]
                    )
                  }
                  className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                    active
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-background hover:bg-accent"
                  }`}
                >
                  {s}
                </button>
              );
            })}
          </div>
          {selectedSymptoms.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {selectedSymptoms.map((s) => (
                <Badge key={s} variant="default" className="gap-1">
                  {s}
                  <button onClick={() => setSelectedSymptoms((cur) => cur.filter((x) => x !== s))}>
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          )}
        </div>
      )}

      {!isFile && !isSymptoms && fields.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {fields.map((f: any) => (
            <div key={f.key} className="space-y-1.5">
              <Label htmlFor={f.key} className="text-xs">{f.label}</Label>
              {f.type === "switch" ? (
                <div className="flex h-10 items-center gap-2 rounded-md border bg-background px-3">
                  <Switch
                    id={f.key}
                    checked={Number(values[f.key]) === 1}
                    onCheckedChange={(c) => setField(f.key, c ? 1 : 0)}
                  />
                  <span className="text-xs text-muted-foreground">
                    {Number(values[f.key]) === 1 ? "Yes" : "No"}
                  </span>
                </div>
              ) : (
                <Input
                  id={f.key}
                  type="number"
                  step={f.step ?? 1}
                  value={values[f.key] ?? ""}
                  onChange={(e) => setField(f.key, e.target.value)}
                />
              )}
            </div>
          ))}
        </div>
      )}

      <Button onClick={submit} disabled={loading} className="w-full" size="lg">
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        Run Analysis
      </Button>
    </div>
  );
}

function numberify(o: Record<string, any>) {
  const out: Record<string, number> = {};
  Object.entries(o).forEach(([k, v]) => {
    out[k] = typeof v === "number" ? v : Number(v);
  });
  return out;
}
