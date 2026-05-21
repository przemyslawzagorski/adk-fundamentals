import { NavLink } from "react-router-dom";
import { Github, ExternalLink } from "lucide-react";
import { Logo } from "./logo";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const links = [
  { to: "/", label: "Overview" },
  { to: "/studio", label: "Studio" },
  { to: "/audit", label: "Audit" },
  { to: "/analyst", label: "Analyst" },
  { to: "/knowledge", label: "Knowledge" },
  { to: "/history", label: "History" },
];

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-cnc-border/60 bg-cnc-bg/80 backdrop-blur-xl">
      <div className="container flex h-16 items-center justify-between gap-4">
        <Logo />
        <nav className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === "/"}
              className={({ isActive }) =>
                cn(
                  "rounded-lg px-4 py-2 text-sm font-semibold transition-colors",
                  isActive ? "text-white bg-cnc-electric/15" : "text-cnc-muted hover:text-cnc-ink hover:bg-cnc-surface/60",
                )
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-2">
          <Badge variant="cyan" className="hidden md:inline-flex">v0.2 · Concierge + AuditOps</Badge>
          <a
            href="http://localhost:8765/"
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-cnc-border bg-cnc-surface/40 px-3 text-xs font-semibold text-cnc-muted transition-colors hover:text-white hover:border-cnc-electric/60"
          >
            Platform Docs <ExternalLink className="h-3 w-3" />
          </a>
          <a
            href="https://github.com/augmentcode"
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-cnc-border bg-cnc-surface/40 text-cnc-muted transition-colors hover:text-white hover:border-cnc-electric/60"
            title="GitHub"
          >
            <Github className="h-4 w-4" />
          </a>
        </div>
      </div>
    </header>
  );
}
