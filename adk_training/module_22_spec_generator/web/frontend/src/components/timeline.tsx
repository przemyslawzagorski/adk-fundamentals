import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle2,
  Loader2,
  AlertCircle,
  Circle,
  Ticket,
  Network,
  PenLine,
  RefreshCw,
  ListTree,
} from "lucide-react";
import { cn } from "@/lib/utils";

export type StageStatus = "pending" | "active" | "done" | "error";

export interface TimelineStage {
  key: string;
  label: string;
  description?: string;
  status: StageStatus;
  startedAt?: number;
  endedAt?: number;
  preview?: string;
  iteration?: number | null;
}

export const PIPELINE_STAGES: { key: string; label: string; description: string }[] = [
  { key: "ticket_fetcher",   label: "Pobieranie ticketu", description: "Jira MCP -> ticket_payload" },
  { key: "context_parallel", label: "Kontekst (Wiki/Code/NLM)", description: "Parallel agents" },
  { key: "hld_writer",       label: "Pisanie HLD",        description: "Gemini 2.5" },
  { key: "critique_loop",    label: "Krytyka i poprawki", description: "LoopAgent" },
  { key: "epic_decomposer",  label: "Rozbicie na epiki",  description: "JSON output" },
];

const STAGE_ICON: Record<string, React.ComponentType<{ className?: string }>> = {
  ticket_fetcher: Ticket,
  context_parallel: Network,
  hld_writer: PenLine,
  critique_loop: RefreshCw,
  epic_decomposer: ListTree,
};

interface Props {
  stages: TimelineStage[];
  errorMessage?: string;
  isStreaming?: boolean;
}

function formatDuration(start?: number, end?: number): string | null {
  if (!start) return null;
  const stop = end ?? Date.now() / 1000;
  const ms = Math.max(0, (stop - start) * 1000);
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

export function Timeline({ stages, errorMessage, isStreaming }: Props) {
  const anyActive = stages.some((s) => s.status === "active");
  const allDone = stages.length > 0 && stages.every((s) => s.status === "done");
  const status: { label: string; color: string; pulse: boolean } = errorMessage
    ? { label: "Blad polaczenia", color: "bg-destructive", pulse: false }
    : anyActive || isStreaming
    ? { label: "Streaming...", color: "bg-zagi-crimson", pulse: true }
    : allDone
    ? { label: "Zakonczono", color: "bg-zagi-neon", pulse: false }
    : { label: "Oczekiwanie", color: "bg-zagi-dim", pulse: false };

  return (
    <div className="rounded-2xl border border-white/10 bg-zagi-surface/80 p-6 shadow-card-up">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-zagi-neon">
            Pipeline
          </div>
          <h3 className="mt-1 text-lg font-semibold text-white">Live progress</h3>
        </div>
        <div className="flex items-center gap-2 text-xs text-zagi-muted">
          <span className={`h-1.5 w-1.5 rounded-full ${status.color} ${status.pulse ? "animate-pulse" : ""}`} />
          {status.label}
        </div>
      </div>

      <ol className="relative space-y-1">
        {stages.map((stage, idx) => (
          <StageRow key={stage.key} stage={stage} isLast={idx === stages.length - 1} />
        ))}
      </ol>

      {errorMessage && (
        <div className="mt-4 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}

function StageRow({ stage, isLast }: { stage: TimelineStage; isLast: boolean }) {
  const Icon = STAGE_ICON[stage.key] ?? Circle;
  const dur = formatDuration(stage.startedAt, stage.endedAt);

  return (
    <li className="relative pl-12">
      {/* connector */}
      {!isLast && (
        <span
          aria-hidden
          className={cn(
            "absolute left-[19px] top-9 h-[calc(100%-12px)] w-px",
            stage.status === "done"
              ? "bg-gradient-to-b from-zagi-neon to-white/5"
              : stage.status === "active"
                ? "bg-gradient-to-b from-zagi-crimson to-white/5"
                : "bg-white/5",
          )}
        />
      )}

      {/* status dot */}
      <span
        className={cn(
          "absolute left-1 top-2 grid h-9 w-9 place-items-center rounded-xl border transition",
          stage.status === "pending" && "border-white/10 bg-zagi-bg text-zagi-dim",
          stage.status === "active"  && "border-zagi-crimson/60 bg-zagi-crimson/15 text-zagi-crimson2 shadow-glow-sm",
          stage.status === "done"    && "border-zagi-neon/40 bg-zagi-neon/10 text-zagi-neon",
          stage.status === "error"   && "border-destructive/50 bg-destructive/15 text-destructive",
        )}
      >
        {stage.status === "active" ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : stage.status === "done" ? (
          <CheckCircle2 className="h-4 w-4" />
        ) : stage.status === "error" ? (
          <AlertCircle className="h-4 w-4" />
        ) : (
          <Icon className="h-4 w-4" />
        )}
      </span>

      <div className="pb-5 pt-1">
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={cn(
              "text-sm font-semibold",
              stage.status === "pending" ? "text-zagi-muted" : "text-white",
            )}
          >
            {stage.label}
          </span>
          {stage.iteration != null && (
            <span className="rounded-full border border-zagi-violet/30 bg-zagi-violet/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-zagi-violet">
              iter {stage.iteration}
            </span>
          )}
          {dur && stage.status !== "pending" && (
            <span className="rounded-full bg-white/[0.04] px-2 py-0.5 font-mono text-[10px] text-zagi-muted">
              {dur}
            </span>
          )}
        </div>
        {stage.description && (
          <div className="mt-0.5 text-xs text-zagi-muted">{stage.description}</div>
        )}

        <AnimatePresence>
          {stage.preview && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-2 overflow-hidden"
            >
              <pre className="max-h-32 overflow-auto rounded-md border border-white/5 bg-zagi-bg/60 p-2 font-mono text-[11px] leading-relaxed text-zagi-muted no-scrollbar">
                {stage.preview}
              </pre>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </li>
  );
}
