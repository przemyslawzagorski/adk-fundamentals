import * as React from "react";
import { fetchIndexStatus, postSSE, type IndexState, type SseEvent } from "@/api/client";

export interface IndexEvent {
  type: string;
  ts: number;
  message?: string;
  elapsed_s?: number;
  duration_s?: number;
  workspace?: string;
  command?: string;
  exit_code?: number;
  response?: string;
  hint?: string;
  status?: string;
}

export interface UseIndexWarmup {
  state: IndexState;
  events: IndexEvent[];
  isRunning: boolean;
  start: (workspace?: string, additional?: string[]) => void;
  cancel: () => void;
  refresh: () => Promise<void>;
}

const INITIAL: IndexState = {
  status: "idle",
  started_at: null,
  finished_at: null,
  duration_s: null,
  workspace: null,
  error: null,
  exit_code: null,
};

export function useIndexWarmup(): UseIndexWarmup {
  const [state, setState] = React.useState<IndexState>(INITIAL);
  const [events, setEvents] = React.useState<IndexEvent[]>([]);
  const handleRef = React.useRef<{ cancel(): void } | null>(null);
  const [isRunning, setRunning] = React.useState(false);

  const refresh = React.useCallback(async () => {
    try {
      const s = await fetchIndexStatus();
      setState(s);
    } catch {
      /* ignore */
    }
  }, []);

  React.useEffect(() => {
    refresh();
  }, [refresh]);

  const start = React.useCallback((workspace?: string, additional: string[] = []) => {
    if (isRunning) return;
    setEvents([]);
    setRunning(true);
    setState((s) => ({ ...s, status: "running", error: null, started_at: Date.now() / 1000 }));

    handleRef.current = postSSE(
      "/api/index/start",
      { workspace, additional },
      (ev: SseEvent) => {
        setEvents((prev) => [...prev, ev as IndexEvent]);
        if (ev.type === "ok") {
          setState((s) => ({
            ...s,
            status: "ready",
            duration_s: ev.duration_s ?? null,
            finished_at: Date.now() / 1000,
            error: null,
          }));
        } else if (ev.type === "error") {
          setState((s) => ({
            ...s,
            status: "failed",
            error: ev.message ?? "unknown",
            finished_at: Date.now() / 1000,
            exit_code: ev.exit_code ?? -1,
          }));
        } else if (ev.type === "end") {
          setRunning(false);
          handleRef.current = null;
          refresh();
        }
      },
      (err) => {
        setEvents((prev) => [...prev, { type: "error", ts: Date.now() / 1000, message: err.message }]);
        setState((s) => ({ ...s, status: "failed", error: err.message }));
        setRunning(false);
      },
    );
  }, [isRunning, refresh]);

  const cancel = React.useCallback(() => {
    handleRef.current?.cancel();
    handleRef.current = null;
    setRunning(false);
  }, []);

  return { state, events, isRunning, start, cancel, refresh };
}
