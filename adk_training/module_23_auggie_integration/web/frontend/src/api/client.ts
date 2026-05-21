// API client + SSE helpers for Concierge backend.

export interface ToolInputSpec {
  name: string;
  type: "input" | "textarea";
  label: string;
  required?: boolean;
  placeholder?: string;
  default?: string;
  input_type?: "number" | "text";
}

export interface ToolMeta {
  id: string;
  name: string;
  category: string;
  icon: string;
  tagline: string;
  description: string;
  inputs: ToolInputSpec[];
  estimated_seconds: number;
}

export interface ConfigSnapshot {
  model: string;
  timeout: number;
  max_turns: number;
  workspace: string;
  cli_path: string | null;
  has_session_auth: boolean;
  use_cli_fallback: boolean;
  platform: "windows" | "posix";
  index: IndexState;
}

export interface IndexState {
  status: "idle" | "running" | "ready" | "failed";
  started_at: number | null;
  finished_at: number | null;
  duration_s: number | null;
  workspace: string | null;
  error: string | null;
  exit_code: number | null;
}

export interface TelemetrySnapshot {
  summary: {
    total: number;
    success: number;
    failed: number;
    cached_hits: number;
    avg_duration_s: number;
    total_tool_calls: number;
    total_func_calls: number;
  };
  cache: {
    hits: number;
    misses: number;
    skipped_uncacheable: number;
    hit_rate: number;
    saved_seconds: number;
    evictions: number;
  };
  circuit_breaker: { state: string; consecutive_failures: number; opened_at: number };
  last_calls: Array<{
    tool: string;
    duration_s: number;
    success: boolean;
    cached: boolean;
    attempts: number;
    tool_calls: number;
    function_calls: number;
    error: string | null;
  }>;
}

export interface CostSnapshot {
  total_calls: number;
  cached_calls: number;
  total_estimated_usd: number;
  avg_per_call_usd: number;
  by_tool_usd: Record<string, number>;
  by_model_usd: Record<string, number>;
  note: string;
}

// =============================================================================
// REST
// =============================================================================
export async function fetchTools(): Promise<{ tools: ToolMeta[]; count: number }> {
  const r = await fetch("/api/tools");
  if (!r.ok) throw new Error(`tools fetch ${r.status}`);
  return r.json();
}

export async function fetchConfig(): Promise<ConfigSnapshot> {
  const r = await fetch("/api/config");
  if (!r.ok) throw new Error(`config fetch ${r.status}`);
  return r.json();
}

export async function fetchTelemetry(): Promise<TelemetrySnapshot> {
  const r = await fetch("/api/telemetry");
  return r.json();
}

export async function fetchCost(): Promise<CostSnapshot> {
  const r = await fetch("/api/cost");
  return r.json();
}

export async function fetchIndexStatus(): Promise<IndexState> {
  const r = await fetch("/api/index/status");
  return r.json();
}

export async function clearCache(): Promise<void> {
  await fetch("/api/cache/clear", { method: "POST" });
}

// =============================================================================
// SSE — generic POST + Server-Sent Events parser
// =============================================================================
export type SseEvent = { type: string; ts?: number; [k: string]: any };

export interface SseHandle {
  cancel(): void;
  done: Promise<void>;
}

export function postSSE(
  url: string,
  body: any,
  onEvent: (ev: SseEvent) => void,
  onError?: (e: Error) => void,
): SseHandle {
  const ctrl = new AbortController();
  const done = (async () => {
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body ?? {}),
        signal: ctrl.signal,
      });
      if (!r.ok || !r.body) throw new Error(`SSE ${r.status}`);
      const reader = r.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf("\n\n")) !== -1) {
          const chunk = buf.slice(0, idx);
          buf = buf.slice(idx + 2);
          const line = chunk.split("\n").find((l) => l.startsWith("data: "));
          if (!line) continue;
          try {
            onEvent(JSON.parse(line.slice(6)));
          } catch (err) {
            console.warn("SSE parse fail", err, line);
          }
        }
      }
    } catch (e: any) {
      if (e.name !== "AbortError") onError?.(e);
    }
  })();
  return { cancel: () => ctrl.abort(), done };
}
