import { ReactNode, useState } from "react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { Button } from "@/components/ui/button";
import { Moon, Sun, Settings } from "lucide-react";
import { useStore } from "@/store/useStore";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getApiBaseUrl, setApiBaseUrl } from "@/lib/api";
import { toast } from "sonner";

export function AppLayout({ children }: { children: ReactNode }) {
  const theme = useStore((s) => s.theme);
  const toggleTheme = useStore((s) => s.toggleTheme);
  const [apiUrl, setApiUrl] = useState(getApiBaseUrl());
  const [open, setOpen] = useState(false);

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-gradient-soft">
        <AppSidebar />

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 flex h-14 items-center justify-between gap-2 border-b border-border/60 bg-background/80 px-4 backdrop-blur-md">
            <div className="flex items-center gap-2">
              <SidebarTrigger />
              <div className="hidden text-sm text-muted-foreground sm:block">
                AI Medical Analysis Platform
              </div>
            </div>
            <div className="flex items-center gap-1">
              <Dialog open={open} onOpenChange={setOpen}>
                <DialogTrigger asChild>
                  <Button variant="ghost" size="icon" aria-label="Settings">
                    <Settings className="h-4 w-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Settings</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-2">
                    <Label htmlFor="api-url">Backend URL</Label>
                    <Input
                      id="api-url"
                      value={apiUrl}
                      onChange={(e) => setApiUrl(e.target.value)}
                      placeholder="http://localhost:8000"
                    />
                    <p className="text-xs text-muted-foreground">
                      Override the FastAPI backend URL. Stored locally.
                    </p>
                  </div>
                  <DialogFooter>
                    <Button
                      onClick={() => {
                        setApiBaseUrl(apiUrl.trim());
                        toast.success("Backend URL updated");
                        setOpen(false);
                      }}
                    >
                      Save
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                aria-label="Toggle theme"
              >
                {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>
            </div>
          </header>

          <main className="flex-1 animate-fade-in">{children}</main>

          <footer className="border-t border-border/60 bg-background/60 px-6 py-3 text-center text-xs text-muted-foreground">
            ⚠️ HealthIntel is for informational purposes only and not a substitute for professional
            medical advice, diagnosis, or treatment.
          </footer>
        </div>
      </div>
    </SidebarProvider>
  );
}
