import { ReactNode, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Activity, Home, Stethoscope, Hospital, History, Info, Moon, Sun, Settings, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useStore } from "@/store/useStore";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getApiBaseUrl, setApiBaseUrl } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { title: "Home",      url: "/",          icon: Home },
  { title: "Analyze",   url: "/analyze",   icon: Stethoscope },
  { title: "Hospitals", url: "/hospitals", icon: Hospital },
  { title: "History",   url: "/history",   icon: History },
  { title: "About",     url: "/about",     icon: Info },
];

export function AppLayout({ children }: { children: ReactNode }) {
  const theme = useStore((s) => s.theme);
  const toggleTheme = useStore((s) => s.toggleTheme);
  const [apiUrl, setApiUrl] = useState(getApiBaseUrl());
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className={cn("flex min-h-screen flex-col bg-background bg-animated", theme)}>
      {/* Animated background layers are CSS ::before / ::after */}

      {/* ── Top Navigation Bar ─────────────────────────────────────── */}
      <header className="top-nav sticky top-0 z-50 w-full">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">

          {/* Logo */}
          <Link to="/" className="flex shrink-0 items-center gap-3 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-primary shadow-glow animate-pulse-glow transition-transform group-hover:scale-110">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col leading-none">
              <span className="text-base font-bold tracking-tight gradient-text">HealthIntel</span>
              <span className="text-[10px] text-muted-foreground hidden sm:block">AI Medical Insights</span>
            </div>
          </Link>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map(({ title, url, icon: Icon }) => (
              <NavLink
                key={url}
                to={url}
                end={url === "/"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-gradient-primary text-white shadow-soft"
                      : "text-muted-foreground hover:text-foreground hover:bg-accent/10"
                  )
                }
              >
                <Icon className="h-4 w-4" />
                {title}
              </NavLink>
            ))}
          </nav>

          {/* Right controls */}
          <div className="flex items-center gap-2">
            {/* Settings */}
            <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
              <DialogTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Settings"
                  className="rounded-xl hover:bg-accent/10 hover:text-primary">
                  <Settings className="h-4 w-4" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle className="gradient-text">Settings</DialogTitle>
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
                  <Button className="bg-gradient-primary text-white border-0"
                    onClick={() => { setApiBaseUrl(apiUrl.trim()); toast.success("Backend URL updated"); setSettingsOpen(false); }}>
                    Save
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label="Toggle theme"
              className="rounded-xl hover:bg-accent/10 hover:text-primary"
            >
              {theme === "dark"
                ? <Sun className="h-4 w-4 text-yellow-400" />
                : <Moon className="h-4 w-4" />}
            </Button>

            {/* Mobile hamburger */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden rounded-xl"
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Toggle menu"
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Nav Dropdown */}
        {mobileOpen && (
          <div className="md:hidden border-t border-border/40 bg-background/95 backdrop-blur-xl px-4 pb-4">
            <nav className="flex flex-col gap-1 pt-3">
              {NAV_ITEMS.map(({ title, url, icon: Icon }) => (
                <NavLink
                  key={url}
                  to={url}
                  end={url === "/"}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all",
                      isActive
                        ? "bg-gradient-primary text-white shadow-soft"
                        : "text-muted-foreground hover:text-foreground hover:bg-accent/10"
                    )
                  }
                >
                  <Icon className="h-4 w-4" />
                  {title}
                </NavLink>
              ))}
            </nav>
          </div>
        )}
      </header>

      {/* ── Page Content ───────────────────────────────────────────── */}
      <main className="relative z-10 flex-1 animate-fade-up">
        {children}
      </main>

      {/* ── Footer ─────────────────────────────────────────────────── */}
      <footer className="relative z-10 border-t border-border/40 bg-background/60 backdrop-blur-md px-6 py-4 text-center text-xs text-muted-foreground">
        ⚠️ HealthIntel is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.
      </footer>
    </div>
  );
}
