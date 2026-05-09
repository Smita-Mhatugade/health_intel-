import { useState } from "react";
import { useStore, HistoryEntry } from "@/store/useStore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Trash2, FileDown, Eye, Inbox } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { exportHistoryToPDF } from "@/utils/exportPDF";
import { toast } from "sonner";

export default function History() {
  const history = useStore((s) => s.history);
  const removeHistory = useStore((s) => s.removeHistory);
  const clearHistory = useStore((s) => s.clearHistory);
  const [active, setActive] = useState<HistoryEntry | null>(null);

  const sorted = [...history].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">History</h1>
          <p className="text-sm text-muted-foreground">
            {history.length} saved {history.length === 1 ? "analysis" : "analyses"}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            disabled={history.length === 0}
            onClick={() => {
              exportHistoryToPDF(history);
              toast.success("PDF generated");
            }}
            className="gap-2"
          >
            <FileDown className="h-4 w-4" /> Export All to PDF
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" disabled={history.length === 0} className="gap-2">
                <Trash2 className="h-4 w-4" /> Clear All
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Clear all history?</AlertDialogTitle>
                <AlertDialogDescription>
                  This permanently removes all saved analyses from this device.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={() => {
                    clearHistory();
                    toast.success("History cleared");
                  }}
                >
                  Clear
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      {sorted.length === 0 ? (
        <Card className="shadow-card">
          <CardContent className="flex flex-col items-center justify-center gap-3 py-16 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
              <Inbox className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold">No analyses yet</h3>
            <p className="max-w-sm text-sm text-muted-foreground">
              Run an analysis and click <em>Save to History</em> to keep a record here.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {sorted.map((entry) => {
            const sev = entry.severity?.color || "hsl(var(--muted-foreground))";
            return (
              <Card key={entry.id} className="overflow-hidden shadow-card">
                <div className="h-1 w-full" style={{ background: sev }} />
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">
                        {entry.diseaseCategory}
                      </p>
                      <CardTitle className="truncate text-lg">{entry.prediction_label}</CardTitle>
                    </div>
                    <Badge className="text-white" style={{ backgroundColor: sev }}>
                      {entry.severity?.label}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{new Date(entry.timestamp).toLocaleString()}</span>
                    <span>Confidence: {entry.confidence}%</span>
                  </div>
                  <p className="line-clamp-2 text-sm">{entry.summary}</p>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => setActive(entry)} className="gap-1.5">
                      <Eye className="h-3.5 w-3.5" /> View Details
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        removeHistory(entry.id);
                        toast.success("Removed");
                      }}
                      className="gap-1.5 text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-3.5 w-3.5" /> Delete
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <Dialog open={!!active} onOpenChange={(o) => !o && setActive(null)}>
        <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
          {active && (
            <>
              <DialogHeader>
                <DialogTitle>{active.prediction_label}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge className="text-white" style={{ backgroundColor: active.severity?.color }}>
                    {active.severity?.label}
                  </Badge>
                  <Badge variant="outline">Confidence: {active.confidence}%</Badge>
                  <Badge variant="secondary">{active.diseaseCategory}</Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(active.timestamp).toLocaleString()}
                  </span>
                </div>
                <div>
                  <h4 className="mb-1 text-sm font-semibold">Summary</h4>
                  <p className="text-sm leading-relaxed text-foreground/90">{active.summary}</p>
                </div>
                <div>
                  <h4 className="mb-1 text-sm font-semibold">Model Details</h4>
                  <pre className="max-h-72 overflow-auto rounded-md bg-muted p-3 text-xs">
                    {JSON.stringify(active.details, null, 2)}
                  </pre>
                </div>
                {active.disclaimer && (
                  <p className="rounded-md border border-warning/40 bg-warning/10 p-3 text-xs">
                    {active.disclaimer}
                  </p>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
