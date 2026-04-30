import { AnalysisResult } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Save, Eye, ShieldAlert } from "lucide-react";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";

interface Props {
  result: (AnalysisResult & { diseaseCategory?: string }) | null;
  onSave?: () => void;
  saved?: boolean;
}

export function PreviewCard({ result, onSave, saved }: Props) {
  const [open, setOpen] = useState(false);

  if (!result) {
    return (
      <Card className="border-dashed shadow-card">
        <CardHeader>
          <CardTitle className="text-base text-muted-foreground">No analysis yet</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Run an analysis from the chat panel. The prediction summary will appear here.
          </p>
        </CardContent>
      </Card>
    );
  }

  const sevColor = result.severity?.color || "hsl(var(--muted-foreground))";

  return (
    <Card className="overflow-hidden shadow-card">
      <div className="h-1.5 w-full" style={{ background: sevColor }} />
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              {result.diseaseCategory ?? "Result"}
            </p>
            <CardTitle className="truncate text-xl">{result.prediction_label}</CardTitle>
          </div>
          <Badge
            className="shrink-0 text-white"
            style={{ backgroundColor: sevColor }}
          >
            {result.severity?.label ?? "—"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="mb-1 flex items-center justify-between text-xs text-muted-foreground">
            <span>Confidence</span>
            <span className="font-semibold text-foreground">{result.confidence}%</span>
          </div>
          <Progress value={result.confidence} className="h-2" />
        </div>
        <p className="line-clamp-3 text-sm leading-relaxed text-foreground/90">
          {result.summary}
        </p>

        <div className="flex flex-wrap items-center gap-2">
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button size="sm" variant="default" className="gap-1.5">
                <Eye className="h-4 w-4" /> View Full Details
              </Button>
            </DialogTrigger>
            <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{result.prediction_label} — Full Report</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge className="text-white" style={{ backgroundColor: sevColor }}>
                    {result.severity?.label}
                  </Badge>
                  <Badge variant="outline">Confidence: {result.confidence}%</Badge>
                  {result.diseaseCategory && (
                    <Badge variant="secondary">{result.diseaseCategory}</Badge>
                  )}
                </div>
                <div>
                  <h4 className="mb-1 text-sm font-semibold">Summary</h4>
                  <p className="text-sm leading-relaxed text-foreground/90">{result.summary}</p>
                </div>
                <div>
                  <h4 className="mb-1 text-sm font-semibold">Model Details</h4>
                  <pre className="max-h-72 overflow-auto rounded-md bg-muted p-3 text-xs">
                    {JSON.stringify(result.details, null, 2)}
                  </pre>
                </div>
                <div className="flex items-start gap-2 rounded-md border border-warning/40 bg-warning/10 p-3 text-xs text-foreground">
                  <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
                  <span>{result.disclaimer}</span>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          {onSave && (
            <Button size="sm" variant="outline" onClick={onSave} disabled={saved} className="gap-1.5">
              <Save className="h-4 w-4" /> {saved ? "Saved" : "Save to History"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
