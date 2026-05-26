import * as React from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Cpu,
  History,
  Trash2,
  ChevronRight,
  ArrowLeft,
} from "lucide-react";
import { GenerateForm } from "@/components/generate-form";
import { Timeline } from "@/components/timeline";
import { HldView } from "@/components/hld-view";
import { EpicsList } from "@/components/epics-list";
import { ActionsBar } from "@/components/actions-bar";
import { AmbientBackground } from "@/components/zagi/ambient-background";
import { useGenerateStream } from "@/hooks/use-generate-stream";
import { useSessionsStorage } from "@/hooks/use-sessions-storage";
import type { Epic } from "@/api/client";

export function Studio() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const isDemo = params.get("demo") === "1";

  const stream = useGenerateStream();
  const { result, stages, isStreaming, sessionId, mode, iterations, error, start, cancel } = stream;

  const [editedEpics, setEditedEpics] = React.useState<Epic[]>([]);
  const [savedSnapshot, setSavedSnapshot] = React.useState("[]");

  const { sessions, upsert, remove } = useSessionsStorage();

  // Auto-demo gdy ?demo=1 (jednorazowo, niezaleznie od HMR/StrictMode)
  const demoFiredRef = React.useRef(false);
  React.useEffect(() => {
    if (!isDemo) return;
    if (demoFiredRef.current) return;
    demoFiredRef.current = true;
    // wyczysc query param zeby nie odpalic ponownie po refreshu
    navigate("/studio", { replace: true });
    start({ issue_key: "DEMO-1", enable_notebooklm: false, max_critique_iterations: 1 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDemo]);

  // Inicjalizacja edytora po zakonczeniu streamu
  React.useEffect(() => {
    if (result) {
      setEditedEpics(result.epics);
      setSavedSnapshot(JSON.stringify(result.epics));
    }
  }, [result]);

  // Zapis do localStorage po zakonczeniu generacji
  React.useEffect(() => {
    if (result && sessionId) {
      upsert({
        id: sessionId,
        issueKey: extractIssueKey(result.hld_markdown) ?? sessionId.slice(0, 8),
        createdAt: Date.now(),
        mode: mode ?? "scaffold",
        hldMarkdown: result.hld_markdown,
        epics: result.epics,
        approved: false,
        iterations,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result, sessionId]);

  const dirty = JSON.stringify(editedEpics) !== savedSnapshot;
  const hasActivity = isStreaming || result || error;

  return (
    <motion.main
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35 }}
      className="relative isolate min-h-screen pt-24"
    >
      <AmbientBackground />

      <div className="container relative">
        {/* Top bar */}
        <div className="mb-8 flex flex-wrap items-center justify-between gap-3">
          <div>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-xs text-zagi-muted hover:text-white"
            >
              <ArrowLeft className="h-3 w-3" /> Powrot na strone glowna
            </Link>
            <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              ZAGI <span className="text-gradient-brand">Studio</span>
            </h1>
            <p className="mt-1 text-sm text-zagi-muted">
              Wygeneruj, edytuj, zatwierdz i wyeksportuj specyfikacje.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-zagi-muted">
            <Cpu className="h-3.5 w-3.5 text-zagi-neon" />
            Backend: <code className="rounded bg-white/[0.04] px-1.5 py-0.5 font-mono text-[11px] text-white">127.0.0.1:8766</code>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[400px_minmax(0,1fr)]">
          {/* LEFT */}
          <aside className="space-y-5">
            <GenerateForm
              isStreaming={isStreaming}
              initialIssueKey={isDemo ? "DEMO-1" : undefined}
              onStart={start}
              onCancel={cancel}
            />

            <SessionInfo
              sessionId={sessionId}
              mode={mode}
              iterations={iterations}
              epicsCount={editedEpics.length}
            />

            <SessionHistory
              sessions={sessions}
              currentId={sessionId ?? undefined}
              onRemove={remove}
              onLoad={(s) => {
                // Lokalny "load" - wstawiamy do widoku bez ponownego streamu.
                // Ustawiamy state przez stream-bypass: tworzymy fake "result"
                // przez bezposredni setState? Najprosciej: re-streamuj.
                start({
                  issue_key: s.issueKey,
                  enable_notebooklm: false,
                  max_critique_iterations: Math.max(1, s.iterations || 1),
                });
              }}
            />
          </aside>

          {/* RIGHT */}
          <section className="space-y-5">
            <AnimatePresence mode="wait">
              {hasActivity ? (
                <motion.div
                  key="content"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-5"
                >
                  <Timeline stages={stages} errorMessage={error ?? undefined} isStreaming={isStreaming} />

                  {result && sessionId && (
                    <>
                      <ActionsBar
                        sessionId={sessionId}
                        epics={editedEpics}
                        hldMarkdown={result.hld_markdown}
                        dirty={dirty}
                        onSaved={() => setSavedSnapshot(JSON.stringify(editedEpics))}
                      />
                      <HldView markdown={result.hld_markdown} />
                      <EpicsList epics={editedEpics} editable onChange={setEditedEpics} />
                    </>
                  )}
                </motion.div>
              ) : (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <EmptyState />
                </motion.div>
              )}
            </AnimatePresence>
          </section>
        </div>
      </div>
    </motion.main>
  );
}

function SessionInfo({
  sessionId,
  mode,
  iterations,
  epicsCount,
}: {
  sessionId: string | null;
  mode: "real" | "scaffold" | null;
  iterations: number;
  epicsCount: number;
}) {
  if (!sessionId) return null;
  return (
    <div className="rounded-2xl border border-white/10 bg-zagi-surface/60 p-5 backdrop-blur">
      <div className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-zagi-muted">
        Sesja
      </div>
      <dl className="space-y-2 text-sm">
        <Row k="ID" v={<code className="font-mono text-xs text-white">{sessionId.slice(0, 12)}</code>} />
        {mode && (
          <Row
            k="Tryb"
            v={
              <span className={mode === "real" ? "text-zagi-neon" : "text-zagi-gold"}>
                {mode === "real" ? "Real (Gemini)" : "Scaffold"}
              </span>
            }
          />
        )}
        <Row k="Epiki" v={<span className="text-white">{epicsCount}</span>} />
        {iterations > 0 && <Row k="Iteracje krytyki" v={<span className="text-white">{iterations}</span>} />}
      </dl>
    </div>
  );
}

function Row({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-zagi-muted">{k}</dt>
      <dd>{v}</dd>
    </div>
  );
}

function SessionHistory({
  sessions,
  currentId,
  onRemove,
  onLoad,
}: {
  sessions: ReturnType<typeof useSessionsStorage>["sessions"];
  currentId?: string;
  onRemove: (id: string) => void;
  onLoad: (s: ReturnType<typeof useSessionsStorage>["sessions"][number]) => void;
}) {
  if (sessions.length === 0) return null;
  return (
    <div className="rounded-2xl border border-white/10 bg-zagi-surface/60 p-5 backdrop-blur">
      <div className="mb-3 flex items-center gap-2">
        <History className="h-3.5 w-3.5 text-zagi-muted" />
        <span className="text-xs font-semibold uppercase tracking-[0.2em] text-zagi-muted">
          Ostatnie sesje
        </span>
      </div>
      <ul className="-mx-1 space-y-0.5">
        {sessions.slice(0, 6).map((s) => (
          <li key={s.id}>
            <div
              className={`group flex items-center gap-2 rounded-lg px-2 py-1.5 transition hover:bg-white/[0.04] ${
                s.id === currentId ? "bg-white/[0.05]" : ""
              }`}
            >
              <button
                onClick={() => onLoad(s)}
                className="flex flex-1 items-center justify-between text-left"
              >
                <div>
                  <div className="font-mono text-xs text-white">{s.issueKey}</div>
                  <div className="text-[10px] text-zagi-muted">
                    {new Date(s.createdAt).toLocaleString("pl-PL", {
                      day: "2-digit",
                      month: "short",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                    {" · "}
                    {s.epics.length} epikow
                  </div>
                </div>
                <ChevronRight className="h-3 w-3 text-zagi-dim transition group-hover:text-white" />
              </button>
              <button
                onClick={() => onRemove(s.id)}
                aria-label="Usun"
                className="opacity-0 transition group-hover:opacity-100 hover:text-destructive"
              >
                <Trash2 className="h-3 w-3 text-zagi-dim" />
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-zagi-surface/80 via-zagi-bg to-zagi-surface/60 p-16 text-center shadow-card-up">
      <div className="absolute inset-0 bg-mesh opacity-30" />
      <div className="relative">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 12 }}
          className="mx-auto grid h-20 w-20 place-items-center rounded-3xl bg-gradient-to-br from-zagi-crimson2 to-zagi-violet shadow-glow"
        >
          <Sparkles className="h-9 w-9 text-white" />
        </motion.div>
        <h2 className="mt-6 text-2xl font-bold text-white">Gotowy do generowania.</h2>
        <p className="mx-auto mt-2 max-w-md text-sm text-zagi-muted">
          Po lewej wpisz klucz Jira (lub kliknij <strong className="text-white">Tryb demo</strong>),
          a ZAGI rozpisze HLD, krytyke i epiki w czasie rzeczywistym.
        </p>
      </div>
    </div>
  );
}

function extractIssueKey(hld: string): string | null {
  const m = hld.match(/HLD:\s*([A-Z]+-\d+|DEMO-\d+)/i);
  return m ? m[1] : null;
}
