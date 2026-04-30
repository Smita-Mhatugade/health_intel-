import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { apiClient, AnalysisResult } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Send, Sparkles, Bot, User, ShieldAlert } from "lucide-react";
import { parseUserMessage } from "@/utils/chatParser";
import { AnalysisForm, CATEGORY_LABELS } from "@/components/AnalysisForm";
import { PreviewCard } from "@/components/PreviewCard";
import { useStore } from "@/store/useStore";
import { toast } from "sonner";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const DEFAULT_CATEGORIES = Object.keys(CATEGORY_LABELS);

export default function Analyze() {
  const [params] = useSearchParams();
  const initialCat = params.get("category");

  const { data: diseases } = useQuery({
    queryKey: ["disease-config"],
    queryFn: apiClient.diseaseConfig,
  });

  const categoryOptions = useMemo(() => {
    const fromApi = (diseases ?? []).map((d: any) => d.id || d.category || d.name).filter(Boolean);
    const merged = Array.from(new Set([...fromApi, ...DEFAULT_CATEGORIES]));
    return merged;
  }, [diseases]);

  const [category, setCategory] = useState<string>(initialCat || "heart_failure");
  const [extractedParams, setExtractedParams] = useState<Record<string, any>>({});
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! Describe your symptoms or pick a module on the right. Example: \"I'm a 62 year old male, smoker, with chest pain and ejection fraction 30.\"",
    },
  ]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  const setCurrentResult = useStore((s) => s.setCurrentResult);
  const currentResult = useStore((s) => s.currentResult);
  const addHistory = useStore((s) => s.addHistory);
  const [savedId, setSavedId] = useState<string | null>(null);

  useEffect(() => {
    if (initialCat) setCategory(initialCat);
  }, [initialCat]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = () => {
    const text = input.trim();
    if (!text) return;
    const parsed = parseUserMessage(text, diseases ?? []);
    setMessages((m) => [
      ...m,
      { role: "user", content: text },
      {
        role: "assistant",
        content:
          (parsed.category
            ? `Detected category: **${CATEGORY_LABELS[parsed.category] ?? parsed.category}**. `
            : "I couldn't confidently detect a category — please pick one. ") +
          (Object.keys(parsed.parameters).length
            ? `Pre-filling parameters: ${Object.entries(parsed.parameters)
                .map(([k, v]) => `${k}=${v}`)
                .join(", ")}.`
            : "") +
          (parsed.symptoms.length ? ` Symptoms: ${parsed.symptoms.join(", ")}.` : ""),
      },
    ]);
    if (parsed.category && categoryOptions.includes(parsed.category)) {
      setCategory(parsed.category);
    }
    setExtractedParams({ ...parsed.parameters, symptoms: parsed.symptoms });
    setInput("");
  };

  const onResult = (r: AnalysisResult, cat: string) => {
    setCurrentResult({ ...r, diseaseCategory: cat });
    setSavedId(null);
    setMessages((m) => [
      ...m,
      {
        role: "assistant",
        content: `Result: ${r.prediction_label} (${r.confidence}% confidence). Severity: ${r.severity?.label}.`,
      },
    ]);
  };

  const handleSave = () => {
    if (!currentResult) return;
    const saved = addHistory({
      diseaseCategory: currentResult.diseaseCategory,
      prediction_label: currentResult.prediction_label,
      confidence: currentResult.confidence,
      severity: currentResult.severity,
      summary: currentResult.summary,
      details: currentResult.details,
      disclaimer: currentResult.disclaimer,
    });
    setSavedId(saved.id);
    toast.success("Saved to history");
  };

  return (
    <div className="mx-auto w-full max-w-7xl px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Analyze</h1>
        <p className="text-sm text-muted-foreground">
          Describe your situation in chat, then refine the inputs and run analysis.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_380px]">
        {/* Chat + form */}
        <div className="space-y-6">
          <Card className="shadow-card">
            <CardHeader className="border-b">
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-primary" />
                Chat with HealthIntel
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div ref={scrollRef} className="max-h-72 space-y-3 overflow-y-auto p-4">
                {messages.map((m, i) => (
                  <div
                    key={i}
                    className={`flex gap-2 ${m.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {m.role === "assistant" && (
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                        <Bot className="h-4 w-4" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                        m.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-foreground"
                      }`}
                    >
                      {m.content}
                    </div>
                    {m.role === "user" && (
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground">
                        <User className="h-4 w-4" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
              <div className="flex items-center gap-2 border-t p-3">
                <Input
                  placeholder="Describe symptoms or parameters..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && send()}
                />
                <Button onClick={send} size="icon" aria-label="Send">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-card">
            <CardHeader className="border-b">
              <CardTitle className="text-base">Inputs & analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="space-y-1.5">
                <Label>Disease module</Label>
                <Select value={category} onValueChange={setCategory}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categoryOptions.map((c) => (
                      <SelectItem key={c} value={c}>
                        {CATEGORY_LABELS[c] ?? c}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <AnalysisForm
                category={category}
                initialValues={extractedParams}
                onResult={onResult}
              />
            </CardContent>
          </Card>
        </div>

        {/* Preview */}
        <div className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <PreviewCard
            result={currentResult}
            onSave={currentResult ? handleSave : undefined}
            saved={!!savedId}
          />
          <Card className="border-warning/30 bg-warning/5">
            <CardContent className="flex items-start gap-2 p-4 text-xs text-foreground/90">
              <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
              <span>
                For informational purposes only. Always consult a licensed medical professional for
                diagnosis or treatment.
              </span>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
