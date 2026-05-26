// Typed klient REST do FastAPI backendu Spec Generatora.
// Faza A: tylko POST /api/generate + GET /health.
// Faza B/C dorzuca: SSE stream, publish, export.

export interface Epic {
  title: string;
  summary: string;
  acceptance_criteria: string[];
  priority: "Highest" | "High" | "Medium" | "Low";
  labels: string[];
  estimated_story_points: number;
  dependencies: string[];
}

export interface GenerateRequest {
  issue_key: string;
  enable_notebooklm: boolean;
  max_critique_iterations: number;
  notebook_url?: string | null;
}

export interface GenerateResponse {
  session_id: string;
  hld_markdown: string;
  epics: Epic[];
  status: "scaffold" | "real" | "real_empty";
}

export interface HealthResponse {
  status: string;
  version: string;
  real_pipeline: boolean;
}

const BASE = ""; // Vite proxy obsluguje /api/* w trybie dev, prod = same origin.

async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + url, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      detail = await res.text();
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => jsonFetch<HealthResponse>("/health"),
  generate: (body: GenerateRequest) =>
    jsonFetch<GenerateResponse>("/api/generate", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  saveEdits: (sessionId: string, epics: Epic[], hldMarkdown?: string) =>
    jsonFetch<{ status: string; epics_count: number }>(`/api/sessions/${sessionId}`, {
      method: "PUT",
      body: JSON.stringify({ epics, hld_markdown: hldMarkdown ?? null }),
    }),
  publish: (sessionId: string, epics: Epic[]) =>
    jsonFetch<{ status: string; mode: string; note: string; epics_count: number }>(
      `/api/publish/${sessionId}`,
      {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, approved: true, edited_epics: epics }),
      },
    ),
  exportUrl: (sessionId: string, fmt: "md" | "json") =>
    `/api/sessions/${sessionId}/export.${fmt}`,
};
