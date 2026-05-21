import * as React from "react";
import { motion } from "framer-motion";
import {
  BookOpen, Brain, Database, ShieldAlert, FileText, RefreshCw,
  ChevronRight, ExternalLink, History, Sparkles, FileSearch, Tag,
} from "lucide-react";
import { AmbientBackground } from "@/components/concierge/ambient-background";
import { HelpPanel } from "@/components/concierge/help-panel";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  listSkills, fetchSkill, listWikiTargets, fetchWikiIndex, fetchWikiLint,
  type SkillManifest, type SkillDetail, type WikiTarget, type WikiLintReport,
} from "@/api/audit-client";
import { cn } from "@/lib/utils";

type Tab = "skills" | "wiki";

export function Knowledge() {
  const [tab, setTab] = React.useState<Tab>("skills");

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
        <header className="mb-6">
          <Badge variant="cyan" className="mb-2">
            <Brain className="h-3 w-3" /> Knowledge
          </Badge>
          <h1 className="text-3xl font-extrabold text-white md:text-4xl">
            Skills <span className="text-gradient-azure">&</span> Wiki
          </h1>
          <p className="mt-1 text-sm text-cnc-muted">
            Progressive-disclosure OWASP skills (V1) i pamięć instytucjonalna per-target (V2/V3).
            Wszystko, czym karmiony jest planner — przejrzyste i audytowalne.
          </p>
        </header>

        <HelpPanel
          storageKey="help.knowledge"
          summary="Przeglądaj OWASP skills wstrzykiwane do plannera oraz wiki audytów dla każdego targetu."
          items={[
            { icon: BookOpen, title: "Manifest L1", desc: "Lista 5 wbudowanych skills (recon-helpers + A01/A02/A03/A05) z opisami i triggerami." },
            { icon: FileText, title: "Instrukcja L2", desc: "Pełne SKILL.md — co LLM zobaczy w prompcie, gdy trigger zostanie spełniony." },
            { icon: FileSearch, title: "Referencje L3", desc: "Szablony payloadów i fingerprinty (np. SQLi error patterns) — ładowane na żądanie." },
            { icon: Database, title: "Wiki per-target", desc: "Indeks, runs, findings, log i synthesis dla każdego audytowanego hosta." },
            { icon: History, title: "Audit-history skill", desc: "Wiki streszczane do plannera przy kolejnym runie — model nie odkrywa CSP od zera." },
            { icon: ShieldAlert, title: "Wiki lint", desc: "Walidacja spójności — broken_link, missing_run_stub. Zielone w CI = ok." },
          ]}
          footer={
            <>
              <strong className="text-white">Zasada:</strong> Python pisze wiki, nigdy LLM.
              Synthesis (LLM-generated) jest gated przez HITL (<code>accept=true</code>).
            </>
          }
          className="mb-6"
        />

        {/* Tabs */}
        <div className="mb-6 inline-flex rounded-xl border border-cnc-border bg-cnc-surface/40 p-1">
          {(["skills", "wiki"] as Tab[]).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={cn(
                "rounded-lg px-4 py-2 text-sm font-semibold transition-colors",
                tab === t ? "bg-cnc-electric/20 text-white" : "text-cnc-muted hover:text-cnc-ink",
              )}
            >
              {t === "skills" ? "Skills" : "Wiki"}
            </button>
          ))}
        </div>

        {tab === "skills" ? <SkillsPanel /> : <WikiPanel />}
      </div>
    </motion.div>
  );
}

// ---------------------------- Skills ----------------------------

