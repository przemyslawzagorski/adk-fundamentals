import * as React from "react";
import { postSSE, type SseEvent } from "@/api/client";

export interface ToolStreamEvent extends SseEvent {
  elapsed_s?: number;
  eta_s?: number;
  progress?: number;
  duration_s?: number;
  cached?: boolean;
  output?: string;
  output_kind?: string;
  message?: string;
  exception?: string;
  success?: boolean;
  level?: string;
  run_id?: string;
}

export interface LogLine {
  ts: number;
  level: string;
  message: string;
}

export interface ToolStreamState {
  events: ToolStreamEvent[];
  logs: LogLine[];
  warnings: string[];
  runId: string | null;
  isRunning: boolean;
  result: { duration_s: number; cached: boolean; output: string; output_kind: string } | null;
  error: { message: string; duration_s?: number; exception?: string } | null;
  elapsed: number;
  eta: number;
  progress: number;
}

const initial: ToolStreamState = {
  events: [],
  logs: [],
  warnings: [],
  runId: null,
  isRunning: false,
  result: null,
  error: null,
  elapsed: 0,
  eta: 0,
  progress: 0,
};

export function useToolStream() {
  const [state, setState] = React.useState<ToolStreamState>(initial);
  const handleRef = React.useRef<{ cancel(): void } | null>(null);

  const run = React.useCallback((toolId: string, inputs: Record<string, any>) => {
    setState({ ...initial, isRunning: true });
    handleRef.current = postSSE(
      "/api/tools/run",
      { tool_id: toolId, inputs },
      (ev: ToolStreamEvent) => {
        setState((s) => {
          const next: ToolStreamState = { ...s, events: [...s.events, ev] };
          if (ev.type === "start") {
            next.eta = ev.eta_s ?? 0;
            next.runId = ev.run_id ?? null;
          } else if (ev.type === "tick") {
            next.elapsed = ev.elapsed_s ?? next.elapsed;
            next.progress = ev.progress ?? next.progress;
            next.eta = ev.eta_s ?? next.eta;
          } else if (ev.type === "log") {
            next.logs = [...s.logs, {
              ts: ev.ts ?? Date.now() / 1000,
              level: ev.level ?? "info",
              message: ev.message ?? "",
            }];
          } else if (ev.type === "warning") {
            next.warnings = [...s.warnings, ev.message ?? ""];
          } else if (ev.type === "result") {
            next.result = {
              duration_s: ev.duration_s ?? 0,
              cached: !!ev.cached,
              output: ev.output ?? "",
              output_kind: ev.output_kind ?? "text",
            };
            next.elapsed = ev.duration_s ?? next.elapsed;
            next.progress = 1;
          } else if (ev.type === "error") {
            next.error = {
              message: ev.message ?? "unknown",
              duration_s: ev.duration_s,
              exception: ev.exception,
            };
          } else if (ev.type === "end") {
            next.isRunning = false;
            handleRef.current = null;
          }
          return next;
        });
      },
      (err) => {
        setState((s) => ({ ...s, isRunning: false, error: { message: err.message } }));
      },
    );
  }, []);

  const cancel = React.useCallback(() => {
    handleRef.current?.cancel();
    handleRef.current = null;
    setState((s) => ({ ...s, isRunning: false }));
  }, []);

  const reset = React.useCallback(() => setState(initial), []);

  return { ...state, run, cancel, reset };
}
