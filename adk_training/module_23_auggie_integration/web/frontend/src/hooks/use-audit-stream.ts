import { useCallback, useRef, useState } from "react";
import { startAudit, type AuditEvent, type AuditMode, type AuditRun, fetchAuditRun } from "@/api/audit-client";

export interface UseAuditStream {
  isRunning: boolean;
  phase: string;
  events: AuditEvent[];
  findings: AuditEvent[]; // narrowed type=finding
  scenarios: AuditEvent[]; // type=scenario_started/finished
  runId: string | null;
  report: AuditRun | null;
  error: string | null;
  start: (params: { url: string; mode: AuditMode; scenario_nl?: string; ack_token?: string }) => Promise<void>;
  cancel: () => void;
  reset: () => void;
}

export function useAuditStream(): UseAuditStream {
  const [isRunning, setIsRunning] = useState(false);
  const [phase, setPhase] = useState("");
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [runId, setRunId] = useState<string | null>(null);
  const [report, setReport] = useState<AuditRun | null>(null);
  const [error, setError] = useState<string | null>(null);
  const handleRef = useRef<{ cancel(): void } | null>(null);

  const findings = events.filter((e) => e.type === "finding");
  const scenarios = events.filter(
    (e) => e.type === "scenario_started" || e.type === "scenario_finished",
  );

  const reset = useCallback(() => {
    setEvents([]);
    setPhase("");
    setRunId(null);
    setReport(null);
    setError(null);
  }, []);

  const cancel = useCallback(() => {
    handleRef.current?.cancel();
    handleRef.current = null;
    setIsRunning(false);
  }, []);

  const start = useCallback(
    async (params: { url: string; mode: AuditMode; scenario_nl?: string; ack_token?: string }) => {
      reset();
      setIsRunning(true);
      let lastRunId: string | null = null;

      const handle = startAudit({
        ...params,
        onEvent: (ev) => {
          setEvents((prev) => [...prev, ev]);
          if (ev.type === "phase") setPhase(ev.phase);
          else if (ev.type === "scenario_started") setPhase(`scenario:${ev.scenario}`);
          else if (ev.type === "run_started") {
            setRunId(ev.run_id);
            lastRunId = ev.run_id;
            setPhase("starting");
          } else if (ev.type === "report_ready") {
            lastRunId = ev.run_id;
            setRunId(ev.run_id);
          } else if (ev.type === "safety_error" || ev.type === "error" || ev.type === "run_failed") {
            setError((ev as any).message ?? (ev as any).error ?? "unknown error");
          } else if (ev.type === "run_finished") {
            setPhase("done");
          }
        },
        onError: (e) => setError(e.message),
      });

      handleRef.current = handle;
      await handle.done;
      handleRef.current = null;
      // Fetch full report once stream ends
      if (lastRunId) {
        try {
          const full = await fetchAuditRun(lastRunId);
          setReport(full);
        } catch (e: any) {
          setError(e?.message ?? "failed to load report");
        }
      }
      setIsRunning(false);
    },
    [reset],
  );

  return { isRunning, phase, events, findings, scenarios, runId, report, error, start, cancel, reset };
}
