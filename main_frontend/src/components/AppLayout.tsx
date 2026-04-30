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
      <footer className="relative z-10 border-t border-border/40 bg-background/60 backdrop-blur-md">
        {/* Disclaimer */}
        <div className="border-b border-border/30 px-6 py-3 text-center text-xs text-muted-foreground">
          ⚠️ HealthIntel is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.
        </div>

        {/* Trademark */}
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-6 py-4 sm:flex-row">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} <span className="font-semibold gradient-text">HealthIntel</span>. All rights reserved.
          </p>

          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>Designed &amp; Developed by</span>
            <span className="font-bold gradient-text">Smita Mhatugade</span>

            {/* LinkedIn */}
            <a
              href="https://www.linkedin.com/in/smita-mhatugade-b85a29290/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Smita Mhatugade on LinkedIn"
              className="ml-2 flex h-7 w-7 items-center justify-center rounded-lg border border-border/50 bg-background/80 text-muted-foreground transition-all hover:border-primary/50 hover:bg-primary/10 hover:text-primary hover:scale-110"
            >
              {/* LinkedIn Icon */}
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
            </a>

            {/* GitHub */}
            <a
              href="https://github.com/Smita-Mhatugade"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Smita Mhatugade on GitHub"
              className="flex h-7 w-7 items-center justify-center rounded-lg border border-border/50 bg-background/80 text-muted-foreground transition-all hover:border-primary/50 hover:bg-primary/10 hover:text-primary hover:scale-110"
            >
              {/* GitHub Icon */}
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
              </svg>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
