// AuditOps API client (module_24)
import { postSSE, type SseHandle } from "./client";

export type AuditMode = "auto" | "guided";
export type Severity = "critical" | "high" | "medium" | "low" | "info";

export interface AuditConfigInfo {
  allowed_domains: string[];
  require_disclaimer: boolean;
  rate_limit_rps: number;
  headless: boolean;
  record_video: boolean;
  max_scenarios: number;
  max_steps_per_scenario: number;
  total_budget_seconds: number;
  llm_model: string;
  playwright: { installed: boolean; version: string | null; browsers_ok: boolean; error: string | null };
}

export interface AuditFinding {
  title: string;
  severity: Severity;
  owasp: string;
  scenario_id: string;
  evidence: Record<string, any>;
}

export interface ScenarioSummary {
  id: string;
  name: string;
  owasp: string;
  severity: Severity;
  passed: boolean;
  duration_s: number;
  error: string | null;
  video_url: string | null;
  screenshots: { path: string; url: string | null }[];
  findings: AuditFinding[];
}

export interface AuditRunSummary {
  run_id: string;
  target_url: string;
  duration_s: number;
  findings: number;
  started_at: number;
}

export interface AuditRun {
  run_id: string;
  target_url: string;
  started_at: number;
  finished_at: number;
  duration_s: number;
  recon: any;
  scenarios: ScenarioSummary[];
  findings: AuditFinding[];
  error?: string | null;
  report?: { markdown_url: string; json_url: string; score: number };
}

export interface AckResponse { token: string; statement: string; }

export type AuditEvent =
  | { type: "run_started"; run_id: string; mode: AuditMode; target_url: string; ts: number }
  | { type: "phase"; phase: string; message: string; ts: number }
  | { type: "recon_complete"; summary: string; forms?: number; technologies?: string[]; paths?: number; ts: number }
  | { type: "plan_ready"; scenarios: { id: string; name: string; severity?: Severity }[]; ts: number }
  | { type: "scenario_started"; scenario: string; name: string; ts: number }
  | { type: "step_started"; scenario: string; step_idx: number; action: string; ts: number }
  | { type: "step_passed"; scenario: string; step_idx: number; action: string; ts: number }
  | { type: "step_skipped"; scenario: string; reason: string; ts: number }
  | { type: "step_error"; scenario: string; step_idx: number; action: string; error: string; ts: number }
  | { type: "finding"; scenario: string; title: string; severity: Severity; ts: number }
  | { type: "scenario_finished"; scenario: string; passed: boolean; findings: number; duration_s: number; video?: string | null; ts: number }
  | { type: "report_ready"; run_id: string; markdown_url: string; json_url: string; score: number; ts: number }
  | { type: "run_finished"; run_id: string; duration_s: number; findings: number; ts: number }
  | { type: "run_failed"; error: string; ts: number }
  | { type: "safety_error"; message: string; ts: number }
  | { type: "error"; message: string; ts: number }
  | { type: "note"; scenario: string; message: string; ts: number }
  | { type: "budget_exceeded"; run_id: string; ts: number }
  | { type: string; [k: string]: any };

export async function fetchAuditConfig(): Promise<AuditConfigInfo> {
  const r = await fetch("/api/audit/config");
  if (!r.ok) throw new Error(`audit config ${r.status}`);
  return r.json();
}

export async function postDisclaimer(target_url: string, user_id = "anonymous"): Promise<AckResponse> {
  const r = await fetch("/api/audit/disclaimer/ack", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_url, user_id, accepted: true }),
  });
  if (!r.ok) throw new Error(`ack ${r.status}`);
  return r.json();
}

export async function fetchAuditRun(run_id: string): Promise<AuditRun> {
  const r = await fetch(`/api/audit/runs/${run_id}`);
  if (!r.ok) throw new Error(`run ${r.status}`);
  return r.json();
}

export async function fetchAuditRuns(): Promise<{ runs: AuditRunSummary[] }> {
  const r = await fetch("/api/audit/runs");
  if (!r.ok) throw new Error(`runs ${r.status}`);
  return r.json();
}

