// Analyst System (module_20) API client — Jira ticket -> HLD -> Epics
import { postSSE, type SseHandle } from "./client";

export interface AnalystConfig {
  jira: { configured: boolean; base_url: string | null };
  confluence: { configured: boolean; base_url: string | null };
  notebooklm: { enabled: boolean; notebook_url: string | null };
  model: string;
  defaults: { max_critique_iterations: number };
}

export interface AnalystEpicUserStory {
  as_a?: string;
  i_want?: string;
  so_that?: string;
}

export interface AnalystEpic {
  title: string;
  summary?: string;
  scope?: string[];
  out_of_scope?: string[];
  acceptance_criteria?: string[];
  user_stories?: AnalystEpicUserStory[];
  labels?: string[];
  priority?: "High" | "Medium" | "Low" | string;
  estimate_t_shirt?: "S" | "M" | "L" | "XL" | string;
  dependencies?: string[];
  hld_section_refs?: string[];
}

export interface AnalystSessionSummary {
  id: string;
  created: number;
  issue_key: string;
  status: "running" | "ready" | "error";
  hld_chars: number;
  epics_count: number;
}

export interface AnalystSession {
  id: string;
  created: number;
  issue_key: string;
  model: string;
  max_critique_iterations: number;
  ticket: string;
  wiki_context: string;
  domain_context: string;
  current_hld: string;
  epics_json_raw: string;
  epics: AnalystEpic[];
  status: "running" | "ready" | "error";
  error: string | null;
  stages: string[];
  published_jira?: { index: number; title: string; key: string; url: string }[];
  published_confluence?: { id: string; title: string; url: string | null; version: number };
  jira_failures?: { index: number; title?: string; error: string }[];
}

export type AnalystStage =
  | "ticket_fetcher"
  | "context_gatherer"
  | "hld_writer"
  | "critique_loop"
  | "epic_decomposer";

export type AnalystEvent =
  | { type: "session_start"; session_id: string }
  | { type: "stages"; stages: AnalystStage[] }
  | { type: "stage_active"; stage: AnalystStage }
  | { type: "text"; stage: AnalystStage; text: string }
  | { type: "done"; session_id: string; epics_count: number; hld_chars: number }
  | { type: "error"; session_id?: string; message: string }
  | { type: string; [k: string]: any };

export async function fetchAnalystConfig(): Promise<AnalystConfig> {
  const r = await fetch("/api/analyst/config");
  if (!r.ok) throw new Error(`analyst config ${r.status}`);
  return r.json();
}

export async function fetchAnalystSessions(): Promise<AnalystSessionSummary[]> {
  const r = await fetch("/api/analyst/sessions");
  if (!r.ok) throw new Error(`analyst sessions ${r.status}`);
  return r.json();
}

export async function fetchAnalystSession(id: string): Promise<AnalystSession> {
  const r = await fetch(`/api/analyst/sessions/${id}`);
  if (!r.ok) throw new Error(`analyst session ${r.status}`);
  return r.json();
}

export interface StartGenerateOptions {
  issue_key: string;
  max_critique_iterations: number;
  enable_notebooklm?: boolean;
  notebooklm_url?: string;
  model?: string;
  onEvent: (ev: AnalystEvent) => void;
  onError?: (e: Error) => void;
}

export function startAnalystGenerate(opts: StartGenerateOptions): SseHandle {
  return postSSE(
    "/api/analyst/generate",
    {
      issue_key: opts.issue_key,
      max_critique_iterations: opts.max_critique_iterations,
      enable_notebooklm: opts.enable_notebooklm,
      notebooklm_url: opts.notebooklm_url,
      model: opts.model,
    },
    (ev) => opts.onEvent(ev as AnalystEvent),
    opts.onError,
  );
}

export interface PublishJiraPayload {
  project_key: string;
  epics: AnalystEpic[];
  parent_key?: string;
  add_acceptance_criteria_in_description?: boolean;
}

export interface PublishJiraResult {
  session_id: string;
  ok: boolean;
  created: { index: number; title: string; key: string; url: string }[];
  failures: { index: number; title?: string; error: string }[];
}

export async function publishJira(
  session_id: string,
  payload: PublishJiraPayload,
): Promise<PublishJiraResult> {
  const r = await fetch(`/api/analyst/sessions/${session_id}/publish/jira`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      add_acceptance_criteria_in_description: true,
      ...payload,
    }),
  });
  if (!r.ok) {
    const txt = await r.text().catch(() => "");
    throw new Error(`publish jira ${r.status}: ${txt}`);
  }
  return r.json();
}

export interface PublishConfluencePayload {
  space_key: string;
  title: string;
  parent_id?: string;
  labels?: string[];
}

export async function publishConfluence(
  session_id: string,
  payload: PublishConfluencePayload,
): Promise<{ session_id: string; ok: boolean; page: { id: string; title: string; url: string | null; version: number } }> {
  const r = await fetch(`/api/analyst/sessions/${session_id}/publish/confluence`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) {
    const txt = await r.text().catch(() => "");
    throw new Error(`publish confluence ${r.status}: ${txt}`);
  }
  return r.json();
}
