import * as React from "react";
import { motion } from "framer-motion";
import {
  Brain,
  CheckCircle2,
  ClipboardList,
  FileText,
  Loader2,
  Network,
  PlayCircle,
  Sparkles,
  Send,
  AlertTriangle,
  RefreshCw,
  ListTree,
  BookOpen,
} from "lucide-react";
import { AmbientBackground } from "@/components/concierge/ambient-background";
import { HelpPanel } from "@/components/concierge/help-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  fetchAnalystConfig,
  fetchAnalystSession,
  startAnalystGenerate,
  publishJira,
  publishConfluence,
  type AnalystConfig,
  type AnalystEpic,
  type AnalystEvent,
  type AnalystSession,
  type AnalystStage,
} from "@/api/analyst-client";

const STAGE_META: Record<AnalystStage, { label: string; icon: typeof Brain }> = {
  ticket_fetcher: { label: "Pobranie ticketu", icon: ClipboardList },
  context_gatherer: { label: "Kontekst (wiki + domena)", icon: Network },
  hld_writer: { label: "HLD draft", icon: FileText },
  critique_loop: { label: "Samokrytyka", icon: RefreshCw },
  epic_decomposer: { label: "Dekompozycja na epiki", icon: ListTree },
};

const ALL_STAGES: AnalystStage[] = [
  "ticket_fetcher",
  "context_gatherer",
  "hld_writer",
  "critique_loop",
  "epic_decomposer",
];

interface StageState {
  active: boolean;
  done: boolean;
}

