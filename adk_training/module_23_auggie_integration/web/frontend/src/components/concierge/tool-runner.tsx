import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  X, Play, Loader2, CheckCircle2, AlertCircle, Copy, Check, Clock, Zap, Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { DynamicIcon } from "./dynamic-icon";
import { useToolStream } from "@/hooks/use-tool-stream";
import { cn, fmtSeconds } from "@/lib/utils";
import type { ToolMeta } from "@/api/client";

interface ToolRunnerProps {
  tool: ToolMeta;
  onClose: () => void;
}

export function ToolRunner({ tool, onClose }: ToolRunnerProps) {
  const stream = useToolStream();
  const [inputs, setInputs] = React.useState<Record<string, string>>(() =>
    Object.fromEntries(tool.inputs.map((i) => [i.name, i.default ?? ""])),
  );
  const [pathSuggestions, setPathSuggestions] = React.useState<
    { label: string; path: string; hint?: string }[]
  >([]);

  React.useEffect(() => {
    let alive = true;
    fetch("/api/workspace/suggestions")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (alive && d?.suggestions) setPathSuggestions(d.suggestions);
      })
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, []);

  const isPathInput = (name: string) =>
    /path|target|file|dir|folder/i.test(name) && !/max_|count|num/i.test(name);

  const canRun = tool.inputs.every(
    (i) => !i.required || (inputs[i.name] ?? "").trim().length > 0,
  );

  const handleRun = () => {
    stream.run(tool.id, inputs);
  };

  const progressPct = stream.isRunning
    ? Math.min(99, Math.max(stream.progress * 100, (stream.elapsed / Math.max(stream.eta, 1)) * 90))
    : stream.result ? 100 : 0;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-cnc-bg/85 p-4 backdrop-blur-md"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, y: 20, opacity: 0 }}
        animate={{ scale: 1, y: 0, opacity: 1 }}
        exit={{ scale: 0.95, y: 20, opacity: 0 }}
        transition={{ duration: 0.3, ease: [0.2, 0.8, 0.2, 1] }}
        onClick={(e) => e.stopPropagation()}
        className="relative flex h-[88vh] max-h-[920px] w-full max-w-6xl flex-col overflow-hidden rounded-3xl border border-cnc-border bg-cnc-surface shadow-card-up"
      >
        {/* Top bar */}
        <header className="relative flex items-center justify-between gap-4 border-b border-cnc-border bg-gradient-to-r from-cnc-azure/10 via-cnc-electric/5 to-cnc-cyan/10 p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-azure-grad shadow-glow-sm">
              <DynamicIcon name={tool.icon} size={22} className="text-white" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-white">{tool.name}</h2>
              <p className="text-xs text-cnc-muted">{tool.tagline}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>

          {/* Progress bar */}
          {(stream.isRunning || stream.result) && (
            <div className="absolute inset-x-0 bottom-0 h-1 bg-cnc-bg">
              <motion.div
                className={cn(
                  "h-full",
                  stream.error ? "bg-cnc-rose" :
                  stream.result ? "bg-emerald-500" : "bg-azure-grad animate-gradient",
                )}
                initial={{ width: 0 }}
                animate={{ width: `${progressPct}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          )}
        </header>

        {/* Body — split */}
        <div className="grid flex-1 grid-cols-1 overflow-hidden lg:grid-cols-[420px_1fr]">
          {/* Left — input form */}
          <aside className="flex flex-col overflow-y-auto border-cnc-border bg-cnc-bg/40 p-5 lg:border-r">
            <h3 className="mb-1 text-xs font-bold uppercase tracking-widest text-cnc-electric2">Inputs</h3>
            <p className="mb-4 text-xs text-cnc-muted">{tool.description}</p>

            <div className="flex-1 space-y-4">
              {tool.inputs.map((spec) => (
                <div key={spec.name} className="space-y-1.5">
                  <Label htmlFor={spec.name}>
                    {spec.label}
                    {spec.required && <span className="ml-1 text-cnc-rose">*</span>}
                  </Label>
                  {spec.type === "textarea" ? (
                    <Textarea
                      id={spec.name}
                      value={inputs[spec.name] ?? ""}
                      onChange={(e) => setInputs((p) => ({ ...p, [spec.name]: e.target.value }))}
                      placeholder={spec.placeholder}
                      disabled={stream.isRunning}
                      rows={6}
                    />
                  ) : (
                    <Input
                      id={spec.name}
                      type={spec.input_type === "number" ? "number" : "text"}
                      value={inputs[spec.name] ?? ""}
                      onChange={(e) => setInputs((p) => ({ ...p, [spec.name]: e.target.value }))}
                      placeholder={spec.placeholder}
                      disabled={stream.isRunning}
                    />
                  )}
                  {isPathInput(spec.name) && pathSuggestions.length > 0 && !stream.isRunning && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {pathSuggestions.map((s) => (
                        <button
                          key={s.path}
                          type="button"
                          title={s.hint ? `${s.path}\n${s.hint}` : s.path}
                          onClick={() => setInputs((p) => ({ ...p, [spec.name]: s.path }))}
                          className="rounded-md border border-cnc-line bg-cnc-bg/40 px-2 py-0.5 text-[10px] text-cnc-muted hover:border-cnc-electric2 hover:text-white"
                        >
                          {s.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="sticky bottom-0 -mx-5 -mb-5 mt-5 border-t border-cnc-border bg-cnc-bg/95 p-5 backdrop-blur">
              {stream.isRunning ? (
                <Button variant="outline" size="lg" onClick={stream.cancel} className="w-full">
                  Cancel
                </Button>
              ) : (
                <Button size="lg" onClick={handleRun} disabled={!canRun} className="w-full">
                  <Play className="h-5 w-5" />
                  {stream.result ? "Run Again" : "Execute"} · ~{tool.estimated_seconds}s ETA
                </Button>
              )}
              {stream.result?.cached && (
                <p className="mt-2 text-center text-[11px] text-emerald-400">
                  ⚡ Cache hit — odpowiedź z lokalnego cache (0.1ms)
                </p>
              )}
            </div>
          </aside>

          {/* Right — output */}
          <main className="flex flex-col overflow-hidden bg-cnc-bg/20">
            {/* Status strip */}
            <div className="flex flex-wrap items-center gap-2 border-b border-cnc-border p-4">
              <StatusPill stream={stream} />
              {stream.isRunning && (
                <Badge variant="azure">
                  <Clock className="h-3 w-3" /> {fmtSeconds(stream.elapsed)} / ~{stream.eta}s
                </Badge>
              )}
              {stream.result && (
                <>
                  <Badge variant="success">
                    <CheckCircle2 className="h-3 w-3" /> {fmtSeconds(stream.result.duration_s)}
                  </Badge>
                  {stream.result.cached && <Badge variant="cyan"><Zap className="h-3 w-3" /> Cached</Badge>}
                </>
              )}
            </div>

            <div className="grid flex-1 grid-rows-[auto_auto_1fr] overflow-hidden">
              {/* Warnings strip */}
              {stream.warnings.length > 0 && (
                <div className="border-b border-amber-500/30 bg-amber-500/10 px-4 py-2 text-xs text-amber-200">
                  {stream.warnings.map((w, i) => (
                    <div key={i}>⚠ {w}</div>
                  ))}
                </div>
              )}

              {/* Live log stream (CLI stdout + factory logs) */}
              <div className="max-h-48 overflow-y-auto border-b border-cnc-border bg-cnc-bg/60 px-4 py-2 font-mono text-[11px] no-scrollbar">
                {stream.logs.length === 0 && stream.events.length <= 1 ? (
                  <div className="text-cnc-muted">Waiting for execution...</div>
                ) : (
                  <>
                    {stream.events.filter(e => e.type === "start" || e.type === "tick").slice(-3).map((ev, i) => (
                      <div key={`e-${i}`} className="flex items-center gap-2 py-0.5">
                        <Activity className={cn(
                          "h-3 w-3 shrink-0",
                          ev.type === "tick" ? "text-cnc-cyan" : "text-cnc-electric",
                        )} />
                        <span className="text-cnc-muted">[{new Date((ev.ts ?? 0) * 1000).toLocaleTimeString()}]</span>
                        <span className="font-bold text-cnc-ink">{ev.type}</span>
                        <span className="truncate text-cnc-muted">
                          {ev.message ?? (ev.elapsed_s != null ? `${ev.elapsed_s}s elapsed` : "")}
                        </span>
                      </div>
                    ))}
                    {stream.logs.slice(-50).map((log, i) => (
                      <div key={`l-${i}`} className="flex items-start gap-2 py-0.5">
                        <span className={cn(
                          "shrink-0 font-bold uppercase",
                          log.level === "error" && "text-cnc-rose",
                          log.level === "warning" && "text-amber-400",
                          log.level === "info" && "text-cnc-electric2",
                          log.level === "debug" && "text-cnc-muted",
                        )}>
                          {log.level.slice(0, 4).padEnd(4)}
                        </span>
                        <span className="text-cnc-muted">[{new Date(log.ts * 1000).toLocaleTimeString()}]</span>
                        <span className="whitespace-pre-wrap break-all text-cnc-ink/90">{log.message}</span>
                      </div>
                    ))}
                  </>
                )}
              </div>

              {/* Result panel */}
              <div className="flex-1 overflow-y-auto p-6">
                {stream.error && <ErrorBlock error={stream.error} />}
                {stream.result && <ResultBlock output={stream.result.output} />}
                {!stream.result && !stream.error && !stream.isRunning && (
                  <EmptyState tool={tool} />
                )}
                {stream.isRunning && !stream.result && <RunningSkeleton />}
              </div>
            </div>
          </main>
        </div>
      </motion.div>
    </motion.div>
  );
}

function StatusPill({ stream }: { stream: ReturnType<typeof useToolStream> }) {
  if (stream.error) return <Badge variant="danger"><AlertCircle className="h-3 w-3" /> Failed</Badge>;
  if (stream.isRunning) return <Badge variant="azure"><Loader2 className="h-3 w-3 animate-spin" /> Running</Badge>;
  if (stream.result) return <Badge variant="success"><CheckCircle2 className="h-3 w-3" /> Complete</Badge>;
  return <Badge variant="muted">Idle</Badge>;
}

function ErrorBlock({ error }: { error: { message: string; exception?: string } }) {
  return (
    <div className="rounded-2xl border border-cnc-rose/40 bg-cnc-rose/10 p-5">
      <div className="mb-2 flex items-center gap-2 font-bold text-cnc-rose">
        <AlertCircle className="h-5 w-5" />
        {error.exception ?? "Execution Error"}
      </div>
      <pre className="whitespace-pre-wrap font-mono text-xs text-cnc-ink/90">{error.message}</pre>
    </div>
  );
}

function ResultBlock({ output }: { output: string }) {
  const [copied, setCopied] = React.useState(false);
  const looksMarkdown = /^#|```|^\*\s|\n\*\s|^\d+\.\s/m.test(output);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold uppercase tracking-widest text-cnc-cyan2">Output</h4>
        <Button
          variant="ghost" size="sm"
          onClick={() => {
            navigator.clipboard.writeText(output);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          }}
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? "Copied" : "Copy"}
        </Button>
      </div>
      {looksMarkdown ? (
        <div className="prose-cnc rounded-2xl border border-cnc-border bg-cnc-bg/60 p-6">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{output}</ReactMarkdown>
        </div>
      ) : (
        <pre className="overflow-x-auto rounded-2xl border border-cnc-border bg-cnc-bg/60 p-6 font-mono text-sm whitespace-pre-wrap text-cnc-ink">
          {output}
        </pre>
      )}
    </div>
  );
}

function EmptyState({ tool }: { tool: ToolMeta }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
      <div className="rounded-2xl bg-cnc-surface p-5 ring-1 ring-cnc-border">
        <DynamicIcon name={tool.icon} size={48} className="text-cnc-electric2" />
      </div>
      <h3 className="text-lg font-bold text-white">{tool.name}</h3>
      <p className="max-w-md text-sm text-cnc-muted">{tool.description}</p>
      <p className="text-xs text-cnc-muted">Wypełnij pola po lewej i kliknij <b className="text-cnc-electric2">Execute</b>.</p>
    </div>
  );
}

function RunningSkeleton() {
  return (
    <div className="space-y-3">
      <div className="h-4 w-1/3 animate-pulse rounded bg-cnc-surface2" />
      <div className="h-3 w-full animate-pulse rounded bg-cnc-surface2" />
      <div className="h-3 w-5/6 animate-pulse rounded bg-cnc-surface2" />
      <div className="h-3 w-4/6 animate-pulse rounded bg-cnc-surface2" />
      <div className="mt-6 h-32 animate-pulse rounded-xl bg-cnc-surface2" />
    </div>
  );
}