export interface StartAuditOptions {
  url: string;
  mode: AuditMode;
  scenario_nl?: string;
  ack_token?: string;
  onEvent: (ev: AuditEvent) => void;
  onError?: (e: Error) => void;
}

export function startAudit(opts: StartAuditOptions): SseHandle {
  return postSSE(
    "/api/audit/start",
    {
      url: opts.url,
      mode: opts.mode,
      scenario_nl: opts.scenario_nl,
      ack_token: opts.ack_token,
    },
    (ev) => opts.onEvent(ev as AuditEvent),
    opts.onError,
  );
}

// ----------------------------------------------------------------------------
// Skills (V1) — progressive disclosure: L1 manifest, L2 instructions, L3 refs
// ----------------------------------------------------------------------------

export interface SkillManifest {
  name: string;
  description: string;
  triggers: string[];
  resources: string[];
  resource_count?: number;
}

export interface SkillDetail extends SkillManifest {
  instructions: string;
}

export interface SkillResource {
  name: string;
  path: string;
  content: string;
}

export async function listSkills(): Promise<{ skills: SkillManifest[] }> {
  const r = await fetch("/api/audit/skills");
  if (!r.ok) throw new Error(`skills ${r.status}`);
  return r.json();
}

export async function fetchSkill(name: string): Promise<SkillDetail> {
  const r = await fetch(`/api/audit/skills/${encodeURIComponent(name)}`);
  if (!r.ok) throw new Error(`skill ${name} ${r.status}`);
  return r.json();
}

export async function fetchSkillResource(name: string, path: string): Promise<SkillResource> {
  const r = await fetch(`/api/audit/skills/${encodeURIComponent(name)}/resource?path=${encodeURIComponent(path)}`);
  if (!r.ok) throw new Error(`resource ${path} ${r.status}`);
  return r.json();
}

// ----------------------------------------------------------------------------
// Wiki (V2 / V3 / V4) — per-target audit memory
// ----------------------------------------------------------------------------

export interface WikiTarget {
  slug: string;
  runs: number;
  findings: number;
}

export interface WikiLintIssue {
  kind: string;
  path: string;
  detail: string;
}

export interface WikiLintReport {
  slug: string;
  issues: WikiLintIssue[];
}

export async function listWikiTargets(): Promise<{ targets: WikiTarget[] }> {
  const r = await fetch("/api/audit/wiki");
  if (!r.ok) throw new Error(`wiki ${r.status}`);
  return r.json();
}

export async function fetchWikiIndex(slug: string): Promise<string> {
  const r = await fetch(`/api/audit/wiki/${encodeURIComponent(slug)}/index`);
  if (!r.ok) throw new Error(`wiki index ${r.status}`);
  return r.text();
}

export async function fetchWikiFile(slug: string, path: string): Promise<string> {
  const r = await fetch(`/api/audit/wiki/${encodeURIComponent(slug)}/file?path=${encodeURIComponent(path)}`);
  if (!r.ok) throw new Error(`wiki file ${r.status}`);
  return r.text();
}

export async function fetchWikiLint(slug: string): Promise<WikiLintReport> {
  const r = await fetch(`/api/audit/wiki/${encodeURIComponent(slug)}/lint`);
  if (!r.ok) throw new Error(`wiki lint ${r.status}`);
  return r.json();
}

export interface SynthesizeRequest {
  slug: string;
  question?: string;
  accept?: boolean;
}

export interface SynthesizePreview {
  accepted: false;
  preview: string;
  note: string;
}

export interface SynthesizeAccepted {
  accepted: true;
  path: string;
  url: string;
}

export async function postWikiSynthesize(req: SynthesizeRequest): Promise<SynthesizePreview | SynthesizeAccepted> {
  const r = await fetch("/api/audit/wiki/synthesize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accept: false, ...req }),
  });
  if (!r.ok) throw new Error(`synthesize ${r.status}`);
  return r.json();
}
