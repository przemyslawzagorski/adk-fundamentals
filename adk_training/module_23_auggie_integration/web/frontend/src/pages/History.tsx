import * as React from "react";
import { motion } from "framer-motion";
import {
  History as HistoryIcon, Clock, CheckCircle2, AlertCircle, XCircle, Zap, RefreshCw, Copy, Check,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AmbientBackground } from "@/components/concierge/ambient-background";
import { HelpPanel } from "@/components/concierge/help-panel";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn, fmtSeconds } from "@/lib/utils";

interface RunSummary {
  run_id: string;
  tool_id: string | null;
  tool_name: string | null;
  status: "running" | "ok" | "error" | "cancelled" | string;
  started_at: number | null;
  duration_s: number | null;
  cached: boolean | null;
  inputs_summary: string | null;
  error: string | null;
}

interface RunDetail extends RunSummary {
  inputs?: Record<string, any>;
  output?: string;
  logs?: Array<{ ts: number; level: string; message: string }>;
  events?: Array<{ ts: number; type: string; [k: string]: any }>;
  finished_at?: number;
}

const statusBadge = (s: string) => {
  switch (s) {
    case "ok": return <Badge variant="success"><CheckCircle2 className="h-3 w-3" /> OK</Badge>;
    case "error": return <Badge variant="danger"><AlertCircle className="h-3 w-3" /> Error</Badge>;
    case "cancelled": return <Badge variant="muted"><XCircle className="h-3 w-3" /> Cancelled</Badge>;
    case "running": return <Badge variant="azure">Running</Badge>;
    default: return <Badge variant="muted">{s}</Badge>;
  }
};

