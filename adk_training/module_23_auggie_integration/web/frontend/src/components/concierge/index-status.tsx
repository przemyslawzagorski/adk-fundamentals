import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Database, Loader2, CheckCircle2, AlertCircle, Play, RotateCcw, FolderOpen, Clock, Zap, ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useIndexWarmup, type UseIndexWarmup } from "@/hooks/use-index-warmup";
import { fmtSeconds, cn } from "@/lib/utils";

interface IndexStatusCardProps {
  defaultWorkspace?: string;
  onReady?: () => void;
  className?: string;
  warmup?: UseIndexWarmup;
}

export function IndexStatusCard({ defaultWorkspace, onReady, className, warmup }: IndexStatusCardProps) {
  const localWarmup = useIndexWarmup();
  const { state, events, isRunning, start, cancel } = warmup ?? localWarmup;
  const [workspace, setWorkspace] = React.useState(defaultWorkspace ?? "");
  const [advanced, setAdvanced] = React.useState(false);

  React.useEffect(() => {
    if (defaultWorkspace && !workspace) setWorkspace(defaultWorkspace);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultWorkspace]);

  React.useEffect(() => {
    if (state.status === "ready") onReady?.();
  }, [state.status, onReady]);

  const elapsed = events
    .slice()
    .reverse()
    .find((e) => typeof e.elapsed_s === "number")?.elapsed_s ?? 0;

  const status = state.status;
  const isReady = status === "ready";
  const isFailed = status === "failed";

  return (
    <Card className={cn(
      "relative overflow-hidden border-2 transition-all duration-500",
      isReady && "border-emerald-500/40 shadow-glow-cyan",
      isRunning && "border-cnc-electric/60 shadow-glow",
      isFailed && "border-cnc-rose/50",
      !isReady && !isRunning && !isFailed && "border-cnc-electric/30 shadow-glow-sm",
      className,
    )}>
      {/* Animated top border */}
      {isRunning && (
        <div className="absolute inset-x-0 top-0 h-[2px] overflow-hidden">
          <div className="h-full w-full animate-shimmer bg-gradient-to-r from-transparent via-cnc-cyan to-transparent bg-[length:200%_100%]" />
        </div>
      )}

      <div className="grid gap-6 p-6 md:grid-cols-[auto_1fr_auto] md:p-8 md:items-center">
        {/* Step indicator + icon */}
        <div className="flex items-center gap-4">
          <div className={cn(
            "relative flex h-16 w-16 items-center justify-center rounded-2xl transition-all duration-500",
            isReady && "bg-emerald-500/20 ring-2 ring-emerald-500/40",
            isRunning && "bg-cnc-electric/20 ring-2 ring-cnc-electric/60 animate-pulse-glow",
            isFailed && "bg-cnc-rose/20 ring-2 ring-cnc-rose/50",
            !isReady && !isRunning && !isFailed && "bg-azure-grad shadow-glow",
          )}>
            {isReady ? (
              <CheckCircle2 className="h-8 w-8 text-emerald-400" strokeWidth={2.5} />
            ) : isRunning ? (
              <Loader2 className="h-8 w-8 animate-spin text-cnc-cyan" strokeWidth={2.5} />
            ) : isFailed ? (
              <AlertCircle className="h-8 w-8 text-cnc-rose" strokeWidth={2.5} />
            ) : (
              <Database className="h-8 w-8 text-white" strokeWidth={2.5} />
            )}
          </div>
          <div className="hidden md:flex flex-col">
            <span className="text-[10px] font-mono uppercase tracking-widest text-cnc-muted">Step 1 / 2</span>
            <span className="text-2xl font-extrabold text-white">Index Workspace</span>
          </div>
        </div>

        {/* Center — status */}
        <div className="space-y-3 md:space-y-2">
          <div className="md:hidden">
            <span className="text-2xl font-extrabold text-white">Index Workspace</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={status} />
            {state.workspace && (
              <Badge variant="muted" className="font-mono">
                <FolderOpen className="h-3 w-3" />
                {truncatePath(state.workspace, 50)}
              </Badge>
            )}
            {isReady && state.duration_s != null && (
              <Badge variant="success">
                <Clock className="h-3 w-3" />
                Indexed in {fmtSeconds(state.duration_s)}
              </Badge>
            )}
          </div>

          <p className="max-w-xl text-sm text-cnc-muted">
            {status === "idle" && "Augment buduje semantyczny index Twojego repo (vector + AST). Zrób to raz — wszystkie późniejsze tool calls są szybsze i bardziej precyzyjne."}
            {status === "running" && `Indeksowanie w toku... ${fmtSeconds(elapsed)}. Inkrementalne — kolejne uruchomienia będą szybsze.`}
            {status === "ready" && "✓ Index gotowy. Możesz teraz uruchamiać dowolny tool z pełnym kontekstem repo."}
            {status === "failed" && (state.error ?? "Indexing failed. Sprawdź instalację Auggie CLI.")}
          </p>

          {/* Advanced workspace input */}
          <AnimatePresence>
            {(advanced || (!isReady && !isRunning)) && status !== "ready" && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="flex flex-col gap-2 pt-2 sm:flex-row"
              >
                <div className="flex-1 space-y-1.5">
                  <Label htmlFor="ws-path">Workspace path (optional)</Label>
                  <Input
                    id="ws-path"
                    value={workspace}
                    onChange={(e) => setWorkspace(e.target.value)}
                    placeholder="/abs/path/to/repo (default: AUGGIE_WORKSPACE or cwd)"
                    disabled={isRunning}
                    className="font-mono text-xs"
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Live progress timeline */}
          {isRunning && events.length > 0 && (
            <div className="mt-3 max-h-32 overflow-y-auto rounded-lg border border-cnc-border bg-cnc-bg/60 p-3 font-mono text-[11px] no-scrollbar">
              {events.slice(-6).map((ev, i) => (
                <div key={i} className="flex items-center gap-2 py-0.5">
                  <span className={cn(
                    "h-1.5 w-1.5 shrink-0 rounded-full",
                    ev.type === "tick" && "bg-cnc-cyan animate-pulse",
                    ev.type === "ok" && "bg-emerald-400",
                    ev.type === "error" && "bg-cnc-rose",
                    ev.type === "start" && "bg-cnc-electric",
                  )} />
                  <span className="text-cnc-muted">[{new Date((ev.ts ?? 0) * 1000).toLocaleTimeString()}]</span>
                  <span className="text-cnc-ink truncate">{ev.message ?? ev.type}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right — CTA */}
        <div className="flex flex-col gap-2 md:items-end md:min-w-[180px]">
          {!isRunning && !isReady && (
            <Button size="lg" className="w-full md:w-auto" onClick={() => start(workspace || undefined)}>
              <Play className="h-5 w-5" />
              {isFailed ? "Retry Indexing" : "Start Indexing"}
              <ArrowRight className="h-4 w-4" />
            </Button>
          )}
          {isRunning && (
            <Button variant="outline" size="lg" onClick={cancel} className="w-full md:w-auto">
              Cancel
            </Button>
          )}
          {isReady && (
            <>
              <Button variant="accent" size="lg" className="w-full md:w-auto" onClick={() => onReady?.()}>
                <Zap className="h-5 w-5" />
                Run Tools
              </Button>
              <Button variant="ghost" size="sm" onClick={() => start(workspace || undefined)}>
                <RotateCcw className="h-3.5 w-3.5" /> Re-index
              </Button>
            </>
          )}
          {!advanced && status === "idle" && (
            <button
              onClick={() => setAdvanced(true)}
              className="text-[10px] uppercase tracking-wider text-cnc-muted hover:text-cnc-electric2"
            >
              Advanced options
            </button>
          )}
        </div>
      </div>
    </Card>
  );
}

function StatusBadge({ status }: { status: string }) {
  switch (status) {
    case "ready": return <Badge variant="success">● Ready</Badge>;
    case "running": return <Badge variant="azure">● Indexing</Badge>;
    case "failed": return <Badge variant="danger">● Failed</Badge>;
    default: return <Badge variant="muted">○ Idle</Badge>;
  }
}

function truncatePath(p: string, max: number): string {
  if (p.length <= max) return p;
  return "…" + p.slice(p.length - max + 1);
}
