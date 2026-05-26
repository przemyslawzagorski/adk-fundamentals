import * as React from "react";
import { streamGenerate, type StreamEvent } from "@/api/stream";
import type { GenerateRequest, GenerateResponse } from "@/api/client";
import { PIPELINE_STAGES, type TimelineStage } from "@/components/timeline";

interface State {
  isStreaming: boolean;
  sessionId: string | null;
  mode: "real" | "scaffold" | null;
  stages: TimelineStage[];
  result: GenerateResponse | null;
  error: string | null;
  iterations: number;
}

const INITIAL_STAGES: TimelineStage[] = PIPELINE_STAGES.map((s) => ({
  key: s.key,
  label: s.label,
  description: s.description,
  status: "pending",
}));

const INITIAL_STATE: State = {
  isStreaming: false,
  sessionId: null,
  mode: null,
  stages: INITIAL_STAGES,
  result: null,
  error: null,
  iterations: 0,
};

function applyEvent(state: State, ev: StreamEvent): State {
  switch (ev.type) {
    case "session":
      return { ...state, sessionId: ev.session_id, mode: ev.mode };
    case "stage_start": {
      const stages = state.stages.map((s) =>
        s.key === ev.stage
          ? { ...s, status: "active" as const, startedAt: ev.ts, endedAt: undefined,
              iteration: ev.iteration ?? s.iteration }
          : s,
      );
      // Jezeli stage nie byl predefiniowany - dodaj na koniec
      if (!stages.find((s) => s.key === ev.stage)) {
        stages.push({
          key: ev.stage,
          label: ev.stage,
          status: "active",
          startedAt: ev.ts,
          iteration: ev.iteration,
        });
      }
      return { ...state, stages };
    }
    case "stage_event": {
      const stages = state.stages.map((s) =>
        s.key === ev.stage ? { ...s, preview: ev.preview } : s,
      );
      return { ...state, stages };
    }
    case "stage_end": {
      const stages = state.stages.map((s) =>
        s.key === ev.stage && s.status === "active"
          ? { ...s, status: "done" as const, endedAt: ev.ts }
          : s,
      );
      return { ...state, stages };
    }
    case "done": {
      const result: GenerateResponse = {
        session_id: state.sessionId ?? "",
        hld_markdown: ev.hld_markdown,
        epics: ev.epics,
        status: state.mode === "real" ? (ev.hld_markdown ? "real" : "real_empty") : "scaffold",
      };
      return { ...state, result, iterations: ev.iterations };
    }
    case "end":
      return { ...state, isStreaming: false };
    case "error": {
      const stages = state.stages.map((s) =>
        s.status === "active" ? { ...s, status: "error" as const } : s,
      );
      return { ...state, stages, error: ev.message, isStreaming: false };
    }
  }
}

export function useGenerateStream() {
  const [state, setState] = React.useState<State>(INITIAL_STATE);
  const abortRef = React.useRef<AbortController | null>(null);

  const start = React.useCallback(async (body: GenerateRequest) => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setState({ ...INITIAL_STATE, isStreaming: true });
    try {
      for await (const ev of streamGenerate(body, ctrl.signal)) {
        setState((prev) => applyEvent(prev, ev));
      }
    } catch (e) {
      if ((e as Error).name === "AbortError") return;
      setState((prev) => ({
        ...prev,
        error: (e as Error).message,
        isStreaming: false,
      }));
    }
  }, []);

  const cancel = React.useCallback(() => {
    abortRef.current?.abort();
    setState((prev) => ({ ...prev, isStreaming: false }));
  }, []);

  React.useEffect(() => () => abortRef.current?.abort(), []);

  return { ...state, start, cancel };
}
