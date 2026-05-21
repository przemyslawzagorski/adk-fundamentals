import { Link } from "react-router-dom";
import { Hexagon } from "lucide-react";
import { cn } from "@/lib/utils";

export function Logo({ className, compact = false }: { className?: string; compact?: boolean }) {
  return (
    <Link to="/" className={cn("group inline-flex items-center gap-2.5", className)}>
      <span className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-azure-grad shadow-glow-sm transition-transform group-hover:scale-110">
        <Hexagon className="h-5 w-5 text-white" strokeWidth={2.5} />
        <span className="absolute inset-0 rounded-xl ring-1 ring-white/20" />
      </span>
      {!compact && (
        <span className="flex flex-col leading-tight">
          <span className="text-lg font-extrabold tracking-tight text-gradient-azure">ADK Platform</span>
          <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-cnc-muted">concierge · auditops</span>
        </span>
      )}
    </Link>
  );
}