export function Analyst() {
  const [config, setConfig] = React.useState<AnalystConfig | null>(null);
  const [issueKey, setIssueKey] = React.useState("");
  const [maxIter, setMaxIter] = React.useState(3);
  const [enableNblm, setEnableNblm] = React.useState<boolean>(false);
  const [nblmUrl, setNblmUrl] = React.useState<string>("");
  const [running, setRunning] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [sessionId, setSessionId] = React.useState<string | null>(null);
  const [session, setSession] = React.useState<AnalystSession | null>(null);
  const [stages, setStages] = React.useState<Record<AnalystStage, StageState>>(() =>
    Object.fromEntries(ALL_STAGES.map((s) => [s, { active: false, done: false }])) as any,
  );
  const [liveText, setLiveText] = React.useState<Partial<Record<AnalystStage, string>>>({});
  const [editedEpics, setEditedEpics] = React.useState<AnalystEpic[]>([]);
  const [editedEpicsRaw, setEditedEpicsRaw] = React.useState<string>("");
  const [projectKey, setProjectKey] = React.useState("");
  const [parentKey, setParentKey] = React.useState("");
  const [confSpaceKey, setConfSpaceKey] = React.useState("");
  const [confTitle, setConfTitle] = React.useState("");
  const [confParentId, setConfParentId] = React.useState("");
  const [confLabels, setConfLabels] = React.useState("");
  const [publishing, setPublishing] = React.useState<"jira" | "wiki" | null>(null);
  const [publishMsg, setPublishMsg] = React.useState<string | null>(null);

  React.useEffect(() => {
    fetchAnalystConfig()
      .then((c) => {
        setConfig(c);
        setMaxIter(c.defaults.max_critique_iterations);
        setEnableNblm(c.notebooklm.enabled);
        if (c.notebooklm.notebook_url) setNblmUrl(c.notebooklm.notebook_url);
      })
      .catch((e) => console.warn("analyst/config failed", e));
  }, []);

  // Sync edited epics when session loads/changes.
  React.useEffect(() => {
    if (session?.epics) {
      setEditedEpics(session.epics);
      setEditedEpicsRaw(JSON.stringify(session.epics, null, 2));
      if (!confTitle && session.current_hld) {
        setConfTitle(`HLD: ${session.issue_key}`);
      }
    }
  }, [session?.id]);

  function resetState() {
    setError(null);
    setSession(null);
    setSessionId(null);
    setLiveText({});
    setStages(
      Object.fromEntries(ALL_STAGES.map((s) => [s, { active: false, done: false }])) as any,
    );
    setEditedEpics([]);
    setEditedEpicsRaw("");
    setPublishMsg(null);
  }

  async function handleStart() {
    if (!issueKey.trim()) return;
    resetState();
    setRunning(true);
    let sid: string | null = null;
    const handle = startAnalystGenerate({
      issue_key: issueKey.trim(),
      max_critique_iterations: maxIter,
      enable_notebooklm: enableNblm,
      notebooklm_url: nblmUrl || undefined,
      onEvent: (ev: AnalystEvent) => {
        if (ev.type === "session_start") sid = ev.session_id;
        else if (ev.type === "stage_active") {
          setStages((prev) => {
            const next = { ...prev };
            // mark previous active stages as done
            for (const s of ALL_STAGES) {
              if (s === ev.stage) {
                next[s] = { active: true, done: false };
                break;
              } else if (next[s].active) {
                next[s] = { active: false, done: true };
              }
            }
            return next;
          });
        } else if (ev.type === "text" && ev.stage) {
          setLiveText((prev) => ({
            ...prev,
            [ev.stage as AnalystStage]: (prev[ev.stage as AnalystStage] ?? "") + ev.text,
          }));
        } else if (ev.type === "done") {
          // mark all reached stages as done
          setStages((prev) => {
            const next = { ...prev };
            for (const s of ALL_STAGES) {
              if (next[s].active) next[s] = { active: false, done: true };
            }
            return next;
          });
          sid = ev.session_id;
        } else if (ev.type === "error") {
          setError(ev.message ?? "unknown error");
        }
      },
      onError: (e) => setError(e.message),
    });
    await handle.done;
    setRunning(false);
    if (sid) {
      setSessionId(sid);
      try {
        const full = await fetchAnalystSession(sid);
        setSession(full);
      } catch (e: any) {
        setError(e?.message ?? "failed to load session");
      }
    }
  }

  function applyEditedJson() {
    try {
      const parsed = JSON.parse(editedEpicsRaw);
      const arr: AnalystEpic[] = Array.isArray(parsed) ? parsed : (parsed.epics ?? []);
      setEditedEpics(arr);
      setError(null);
    } catch (e: any) {
      setError(`Invalid epics JSON: ${e.message}`);
    }
  }

  async function handlePublishJira() {
    if (!sessionId || !projectKey.trim() || editedEpics.length === 0) return;
    setPublishing("jira");
    setPublishMsg(null);
    try {
      const result = await publishJira(sessionId, {
        project_key: projectKey.trim().toUpperCase(),
        epics: editedEpics,
        parent_key: parentKey.trim() || undefined,
      });
      setPublishMsg(
        result.ok
          ? `✓ Utworzono ${result.created.length} epików w Jira (${result.created.map((c) => c.key).join(", ")})`
          : `Częściowy sukces: utworzono ${result.created.length}, nieudane ${result.failures.length}: ${result.failures
              .map((f) => f.error)
              .join("; ")}`,
      );
      // reload session to show published artifacts
      const full = await fetchAnalystSession(sessionId);
      setSession(full);
    } catch (e: any) {
      setError(e?.message ?? "publish jira failed");
    } finally {
      setPublishing(null);
    }
  }

  async function handlePublishConfluence() {
    if (!sessionId || !confSpaceKey.trim() || !confTitle.trim()) return;
    setPublishing("wiki");
    setPublishMsg(null);
    try {
      const labels = confLabels
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const result = await publishConfluence(sessionId, {
        space_key: confSpaceKey.trim().toUpperCase(),
        title: confTitle.trim(),
        parent_id: confParentId.trim() || undefined,
        labels: labels.length ? labels : undefined,
      });
      setPublishMsg(
        result.ok ? `✓ Strona Confluence: ${result.page.title} (id ${result.page.id})` : "Confluence publish nieudany",
      );
      const full = await fetchAnalystSession(sessionId);
      setSession(full);
    } catch (e: any) {
      setError(e?.message ?? "publish confluence failed");
    } finally {
      setPublishing(null);
    }
  }

  const jiraReady = config?.jira.configured ?? false;
  const wikiReady = config?.confluence.configured ?? false;

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
        <header className="mb-8 flex flex-wrap items-center justify-between gap-3">
          <div>
            <Badge variant="cyan" className="mb-2">
              <Brain className="h-3 w-3" /> Analyst
            </Badge>
            <h1 className="text-3xl font-extrabold text-white md:text-4xl">
              Jira ticket → <span className="text-gradient-azure">HLD + epiki</span>
            </h1>
            <p className="mt-1 text-sm text-cnc-muted">
              Pipeline ADK: pobranie ticketu z Jira DC → kontekst (Confluence + NotebookLM)
              → HLD z samokrytyką → 3-7 epików gotowych do publikacji.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant={jiraReady ? "cyan" : "warning"}>
              Jira: {jiraReady ? "gotowe" : "skonfiguruj JIRA_DC_*"}
            </Badge>
            <Badge variant={wikiReady ? "cyan" : "warning"}>
              Confluence: {wikiReady ? "gotowe" : "skonfiguruj CONFLUENCE_DC_*"}
            </Badge>
            <Badge variant={config?.notebooklm.enabled ? "cyan" : "default"}>
              NotebookLM: {config?.notebooklm.enabled ? "wł." : "wył."}
            </Badge>
          </div>
        </header>

        <HelpPanel
          storageKey="help.analyst"
          summary="Wprowadź klucz ticketu Jira, dostań HLD + propozycję epików — zatwierdź i opublikuj."
          items={[
            { icon: ClipboardList, title: "Ticket Fetcher", desc: "Pobiera opis i komentarze z Jira DC przez REST (PAT)." },
            { icon: Network, title: "Context Gatherer", desc: "Równolegle: CQL search w Confluence + NotebookLM (opcj.)." },
            { icon: FileText, title: "HLD Writer", desc: "Tworzy 12-sekcyjny HLD wg sztywnego szablonu." },
            { icon: RefreshCw, title: "Critique Loop", desc: "Critic→Reviser do `LGTM` lub max N iteracji." },
            { icon: ListTree, title: "Epic Decomposer", desc: "Rozbija HLD na 3-7 epików (JSON, edytowalny)." },
            { icon: Send, title: "HITL Publish", desc: "Akceptujesz w UI → Jira create_issue + Confluence create_page." },
          ]}
          footer={
            <>
              <strong className="text-white">Bez MCP:</strong> bezpośrednie REST do Jira/Confluence
              (mniej tokenów, niższa latencja). Klucze PAT w <code>.env</code> modułu_20.
            </>
          }
          className="mb-6"
        />

        {/* INPUT FORM */}
        <Card className="mb-6 p-5">
          <div className="grid gap-4 md:grid-cols-[1fr_auto_auto] md:items-end">
            <div>
              <Label htmlFor="issue_key">Klucz ticketu Jira</Label>
              <Input
                id="issue_key"
                value={issueKey}
                onChange={(e) => setIssueKey(e.target.value.toUpperCase())}
                placeholder="np. SWOK-1234"
                disabled={running}
              />
            </div>
            <div>
              <Label htmlFor="iter">Max iteracji krytyki</Label>
              <Input
                id="iter"
                type="number"
                min={1}
                max={5}
                value={maxIter}
                onChange={(e) => setMaxIter(Math.max(1, Math.min(5, Number(e.target.value) || 3)))}
                disabled={running}
                className="w-28"
              />
            </div>
            <Button onClick={handleStart} disabled={running || !issueKey.trim() || !jiraReady}>
              {running ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> Generowanie...
                </>
              ) : (
                <>
                  <PlayCircle className="h-4 w-4" /> Uruchom pipeline
                </>
              )}
            </Button>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="flex items-center gap-2 text-sm text-cnc-muted">
              <input
                type="checkbox"
                checked={enableNblm}
                onChange={(e) => setEnableNblm(e.target.checked)}
                disabled={running}
                className="h-4 w-4 rounded border-cnc-border bg-cnc-surface accent-cnc-electric"
              />
              Użyj NotebookLM (Playwright/Computer Use)
            </label>
            {enableNblm && (
              <div>
                <Input
                  value={nblmUrl}
                  onChange={(e) => setNblmUrl(e.target.value)}
                  placeholder="NotebookLM notebook URL (https://notebooklm.google.com/notebook/...)"
                  disabled={running}
                />
              </div>
            )}
          </div>
        </Card>

        {/* PIPELINE STATUS */}
        {(running || session) && (
          <Card className="mb-6 p-5">
            <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-cnc-muted">
              <Sparkles className="h-4 w-4 text-cnc-electric2" /> Postęp pipeline'u
            </h2>
            <ol className="grid gap-2 md:grid-cols-5">
              {ALL_STAGES.map((s) => {
                const meta = STAGE_META[s];
                const Icon = meta.icon;
                const st = stages[s];
                return (
                  <li
                    key={s}
                    className={[
                      "rounded-xl border px-3 py-2 transition-colors",
                      st.done
                        ? "border-emerald-500/40 bg-emerald-500/5"
                        : st.active
                        ? "border-cnc-electric/60 bg-cnc-electric/10 animate-pulse"
                        : "border-cnc-border/60 bg-cnc-surface/30",
                    ].join(" ")}
                  >
                    <div className="flex items-center gap-2 text-xs font-semibold text-white">
                      {st.done ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                      ) : st.active ? (
                        <Loader2 className="h-4 w-4 animate-spin text-cnc-electric2" />
                      ) : (
                        <Icon className="h-4 w-4 text-cnc-muted" />
                      )}
                      {meta.label}
                    </div>
                  </li>
                );
              })}
            </ol>
          </Card>
        )}

        {error && (
          <Card className="mb-6 border-rose-500/50 bg-rose-950/30 p-4">
            <div className="flex items-start gap-2 text-sm text-rose-200">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              <pre className="whitespace-pre-wrap font-mono text-xs">{error}</pre>
            </div>
          </Card>
        )}

        {/* RESULTS */}
        {session && session.status !== "running" && (
          <div className="grid gap-6 lg:grid-cols-2">
            {/* HLD */}
            <Card className="p-5">
              <header className="mb-3 flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-cnc-muted">
                  <FileText className="h-4 w-4 text-cnc-electric2" /> HLD ({session.current_hld.length} znaków)
                </h2>
                <Badge variant="cyan">{session.issue_key}</Badge>
              </header>
              <Textarea
                value={session.current_hld}
                onChange={(e) =>
                  setSession((prev) => (prev ? { ...prev, current_hld: e.target.value } : prev))
                }
                rows={20}
                className="font-mono text-xs"
              />
            </Card>

            {/* EPICS */}
            <Card className="p-5">
              <header className="mb-3 flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-cnc-muted">
                  <ListTree className="h-4 w-4 text-cnc-electric2" /> Epiki ({editedEpics.length})
                </h2>
                <Button size="sm" variant="outline" onClick={applyEditedJson}>
                  Zastosuj edycję JSON
                </Button>
              </header>
              <Textarea
                value={editedEpicsRaw}
                onChange={(e) => setEditedEpicsRaw(e.target.value)}
                rows={20}
                className="font-mono text-xs"
              />
              {editedEpics.length > 0 && (
                <ul className="mt-3 space-y-1 text-xs text-cnc-muted">
                  {editedEpics.map((e, i) => (
                    <li key={i} className="truncate">
                      <span className="font-semibold text-white">{i + 1}.</span> {e.title}{" "}
                      <span className="text-cnc-muted/70">
                        [{e.estimate_t_shirt ?? "?"} · {e.priority ?? "?"}]
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            {/* PUBLISH JIRA */}
            <Card className="p-5">
              <header className="mb-3 flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-cnc-muted">
                  <Send className="h-4 w-4 text-cnc-electric2" /> Publikacja → Jira
                </h2>
                <Badge variant={jiraReady ? "cyan" : "warning"}>
                  {jiraReady ? "klient OK" : "brak konfiguracji"}
                </Badge>
              </header>
              <div className="grid gap-3">
                <div>
                  <Label htmlFor="proj">Projekt (klucz)</Label>
                  <Input
                    id="proj"
                    value={projectKey}
                    onChange={(e) => setProjectKey(e.target.value.toUpperCase())}
                    placeholder="SWOK"
                  />
                </div>
                <div>
                  <Label htmlFor="parent">Parent (opc.)</Label>
                  <Input
                    id="parent"
                    value={parentKey}
                    onChange={(e) => setParentKey(e.target.value.toUpperCase())}
                    placeholder="np. SWOK-1000 (Inicjatywa)"
                  />
                </div>
                <Button
                  onClick={handlePublishJira}
                  disabled={
                    !jiraReady ||
                    !projectKey.trim() ||
                    editedEpics.length === 0 ||
                    publishing !== null
                  }
                >
                  {publishing === "jira" ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> Publikuję {editedEpics.length} epików...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" /> Utwórz {editedEpics.length} epików w Jira
                    </>
                  )}
                </Button>
                {session.published_jira && session.published_jira.length > 0 && (
                  <ul className="mt-2 space-y-1 text-xs text-emerald-300">
                    {session.published_jira.map((p) => (
                      <li key={p.key}>
                        ✓{" "}
                        <a href={p.url} target="_blank" rel="noreferrer" className="underline">
                          {p.key}
                        </a>{" "}
                        — {p.title}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </Card>

            {/* PUBLISH CONFLUENCE */}
            <Card className="p-5">
              <header className="mb-3 flex items-center justify-between">
                <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-cnc-muted">
                  <BookOpen className="h-4 w-4 text-cnc-electric2" /> Publikacja → Confluence
                </h2>
                <Badge variant={wikiReady ? "cyan" : "warning"}>
                  {wikiReady ? "klient OK" : "brak konfiguracji"}
                </Badge>
              </header>
              <div className="grid gap-3">
                <div>
                  <Label htmlFor="space">Space key</Label>
                  <Input
                    id="space"
                    value={confSpaceKey}
                    onChange={(e) => setConfSpaceKey(e.target.value.toUpperCase())}
                    placeholder="np. ARCH"
                  />
                </div>
                <div>
                  <Label htmlFor="title">Tytuł strony</Label>
                  <Input
                    id="title"
                    value={confTitle}
                    onChange={(e) => setConfTitle(e.target.value)}
                  />
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <div>
                    <Label htmlFor="cparent">Parent ID (opc.)</Label>
                    <Input
                      id="cparent"
                      value={confParentId}
                      onChange={(e) => setConfParentId(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="clabels">Etykiety (CSV)</Label>
                    <Input
                      id="clabels"
                      value={confLabels}
                      onChange={(e) => setConfLabels(e.target.value)}
                      placeholder="hld,ai-generated"
                    />
                  </div>
                </div>
                <Button
                  onClick={handlePublishConfluence}
                  disabled={!wikiReady || !confSpaceKey.trim() || !confTitle.trim() || publishing !== null}
                >
                  {publishing === "wiki" ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> Publikuję HLD...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" /> Opublikuj HLD
                    </>
                  )}
                </Button>
                {session.published_confluence && (
                  <p className="text-xs text-emerald-300">
                    ✓ Strona:{" "}
                    {session.published_confluence.url ? (
                      <a
                        href={session.published_confluence.url}
                        target="_blank"
                        rel="noreferrer"
                        className="underline"
                      >
                        {session.published_confluence.title}
                      </a>
                    ) : (
                      session.published_confluence.title
                    )}{" "}
                    (v{session.published_confluence.version})
                  </p>
                )}
              </div>
            </Card>

            {publishMsg && (
              <Card className="lg:col-span-2 border-cnc-electric/40 bg-cnc-electric/10 p-4">
                <p className="text-sm text-cnc-ink">{publishMsg}</p>
              </Card>
            )}

            {/* CONTEXT (debug / explainability) */}
            {(session.wiki_context || session.domain_context) && (
              <Card className="lg:col-span-2 p-5">
                <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-cnc-muted">
                  <Network className="h-4 w-4 text-cnc-electric2" /> Zebrany kontekst (input do HLD)
                </h2>
                {session.wiki_context && (
                  <details className="mb-2 rounded-lg border border-cnc-border/40 bg-cnc-surface/30 p-3">
                    <summary className="cursor-pointer text-xs font-semibold text-cnc-muted">
                      wiki_context ({session.wiki_context.length} znaków)
                    </summary>
                    <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap font-mono text-xs text-cnc-ink">
                      {session.wiki_context}
                    </pre>
                  </details>
                )}
                {session.domain_context && (
                  <details className="rounded-lg border border-cnc-border/40 bg-cnc-surface/30 p-3">
                    <summary className="cursor-pointer text-xs font-semibold text-cnc-muted">
                      domain_context ({session.domain_context.length} znaków)
                    </summary>
                    <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap font-mono text-xs text-cnc-ink">
                      {session.domain_context}
                    </pre>
                  </details>
                )}
              </Card>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default Analyst;
