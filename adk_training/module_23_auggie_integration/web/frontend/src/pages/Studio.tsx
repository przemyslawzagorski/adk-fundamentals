import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cpu, Settings2, Server, Wifi, WifiOff, ChevronRight, Database, Wrench, Telescope, Activity, Code2 } from "lucide-react";
import { AmbientBackground } from "@/components/concierge/ambient-background";
import { HelpPanel } from "@/components/concierge/help-panel";
import { IndexStatusCard } from "@/components/concierge/index-status";
import { ToolCard } from "@/components/concierge/tool-card";
import { ToolRunner } from "@/components/concierge/tool-runner";
import { TelemetryPanel } from "@/components/concierge/telemetry-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useTools, useConfig } from "@/hooks/use-meta";
import { useIndexWarmup } from "@/hooks/use-index-warmup";
import { cn } from "@/lib/utils";
import type { ToolMeta } from "@/api/client";

const CATEGORIES = [
  { id: "all", label: "All Tools" },
  { id: "review", label: "Review" },
  { id: "analysis", label: "Analysis" },
  { id: "generate", label: "Generate" },
  { id: "refactor", label: "Refactor" },
  { id: "security", label: "Security" },
  { id: "general", label: "General" },
];

export function Studio() {
  const { tools } = useTools();
  const { config, refresh: refreshConfig } = useConfig();
  const warmup = useIndexWarmup();
  const [category, setCategory] = React.useState("all");
  const [activeTool, setActiveTool] = React.useState<ToolMeta | null>(null);

  // Unlock if either local warmup OR backend config reports ready
  const indexReady =
    warmup.state.status === "ready" || config?.index?.status === "ready";

  // When local warmup flips to ready, also refresh /api/config
  React.useEffect(() => {
    if (warmup.state.status === "ready") {
      refreshConfig();
    }
  }, [warmup.state.status, refreshConfig]);
  const filteredTools = category === "all" ? tools : tools.filter((t) => t.category === category);

  const toolGridRef = React.useRef<HTMLDivElement>(null);
  const scrollToTools = () => toolGridRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });

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
        {/* Top context bar */}
        <header className="mb-8 flex flex-wrap items-center justify-between gap-3">
          <div>
            <Badge variant="cyan" className="mb-2"><Code2 className="h-3 w-3" /> Module 23 · Concierge</Badge>
            <h1 className="text-3xl font-extrabold text-white md:text-4xl">
              <span className="text-gradient-azure">Concierge</span> Workspace
            </h1>
            <p className="mt-1 text-sm text-cnc-muted">
              Indeksuj repo i uruchamiaj 9 narzędzi LLM — review, security, refactor, generation, analysis.
              Wszystko lokalnie, z telemetrią i cache.
            </p>
          </div>
          {config && <ConfigBadges config={config} />}
        </header>

        <HelpPanel
          storageKey="help.studio"
          summary="Code-Analyst Studio — zaindeksuj repo, uruchom narzędzia LLM, podejrzyj telemetrię. Wszystko lokalnie."
          items={[
            { icon: Database, title: "Indexing", desc: "Krok 1: workspace → embeddings (lokalny RAG). Indeks musi być ready, by odblokować tools." },
            { icon: Wrench, title: "Tools", desc: "Review, Analysis, Generate, Refactor, Security, General — każdy z manifestem i parametrami." },
            { icon: Telescope, title: "Tool Runner", desc: "Wybierz tool, dostosuj prompt, uruchom — wynik streamowany z modelu." },
            { icon: Activity, title: "Telemetry", desc: "Tokeny, koszt, latency per request. Bez ukrytych wywołań." },
          ]}
          className="mb-8"
        />

        {/* STEP 1 — Indexing (the star) */}
        <section className="mb-8">
          <IndexStatusCard
            defaultWorkspace={config?.workspace}
            onReady={scrollToTools}
            warmup={warmup}
          />
        </section>

        {/* Telemetry */}
        <section className="mb-8">
          <TelemetryPanel />
        </section>

        {/* STEP 2 — Tool grid */}
        <section ref={toolGridRef} className="mb-12 scroll-mt-20">
          <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
            <div>
              <Badge variant={indexReady ? "success" : "muted"} className="mb-2">
                Step 2 / 2 {indexReady ? "· Ready" : "· Locked until indexed"}
              </Badge>
              <h2 className="text-2xl font-extrabold text-white md:text-3xl">
                Choose your specialist
              </h2>
              <p className="mt-1 text-sm text-cnc-muted">
                {indexReady
                  ? "Wszystkie tool'e mają teraz pełen kontekst Twojego repo."
                  : "Zaindeksuj workspace powyżej, aby odblokować tool'e."}
              </p>
            </div>
            {indexReady && (
              <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
                <ChevronRight className="h-4 w-4" /> Refresh
              </Button>
            )}
          </div>

          {/* Category pills */}
          <div className="mb-6 flex flex-wrap gap-2">
            {CATEGORIES.map((c) => (
              <button
                key={c.id}
                onClick={() => setCategory(c.id)}
                className={cn(
                  "rounded-full border px-4 py-1.5 text-xs font-bold uppercase tracking-wider transition-all",
                  category === c.id
                    ? "border-cnc-electric bg-cnc-electric/15 text-cnc-electric2 shadow-glow-sm"
                    : "border-cnc-border bg-cnc-surface/40 text-cnc-muted hover:border-cnc-electric/50 hover:text-cnc-ink",
                )}
              >
                {c.label}
              </button>
            ))}
          </div>

          {/* Grid */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredTools.length === 0 && tools.length > 0 && (
              <Card className="col-span-full p-8 text-center text-cnc-muted">
                Brak tool'ów w kategorii <b className="text-cnc-ink">{category}</b>.
              </Card>
            )}
            {filteredTools.map((tool) => (
              <ToolCard
                key={tool.id}
                tool={tool}
                locked={!indexReady}
                onClick={() => setActiveTool(tool)}
              />
            ))}
            {tools.length === 0 && (
              <Card className="col-span-full animate-pulse p-12 text-center text-cnc-muted">
                Loading tools…
              </Card>
            )}
          </div>
        </section>
      </div>

      {/* Tool runner modal */}
      <AnimatePresence>
        {activeTool && (
          <ToolRunner tool={activeTool} onClose={() => setActiveTool(null)} />
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function ConfigBadges({ config }: { config: NonNullable<ReturnType<typeof useConfig>["config"]> }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant="muted">
        <Cpu className="h-3 w-3" />
        {config.model}
      </Badge>
      <Badge variant={config.has_session_auth ? "success" : "warning"}>
        {config.has_session_auth ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
        {config.has_session_auth ? "Authenticated" : "No session"}
      </Badge>
      <Badge variant={config.use_cli_fallback ? "warning" : "azure"}>
        <Server className="h-3 w-3" />
        {config.use_cli_fallback ? "CLI fallback" : "ACP SDK"}
      </Badge>
      <Badge variant="outline">
        <Settings2 className="h-3 w-3" />
        {config.platform}
      </Badge>
    </div>
  );
}
