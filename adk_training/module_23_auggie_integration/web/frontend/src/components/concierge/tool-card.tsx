import { motion } from "framer-motion";
import { ArrowRight, Clock, Lock } from "lucide-react";
import { DynamicIcon } from "./dynamic-icon";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { ToolMeta } from "@/api/client";

const CATEGORY_COLORS: Record<string, string> = {
  general: "from-cnc-electric/20 to-cnc-azure/20 border-cnc-electric/30",
  review: "from-violet-500/20 to-cnc-azure/20 border-violet-500/30",
  analysis: "from-cnc-cyan/20 to-cnc-electric/20 border-cnc-cyan/30",
  generate: "from-emerald-500/20 to-cnc-cyan/20 border-emerald-500/30",
  refactor: "from-amber-500/20 to-orange-500/20 border-amber-500/30",
  security: "from-cnc-rose/20 to-pink-500/20 border-cnc-rose/30",
};

const CATEGORY_LABELS: Record<string, string> = {
  general: "General",
  review: "Review",
  analysis: "Analysis",
  generate: "Generate",
  refactor: "Refactor",
  security: "Security",
};

interface ToolCardProps {
  tool: ToolMeta;
  locked?: boolean;
  onClick: () => void;
}

export function ToolCard({ tool, locked, onClick }: ToolCardProps) {
  return (
    <motion.button
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={!locked ? { y: -4, scale: 1.02 } : {}}
      transition={{ duration: 0.4, ease: [0.2, 0.8, 0.2, 1] }}
      onClick={!locked ? onClick : undefined}
      disabled={locked}
      className={cn(
        "group relative overflow-hidden rounded-2xl border bg-cnc-surface/60 p-5 text-left transition-all duration-300",
        "backdrop-blur-sm",
        locked && "cursor-not-allowed opacity-60 grayscale",
        !locked && "hover:bg-cnc-surface hover:border-cnc-electric/60 hover:shadow-glow cursor-pointer",
      )}
    >
      {/* Gradient background */}
      <div className={cn(
        "absolute inset-0 -z-0 bg-gradient-to-br opacity-30 transition-opacity",
        CATEGORY_COLORS[tool.category] ?? CATEGORY_COLORS.general,
        !locked && "group-hover:opacity-60",
      )} />

      {/* Shine effect on hover */}
      {!locked && (
        <div className="absolute inset-0 -z-0 bg-shine bg-[length:200%_100%] opacity-0 transition-opacity duration-700 group-hover:animate-shimmer group-hover:opacity-100" />
      )}

      {/* Lock overlay */}
      {locked && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-cnc-bg/40 backdrop-blur-[2px]">
          <Lock className="h-8 w-8 text-cnc-muted" />
        </div>
      )}

      <div className="relative z-[1] flex flex-col gap-3">
        {/* Icon + category */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cnc-bg/70 ring-1 ring-cnc-border group-hover:ring-cnc-electric/60 transition">
            <DynamicIcon name={tool.icon} size={24} className="text-cnc-electric2 group-hover:text-cnc-cyan transition-colors" />
          </div>
          <Badge variant="outline" className="text-[9px] uppercase tracking-wider">
            {CATEGORY_LABELS[tool.category] ?? tool.category}
          </Badge>
        </div>

        {/* Name + tagline */}
        <div className="space-y-1">
          <h3 className="text-base font-bold text-white group-hover:text-gradient-azure transition-all">
            {tool.name}
          </h3>
          <p className="line-clamp-2 text-xs text-cnc-muted">{tool.tagline}</p>
        </div>

        {/* Footer */}
        <div className="mt-1 flex items-center justify-between text-[11px]">
          <span className="inline-flex items-center gap-1 font-mono text-cnc-muted">
            <Clock className="h-3 w-3" />
            ~{tool.estimated_seconds}s
          </span>
          <span className="inline-flex items-center gap-1 font-bold text-cnc-electric2 opacity-0 transition-opacity group-hover:opacity-100">
            Run <ArrowRight className="h-3.5 w-3.5" />
          </span>
        </div>
      </div>
    </motion.button>
  );
}
