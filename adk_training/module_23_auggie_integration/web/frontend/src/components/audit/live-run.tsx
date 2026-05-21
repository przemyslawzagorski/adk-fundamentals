import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, ChevronRight, Loader2, AlertTriangle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AuditEvent } from "@/api/audit-client";

interface Props {
  events: AuditEvent[];
  phase: string;
  isRunning: boolean;
  error: string | null;
}

const PHASES = ["recon", "planning", "execution", "report"] as const;

function classifyPhase(phase: string): string {
  if (phase === "recon") return "recon";
  if (phase === "planning") return "planning";
  if (phase.startsWith("scenario:")) return "execution";
  if (phase === "done") return "report";
  return "recon";
}

export function LiveRun({ events, phase, isRunning, error }: Props) {
  const cur = classifyPhase(phase);
  const curIdx = PHASES.indexOf(cur as any);
  const items = events.slice(-200);

  return (
    <Card className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-cnc-electric2" />
          <h3 className="text-lg font-extrabold text-white">Live run</h3>
          {isRunning && <Loader2 className="h-4 w-4 animate-spin text-cnc-cyan" />}
        </div>
        <Badge variant={error ? "danger" : isRunning ? "cyan" : "muted"}>
          {error ? "error" : isRunning ? phase || "running" : "idle"}
        </Badge>
      </div>

      {/* Phase tracker */}
      <div className="mb-4 grid grid-cols-4 gap-2">
        {PHASES.map((p, idx) => {
          const reached = curIdx >= idx;
          const active = curIdx === idx && isRunning;
          return (
            <div
              key={p}
              className={`rounded-xl border px-3 py-2 text-xs font-bold uppercase tracking-wider transition-all ${
                active
                  ? "border-cnc-electric bg-cnc-electric/15 text-cnc-electric2"
                  : reached
                  ? "border-cnc-cyan/40 bg-cnc-cyan/10 text-cnc-cyan2"
                  : "border-cnc-border bg-cnc-surface/40 text-cnc-muted"
              }`}
            >
              {idx + 1}. {p}
            </div>
          );
        })}
      </div>

      {error && (
        <div className="mb-3 flex items-start gap-2 rounded-xl border border-cnc-rose/40 bg-cnc-rose/10 p-3 text-sm text-cnc-rose">
          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
          <span className="break-all">{error}</span>
        </div>
      )}

      {/* Event timeline */}
      <div className="max-h-[420px] overflow-y-auto rounded-xl border border-cnc-line bg-cnc-bg/60 p-3 font-mono text-xs">
        <AnimatePresence initial={false}>
          {items.length === 0 && (
            <div className="text-cnc-muted">Waiting for events...</div>
          )}
          {items.map((ev, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-1 flex items-start gap-2"
            >
              <ChevronRight className="h-3 w-3 mt-1 shrink-0 text-cnc-electric2" />
              <span className="shrink-0 text-cnc-muted">
                {new Date((ev.ts ?? 0) * 1000).toLocaleTimeString([], { hour12: false })}
              </span>
              <EventLine ev={ev} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </Card>
  );
}

function EventLine({ ev }: { ev: AuditEvent }) {
  switch (ev.type) {
    case "phase":
      return <span className="text-cnc-cyan2">phase → {ev.phase}: {ev.message}</span>;
    case "recon_complete":
      return <span className="text-cnc-ink">recon done · {ev.summary?.split("\n")[0]}</span>;
    case "plan_ready":
      return (
        <span className="text-cnc-electric2">
          plan: {ev.scenarios?.map((s: any) => s.name).join(", ")}
        </span>
      );
    case "scenario_started":
      return <span className="text-cnc-cyan2">▶ scenario: {ev.name}</span>;
    case "scenario_finished":
      return (
        <span className={ev.passed ? "text-emerald-400" : "text-cnc-rose"}>
          ■ {ev.scenario} · {ev.passed ? "passed" : "failed"} · {ev.findings} findings · {ev.duration_s.toFixed(2)}s
        </span>
      );
    case "step_started":
      return <span className="text-cnc-muted">  · step #{ev.step_idx}: {ev.action}</span>;
    case "step_passed":
      return <span className="text-emerald-400">  ✓ step #{ev.step_idx}</span>;
    case "step_skipped":
      return <span className="text-cnc-muted">  ⊘ skipped: {ev.reason}</span>;
    case "step_error":
      return <span className="text-cnc-rose">  ✗ step #{ev.step_idx} error: {ev.error}</span>;
    case "finding":
      return (
        <span className="text-cnc-rose">
          ⚠ finding [{ev.severity}] {ev.title}
        </span>
      );
    case "report_ready":
      return <span className="text-emerald-400">📄 report ready · score {ev.score}/100</span>;
    case "run_finished":
      return <span className="text-emerald-400">✔ run finished · {ev.findings} findings · {ev.duration_s.toFixed(1)}s</span>;
    case "run_started":
      return <span className="text-cnc-electric2">▶ run started · {ev.run_id}</span>;
    case "safety_error":
      return <span className="text-cnc-rose">SAFETY: {ev.message}</span>;
    case "error":
      return <span className="text-cnc-rose">error: {ev.message}</span>;
    case "note":
      return <span className="text-cnc-muted">note: {ev.message}</span>;
    case "budget_exceeded":
      return <span className="text-cnc-gold">⏱ budget exceeded</span>;
    default:
      return <span className="text-cnc-muted">{ev.type}</span>;
  }
}