function SkillsPanel() {
  const [skills, setSkills] = React.useState<SkillManifest[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [selected, setSelected] = React.useState<string | null>(null);
  const [detail, setDetail] = React.useState<SkillDetail | null>(null);
  const [detailLoading, setDetailLoading] = React.useState(false);

  React.useEffect(() => {
    listSkills()
      .then((r) => setSkills(r.skills))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  React.useEffect(() => {
    if (!selected) {
      setDetail(null);
      return;
    }
    setDetailLoading(true);
    fetchSkill(selected)
      .then(setDetail)
      .catch((e) => setError(String(e)))
      .finally(() => setDetailLoading(false));
  }, [selected]);

  if (loading) return <Loading label="Loading skills…" />;
  if (error) return <ErrorBox message={error} />;
  if (skills.length === 0) {
    return <EmptyBox title="Brak skills" desc="Sprawdź folder skills/ w module_24_audit_ops." />;
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
      <div className="space-y-3">
        {skills.map((s) => (
          <Card
            key={s.name}
            onClick={() => setSelected(s.name)}
            className={cn(
              "cursor-pointer p-4 transition-all hover:border-cnc-electric/50",
              selected === s.name && "border-cnc-electric/70 ring-1 ring-cnc-electric/30",
            )}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="font-mono text-sm font-bold text-white">{s.name}</div>
                <p className="mt-1 text-xs leading-relaxed text-cnc-muted">{s.description}</p>
              </div>
              <ChevronRight className="h-4 w-4 shrink-0 text-cnc-muted" />
            </div>
            <div className="mt-3 flex flex-wrap gap-1">
              {s.triggers.map((t) => (
                <Badge key={t} variant="muted" className="text-[10px]">
                  <Tag className="h-2.5 w-2.5" />
                  {t}
                </Badge>
              ))}
            </div>
            {s.resources.length > 0 && (
              <div className="mt-2 text-[10px] text-cnc-muted">
                {s.resources.length} resource{s.resources.length === 1 ? "" : "s"}
              </div>
            )}
          </Card>
        ))}
      </div>

      <div>
        {!selected && (
          <Card className="flex h-full items-center justify-center p-8">
            <div className="text-center text-sm text-cnc-muted">
              <Sparkles className="mx-auto mb-2 h-8 w-8 text-cnc-electric/60" />
              Wybierz skill po lewej, aby zobaczyć pełną treść SKILL.md (L2).
            </div>
          </Card>
        )}
        {selected && detailLoading && <Loading label="Loading SKILL.md…" />}
        {selected && detail && <SkillDetailView detail={detail} />}
      </div>
    </div>
  );
}

function SkillDetailView({ detail }: { detail: SkillDetail }) {
  return (
    <Card className="p-6">
      <div className="mb-4">
        <div className="mb-1 font-mono text-base font-bold text-white">{detail.name}</div>
        <p className="text-sm text-cnc-muted">{detail.description}</p>
      </div>

      {detail.resources.length > 0 && (
        <div className="mb-4">
          <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-cnc-muted">L3 Resources</div>
          <div className="flex flex-wrap gap-1.5">
            {detail.resources.map((r) => (
              <a
                key={r}
                href={`/api/audit/skills/${encodeURIComponent(detail.name)}/resource?path=${encodeURIComponent(r)}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 rounded-md border border-cnc-border bg-cnc-surface/60 px-2 py-1 text-xs font-mono text-cnc-cyan2 hover:border-cnc-cyan/40"
              >
                {r}
                <ExternalLink className="h-3 w-3" />
              </a>
            ))}
          </div>
        </div>
      )}

      <div>
        <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-cnc-muted">L2 Instructions</div>
        <pre className="max-h-[60vh] overflow-auto rounded-lg border border-cnc-border bg-black/40 p-4 text-xs leading-relaxed text-cnc-ink whitespace-pre-wrap">
          {detail.instructions}
        </pre>
      </div>
    </Card>
  );
}

// ---------------------------- Wiki ----------------------------

function WikiPanel() {
  const [targets, setTargets] = React.useState<WikiTarget[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [selected, setSelected] = React.useState<string | null>(null);
  const [indexMd, setIndexMd] = React.useState<string>("");
  const [lint, setLint] = React.useState<WikiLintReport | null>(null);
  const [detailLoading, setDetailLoading] = React.useState(false);

  const refresh = React.useCallback(() => {
    setLoading(true);
    listWikiTargets()
      .then((r) => setTargets(r.targets))
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  React.useEffect(() => {
    refresh();
  }, [refresh]);

  React.useEffect(() => {
    if (!selected) {
      setIndexMd("");
      setLint(null);
      return;
    }
    setDetailLoading(true);
    Promise.all([fetchWikiIndex(selected), fetchWikiLint(selected)])
      .then(([md, lr]) => {
        setIndexMd(md);
        setLint(lr);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setDetailLoading(false));
  }, [selected]);

  if (loading) return <Loading label="Loading wiki…" />;
  if (error) return <ErrorBox message={error} />;
  if (targets.length === 0) {
    return (
      <EmptyBox
        title="Wiki jest pusta"
        desc="Po pierwszym audycie wiki pojawi się tutaj automatycznie. Uruchom run z zakładki Audit."
      />
    );
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wide text-cnc-muted">
            {targets.length} target{targets.length === 1 ? "" : "s"}
          </span>
          <Button variant="ghost" size="sm" onClick={refresh}>
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </Button>
        </div>
        {targets.map((t) => (
          <Card
            key={t.slug}
            onClick={() => setSelected(t.slug)}
            className={cn(
              "cursor-pointer p-4 transition-all hover:border-cnc-electric/50",
              selected === t.slug && "border-cnc-electric/70 ring-1 ring-cnc-electric/30",
            )}
          >
            <div className="font-mono text-sm font-bold text-white">{t.slug}</div>
            <div className="mt-2 flex gap-2">
              <Badge variant="cyan">{t.runs} runs</Badge>
              <Badge variant="warning">{t.findings} findings</Badge>
            </div>
          </Card>
        ))}
      </div>

      <div>
        {!selected && (
          <Card className="flex h-full items-center justify-center p-8">
            <div className="text-center text-sm text-cnc-muted">
              <Database className="mx-auto mb-2 h-8 w-8 text-cnc-electric/60" />
              Wybierz target, aby zobaczyć indeks wiki + raport lint.
            </div>
          </Card>
        )}
        {selected && detailLoading && <Loading label="Loading wiki index…" />}
        {selected && !detailLoading && (
          <Card className="p-6">
            <CardHeader className="!p-0 mb-4">
              <CardTitle className="font-mono">{selected}</CardTitle>
              <CardDescription>
                Indeks generowany przez Pythona z każdym runem · idempotentny merge findings
              </CardDescription>
            </CardHeader>
            <CardContent className="!p-0 space-y-4">
              {lint && (
                <div
                  className={cn(
                    "rounded-lg border p-3 text-xs",
                    lint.issues.length === 0
                      ? "border-emerald-500/30 bg-emerald-500/5 text-emerald-300"
                      : "border-cnc-rose/40 bg-cnc-rose/5 text-cnc-rose",
                  )}
                >
                  {lint.issues.length === 0 ? (
                    <>✓ Wiki lint: <strong>clean</strong> — brak broken_link, brak missing_run_stub.</>
                  ) : (
                    <>
                      <div className="mb-1 font-semibold">⚠ {lint.issues.length} issue(s):</div>
                      <ul className="ml-4 list-disc space-y-0.5">
                        {lint.issues.map((i, idx) => (
                          <li key={idx}>
                            <code>{i.kind}</code> · <code>{i.path}</code> · {i.detail}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              )}

              <div>
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-cnc-muted">
                  index.md
                </div>
                <pre className="max-h-[55vh] overflow-auto rounded-lg border border-cnc-border bg-black/40 p-4 text-xs leading-relaxed text-cnc-ink whitespace-pre-wrap">
                  {indexMd}
                </pre>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

// ---------------------------- helpers ----------------------------

function Loading({ label }: { label: string }) {
  return (
    <Card className="flex items-center justify-center gap-2 p-8 text-sm text-cnc-muted">
      <RefreshCw className="h-4 w-4 animate-spin" />
      {label}
    </Card>
  );
}

function ErrorBox({ message }: { message: string }) {
  return (
    <Card className="border-cnc-rose/40 bg-cnc-rose/5 p-6 text-sm text-cnc-rose">
      <div className="font-semibold">Error</div>
      <div className="mt-1 font-mono text-xs">{message}</div>
    </Card>
  );
}

function EmptyBox({ title, desc }: { title: string; desc: string }) {
  return (
    <Card className="p-8 text-center text-sm text-cnc-muted">
      <Sparkles className="mx-auto mb-2 h-8 w-8 text-cnc-electric/60" />
      <div className="font-semibold text-white">{title}</div>
      <div className="mt-1 text-xs">{desc}</div>
    </Card>
  );
}
