// SSE client dla POST /api/generate/stream.
// EventSource nie wspiera POST i custom body, wiec uzywamy fetch + ReadableStream.

import type { GenerateRequest, Epic } from "./client";

export type StreamEvent =
  | { type: "session"; session_id: string; mode: "real" | "scaffold" }
  | { type: "stage_start"; stage: string; ts: number; iteration: number | null }
  | { type: "stage_event"; stage: string; preview: string; ts: number }
  | { type: "stage_end"; stage: string; ts: number }
  | { type: "done"; hld_markdown: string; epics: Epic[]; iterations: number }
  | { type: "end"; session_id: string; status: string }
  | { type: "error"; message: string };

export async function* streamGenerate(
  body: GenerateRequest,
  signal?: AbortSignal,
): AsyncGenerator<StreamEvent, void, unknown> {
  const res = await fetch("/api/generate/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`Stream failed: HTTP ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // SSE: events separated by blank lines
    let sepIdx: number;
    while ((sepIdx = buffer.indexOf("\n\n")) !== -1) {
      const raw = buffer.slice(0, sepIdx);
      buffer = buffer.slice(sepIdx + 2);
      const dataLine = raw
        .split("\n")
        .filter((l) => l.startsWith("data:"))
        .map((l) => l.slice(5).trimStart())
        .join("\n");
      if (!dataLine) continue;
      try {
        yield JSON.parse(dataLine) as StreamEvent;
      } catch {
        // ignore malformed event
      }
    }
  }
}