export function HistoryPage() {
  const [runs, setRuns] = React.useState<RunSummary[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [selected, setSelected] = React.useState<RunDetail | null>(null);
  const [detailLoading, setDetailLoading] = React.useState(false);
  const [filter, setFilter] = React.useState<string>("");

  const refresh = React.useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch("/api/runs?limit=200");
      const data = await r.json();
      setRuns(data.runs ?? []);
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => { refresh(); }, [refresh]);

  const openRun = React.useCallback(async (id: string) => {
    setDetailLoading(true);
    setSelected(null);
    try {
      const r = await fetch(`/api/runs/${id}`);
      if (r.ok) setSelected(await r.json());
    } finally {
      setDetailLoading(false);
    }
  }, []);

  const filtered = React.useMemo(() => {
    const f = filter.trim().toLowerCase();
    if (!f) return runs;
    return runs.filter(r =>
      (r.tool_id ?? "").toLowerCase().includes(f) ||
      (r.tool_name ?? "").toLowerCase().includes(f) ||
      (r.inputs_summary ?? "").toLowerCase().includes(f) ||
      (r.status ?? "").toLowerCase().includes(f),
    );
  }, [runs, filter]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="relative min-h-[calc(100vh-4rem)]"
    >
      <AmbientBackground />
      <div className="container py-8 lg:py-12">
        <header className="mb-6 flex items-center justify-between gap-4">
          <div>
            <Badge variant="cyan" className="mb-2">
              <HistoryIcon className="h-3 w-3" /> Run History
            </Badge>
            <h1 className="text-3xl font-extrabold text-white md:text-4xl">
              Historia <span className="text-gradient-azure">wywołań</span>
            </h1>
            <p className="mt-1 text-sm text-cnc-muted">
              Każde uruchomienie toola jest zapisywane na dysku — z inputami, logami z CLI, wynikiem i błędami.
            </p>
          </div>
          <Button variant="outline" onClick={refresh} disabled={loading}>
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} /> Refresh
          </Button>
        </header>

        <HelpPanel
          storageKey="help.history"
          summary="Przeglądaj poprzednie uruchomienia narzędzi Concierge — kliknij wiersz, aby zobaczyć inputy, logi i wynik."
          items={[
            { icon: HistoryIcon, title: "Persistent storage", desc: "Każdy run zapisywany jako JSON w artifacts/concierge_runs/." },
            { icon: Clock, title: "Pełen kontekst", desc: "Inputy, output, logi z CLI Auggie, eventy SSE — wszystko w jednym widoku." },
            { icon: AlertCircle, title: "Błędy i anulowania", desc: "Status: ok / error / cancelled (zamknięcie modala = kill subprocesu)." },
          ]}
        />

        <div className="mt-6 grid gap-4 lg:grid-cols-[440px_1fr]">
          <div>
            <input
              type="text"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Filtruj (tool, status, input)…"
              className="mb-3 w-full rounded-lg border border-cnc-border bg-cnc-surface/40 px-3 py-2 text-sm text-cnc-ink placeholder:text-cnc-muted focus:border-cnc-electric focus:outline-none"
            />
            <Card className="overflow-hidden">
              {filtered.length === 0 ? (
                <div className="p-6 text-center text-sm text-cnc-muted">
                  {loading ? "Ładowanie…" : "Brak runów. Uruchom jakiś tool w Studio."}
                </div>
              ) : (
                <ul className="max-h-[70vh] divide-y divide-cnc-border overflow-y-auto">
                  {filtered.map((r) => (
                    <li key={r.run_id}>
                      <button
                        onClick={() => openRun(r.run_id)}
                        className={cn(
                          "block w-full px-4 py-3 text-left transition-colors hover:bg-cnc-electric/5",
                          selected?.run_id === r.run_id && "bg-cnc-electric/10",
                        )}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex min-w-0 items-center gap-2">
                            {statusBadge(r.status)}
                            <span className="truncate font-mono text-xs text-cnc-ink">
                              {r.tool_name ?? r.tool_id}
                            </span>
                          </div>
                          <div className="flex shrink-0 items-center gap-1.5 text-[10px] text-cnc-muted">
                            {r.cached && <Zap className="h-3 w-3 text-emerald-400" />}
                            <Clock className="h-3 w-3" />
                            {r.duration_s != null ? fmtSeconds(r.duration_s) : "—"}
                          </div>
                        </div>
                        {r.inputs_summary && (
                          <div className="mt-1 truncate font-mono text-[10px] text-cnc-muted">{r.inputs_summary}</div>
                        )}
                        {r.error && (
                          <div className="mt-1 truncate text-[10px] text-cnc-rose">{r.error}</div>
                        )}
                        <div className="mt-1 text-[10px] text-cnc-muted">
                          {r.started_at ? new Date(r.started_at * 1000).toLocaleString() : "—"}
                          <span className="ml-2 font-mono opacity-50">{r.run_id}</span>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>

          <div>
            {!selected && !detailLoading && (
              <Card className="flex h-full min-h-[40vh] items-center justify-center p-8">
                <div className="text-center text-sm text-cnc-muted">
                  <HistoryIcon className="mx-auto mb-2 h-8 w-8 text-cnc-electric/60" />
                  Wybierz run po lewej, aby zobaczyć szczegóły.
                </div>
              </Card>
            )}
            {detailLoading && (
              <Card className="p-8 text-center text-sm text-cnc-muted">Ładowanie szczegółów…</Card>
            )}
            {selected && <RunDetailView run={selected} />}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function RunDetailView({ run }: { run: RunDetail }) {
  const [copied, setCopied] = React.useState(false);
  const output = run.output ?? "";
  const looksMarkdown = /^#|```|^\*\s|\n\*\s|^\d+\.\s/m.test(output);

  return (
    <Card className="space-y-4 p-5">
      <div className="flex flex-wrap items-center gap-2">
        {statusBadge(run.status)}
        <Badge variant="muted"><Clock className="h-3 w-3" /> {fmtSeconds(run.duration_s ?? 0)}</Badge>
        {run.cached && <Badge variant="cyan"><Zap className="h-3 w-3" /> Cached</Badge>}
        <span className="ml-auto font-mono text-[10px] text-cnc-muted">{run.run_id}</span>
      </div>
      <div>
        <div className="font-mono text-base font-bold text-white">{run.tool_name ?? run.tool_id}</div>
        <div className="text-xs text-cnc-muted">
          {run.started_at ? new Date(run.started_at * 1000).toLocaleString() : ""}
          {run.finished_at && run.started_at && (
            <> → {new Date(run.finished_at * 1000).toLocaleTimeString()}</>
          )}
        </div>
      </div>

      {run.inputs && Object.keys(run.inputs).length > 0 && (
        <Section title="Inputs">
          <pre className="rounded-lg border border-cnc-border bg-cnc-bg/60 p-3 font-mono text-xs text-cnc-ink/90">
{JSON.stringify(run.inputs, null, 2)}
          </pre>
        </Section>
      )}

      {run.error && (
        <Section title="Error">
          <div className="rounded-lg border border-cnc-rose/40 bg-cnc-rose/10 p-3">
            <div className="mb-1 text-xs font-bold text-cnc-rose">{(run as any).error?.exception ?? "Error"}</div>
            <pre className="whitespace-pre-wrap font-mono text-xs text-cnc-ink/90">
              {typeof run.error === "string" ? run.error : (run as any).error?.message}
            </pre>
          </div>
        </Section>
      )}

      {run.logs && run.logs.length > 0 && (
        <Section title={`Logs (${run.logs.length})`}>
          <div className="max-h-72 overflow-y-auto rounded-lg border border-cnc-border bg-cnc-bg/60 p-3 font-mono text-[11px]">
            {run.logs.map((log, i) => (
              <div key={i} className="flex items-start gap-2 py-0.5">
                <span className={cn(
                  "shrink-0 font-bold uppercase",
                  log.level === "error" && "text-cnc-rose",
                  log.level === "warning" && "text-amber-400",
                  log.level === "info" && "text-cnc-electric2",
                  log.level === "debug" && "text-cnc-muted",
                )}>{log.level.slice(0, 4).padEnd(4)}</span>
                <span className="text-cnc-muted">[{new Date(log.ts * 1000).toLocaleTimeString()}]</span>
                <span className="whitespace-pre-wrap break-all text-cnc-ink/90">{log.message}</span>
              </div>
            ))}
          </div>
        </Section>
      )}

      {output && (
        <Section
          title="Output"
          action={
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                navigator.clipboard.writeText(output);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              }}
            >
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </Button>
          }
        >
          {looksMarkdown ? (
            <div className="prose-cnc rounded-lg border border-cnc-border bg-cnc-bg/60 p-4">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{output}</ReactMarkdown>
            </div>
          ) : (
            <pre className="overflow-x-auto rounded-lg border border-cnc-border bg-cnc-bg/60 p-4 font-mono text-sm whitespace-pre-wrap text-cnc-ink">
{output}
            </pre>
          )}
        </Section>
      )}
    </Card>
  );
}

function Section({ title, children, action }: { title: string; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <h4 className="text-xs font-bold uppercase tracking-widest text-cnc-cyan2">{title}</h4>
        {action}
      </div>
      {children}
    </div>
  );
}
