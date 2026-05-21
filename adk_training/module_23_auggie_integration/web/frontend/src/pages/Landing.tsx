import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  ArrowRight, Sparkles, Database, Zap, Shield, GitBranch, Microscope, ShieldAlert,
  Rocket, Code2, Cpu, Lock, Workflow, BookOpen, Radar, Brain, Camera, FileText,
  Layers,
} from "lucide-react";
import { AmbientBackground } from "@/components/concierge/ambient-background";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

const conciergeFeatures = [
  { icon: Database, title: "Indexed Workspace", desc: "Augment buduje semantyczny index repo (vector + AST). Każdy tool widzi pełen kontekst.", accent: "electric" },
  { icon: Workflow, title: "9 Production Tools", desc: "Code review, security audit, refactor, generation, analysis — wszystko jako ADK tools.", accent: "cyan" },
  { icon: Zap, title: "11 937× Speedup", desc: "Inteligentny cache: pierwsze wywołanie 12s, kolejne 1ms. Zmierzony, nie estymowany.", accent: "gold" },
  { icon: Shield, title: "Resilience by Design", desc: "Circuit breaker, exponential backoff, retry-after-429, telemetry. Production-grade.", accent: "azure" },
  { icon: Cpu, title: "Cross-Platform", desc: "Windows + WSL + Linux. Auggie SDK (ACP) + CLI fallback. 22 native tools dostępne.", accent: "electric" },
  { icon: Lock, title: "Service-Account Auth", desc: "Bez przechwytywania OAuth flow. Skopiuj session.json — działa headless w CI.", accent: "cyan" },
];

const auditFeatures = [
  { icon: Radar, title: "Recon-First", desc: "DOM snapshot, formularze, security headers, /robots.txt — bez interakcji ofensywnej.", accent: "cyan" },
  { icon: Brain, title: "OWASP Skills V1", desc: "5 progresywnie ujawnianych skills (recon-helpers + A01/A02/A03/A05). Manifest L1, instrukcja L2, payloady L3.", accent: "electric" },
  { icon: Camera, title: "Playwright Evidence", desc: "Każdy krok z artefaktami: wideo, screenshoty, request log. Reprodukowalne dowody.", accent: "azure" },
  { icon: FileText, title: "OWASP Findings", desc: "Tagged findings z severity, evidence, remediation. JSON + Markdown raport.", accent: "gold" },
  { icon: BookOpen, title: "Wiki per-target", desc: "V2/V3 pamięć instytucjonalna — kolejny audyt rusza z kontekstem (history skill).", accent: "cyan" },
  { icon: ShieldAlert, title: "Safety Gates", desc: "Allowlist domen, disclaimer modal, depth limit, rate-limit. Tylko autoryzowane cele.", accent: "electric" },
];

const accents: Record<string, string> = {
  electric: "from-cnc-electric/20 to-transparent text-cnc-electric2",
  cyan: "from-cnc-cyan/20 to-transparent text-cnc-cyan2",
  azure: "from-cnc-azure/30 to-transparent text-cnc-electric2",
  gold: "from-cnc-gold/20 to-transparent text-cnc-gold",
};

export function Landing() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="relative"
    >
      <AmbientBackground />

      {/* HERO */}
      <section className="container relative pt-20 pb-24 md:pt-32 md:pb-32">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.2, 0.8, 0.2, 1] }}
          className="mx-auto max-w-5xl text-center"
        >
          <Badge variant="cyan" className="mb-6 px-4 py-1.5 text-xs">
            <Sparkles className="h-3.5 w-3.5" />
            Modules 23 + 24 · ADK Platform
          </Badge>

          <h1 className="text-balance text-5xl font-black leading-[1.05] tracking-tight md:text-7xl lg:text-8xl">
            <span className="block text-white">ADK Fundamentals</span>
            <span className="block text-gradient-azure animate-gradient">Platform</span>
          </h1>

          <p className="mx-auto mt-8 max-w-3xl text-pretty text-lg text-cnc-muted md:text-xl">
            Dwa produkcyjne agenty AI w jednym workflow.{" "}
            <b className="text-white">AI Code Concierge</b> indeksuje repo i uruchamia 9 narzędzi LLM.{" "}
            <b className="text-white">AuditOps</b> przeprowadza audyt OWASP webapki z dowodami wideo.
            Wspólna infrastruktura: cache, telemetria, circuit breaker, MCP.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
            <Button size="xl" asChild>
              <Link to="/studio">
                <Rocket className="h-5 w-5" />
                Open Studio
                <ArrowRight className="h-5 w-5" />
              </Link>
            </Button>
            <Button size="xl" variant="outline" asChild>
              <Link to="/audit">
                <Shield className="h-5 w-5" />
                Run Audit
              </Link>
            </Button>
            <Button size="xl" variant="ghost" asChild>
              <a href="http://localhost:8765/" target="_blank" rel="noreferrer">
                <BookOpen className="h-5 w-5" />
                Platform Docs
              </a>
            </Button>
          </div>

          <div className="mx-auto mt-16 grid max-w-4xl grid-cols-2 gap-3 md:grid-cols-4">
            {[
              { v: "2", l: "Production agents" },
              { v: "9 + 5", l: "Tools + OWASP skills" },
              { v: "11 937×", l: "Cache speedup" },
              { v: "100%", l: "Audit reproducibility" },
            ].map((s, i) => (
              <motion.div
                key={s.l}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + i * 0.08 }}
                className="rounded-2xl border border-cnc-border bg-cnc-surface/40 p-4 backdrop-blur"
              >
                <div className="text-2xl font-extrabold text-gradient-azure">{s.v}</div>
                <div className="mt-1 text-[10px] uppercase tracking-widest text-cnc-muted">{s.l}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* TWO-PRODUCT GRID */}
      <section className="container py-12">
        <div className="mb-10 text-center">
          <Badge variant="azure" className="mb-3">Two products, shared platform</Badge>
          <h2 className="text-balance text-4xl font-extrabold tracking-tight text-white md:text-5xl">
            Wybierz <span className="text-gradient-cyan">narzędzie</span> dla zadania
          </h2>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <Card className="group h-full overflow-hidden border-2 border-cnc-electric/20 hover:border-cnc-electric/60 transition-all">
              <div className="bg-gradient-to-br from-cnc-electric/10 via-transparent to-transparent p-8">
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-azure-grad shadow-glow-sm">
                  <Code2 className="h-7 w-7 text-white" />
                </div>
                <Badge variant="cyan" className="mb-3">Module 23 · Concierge</Badge>
                <h3 className="text-2xl font-extrabold text-white">AI Code Concierge</h3>
                <p className="mt-2 text-sm text-cnc-muted">
                  Indeksuj repo raz, uruchamiaj 9 wyspecjalizowanych narzędzi LLM (review, security, refactor, generation)
                  z pełnym kontekstem semantycznym Augment.
                </p>
                <ul className="mt-5 space-y-2 text-sm text-cnc-muted">
                  <li>· Code review · Security audit · Refactor</li>
                  <li>· Generate · Analyze · Ask Specialist</li>
                  <li>· MCP server (Claude Desktop / Cursor)</li>
                  <li>· CI mode (GitHub Actions reviews)</li>
                </ul>
                <Button asChild className="mt-6 w-full">
                  <Link to="/studio">Open Studio <ArrowRight className="h-4 w-4" /></Link>
                </Button>
              </div>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }}>
            <Card className="group h-full overflow-hidden border-2 border-cnc-cyan/20 hover:border-cnc-cyan/60 transition-all">
              <div className="bg-gradient-to-br from-cnc-cyan/10 via-transparent to-transparent p-8">
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-cnc-cyan to-cnc-electric shadow-glow-cyan">
                  <Shield className="h-7 w-7 text-white" />
                </div>
                <Badge variant="cyan" className="mb-3">Module 24 · AuditOps</Badge>
                <h3 className="text-2xl font-extrabold text-white">Web Pentest Agent</h3>
                <p className="mt-2 text-sm text-cnc-muted">
                  Recon → LLM planner → Playwright execution → wideo evidence → OWASP report.
                  Z pamięcią instytucjonalną per-target i progressive-disclosure skills.
                </p>
                <ul className="mt-5 space-y-2 text-sm text-cnc-muted">
                  <li>· OWASP A01/A02/A03/A05 skills</li>
                  <li>· Playwright runner z dowodami wideo</li>
                  <li>· Wiki per-target (V2/V3 history)</li>
                  <li>· Allowlist + disclaimer + rate-limit</li>
                </ul>
                <Button variant="outline" asChild className="mt-6 w-full">
                  <Link to="/audit">Run Audit <ArrowRight className="h-4 w-4" /></Link>
                </Button>
              </div>
            </Card>
          </motion.div>
        </div>

        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="mt-6">
          <Card className="flex flex-wrap items-center justify-between gap-4 border border-cnc-border/60 bg-cnc-surface/30 p-5">
            <div className="flex items-center gap-3">
              <div className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-cnc-azure/30">
                <Brain className="h-5 w-5 text-cnc-electric2" />
              </div>
              <div>
                <div className="text-sm font-bold text-white">Knowledge Base — wspólny zasób</div>
                <div className="text-xs text-cnc-muted">
                  Przeglądaj OWASP skills (V1) i wiki audytów (V2/V3) — wszystko, czym karmiony jest planner.
                </div>
              </div>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/knowledge">Open Knowledge <ArrowRight className="h-4 w-4" /></Link>
            </Button>
          </Card>
        </motion.div>
      </section>

      {/* SHARED PLATFORM */}
      <section className="container py-20">
        <div className="mb-12 text-center">
          <Badge variant="default" className="mb-3">Shared infrastructure</Badge>
          <h2 className="text-4xl font-extrabold text-white md:text-5xl">
            Jedna <span className="text-gradient-azure">platforma</span>, dwa agenty
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-sm text-cnc-muted">
            Tier 1 (ADK) orkiestruje, Tier 2 (Auggie) wykonuje ciężką pracę. Cache, telemetria,
            circuit breaker, MCP — wspólne dla obu produktów.
          </p>
        </div>

        <div className="mx-auto grid max-w-5xl grid-cols-2 gap-3 md:grid-cols-4">
          {[
            { i: Zap, n: "Cache", d: "11 937× speedup" },
            { i: Shield, n: "Resilience", d: "Circuit breaker · backoff" },
            { i: Cpu, n: "MCP Server", d: "Claude Desktop · Cursor" },
            { i: Layers, n: "Skills V1", d: "Progressive disclosure" },
          ].map((t, i) => (
            <motion.div
              key={t.n}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="group flex flex-col items-center justify-center gap-2 rounded-2xl border border-cnc-border bg-cnc-surface/40 p-6 hover-rise hover:border-cnc-cyan/50 hover:shadow-glow-cyan"
            >
              <t.i className="h-8 w-8 text-cnc-electric2 transition-colors group-hover:text-cnc-cyan" />
              <span className="text-sm font-bold text-white">{t.n}</span>
              <span className="text-[10px] uppercase tracking-widest text-cnc-muted">{t.d}</span>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CONCIERGE FEATURES */}
      <section className="container py-16">
        <div className="mb-10 flex flex-wrap items-end justify-between gap-3">
          <div>
            <Badge variant="azure" className="mb-2"><Code2 className="h-3 w-3" /> Concierge</Badge>
            <h2 className="text-3xl font-extrabold text-white md:text-4xl">
              Production-grade <span className="text-gradient-azure">code intelligence</span>
            </h2>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/studio">Open Studio <ArrowRight className="h-4 w-4" /></Link>
          </Button>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {conciergeFeatures.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="group h-full overflow-hidden hover-rise hover:border-cnc-electric/50">
                <div className="p-6">
                  <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${accents[f.accent]}`}>
                    <f.icon className="h-6 w-6" />
                  </div>
                  <h3 className="mb-1.5 text-lg font-bold text-white">{f.title}</h3>
                  <p className="text-sm text-cnc-muted">{f.desc}</p>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* AUDITOPS FEATURES */}
      <section className="container py-16">
        <div className="mb-10 flex flex-wrap items-end justify-between gap-3">
          <div>
            <Badge variant="cyan" className="mb-2"><Shield className="h-3 w-3" /> AuditOps</Badge>
            <h2 className="text-3xl font-extrabold text-white md:text-4xl">
              Reproducible <span className="text-gradient-cyan">web pentest</span>, with evidence
            </h2>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/audit">Run Audit <ArrowRight className="h-4 w-4" /></Link>
          </Button>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {auditFeatures.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="group h-full overflow-hidden hover-rise hover:border-cnc-cyan/50">
                <div className="p-6">
                  <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${accents[f.accent]}`}>
                    <f.icon className="h-6 w-6" />
                  </div>
                  <h3 className="mb-1.5 text-lg font-bold text-white">{f.title}</h3>
                  <p className="text-sm text-cnc-muted">{f.desc}</p>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="container py-20">
        <div className="mb-12 text-center">
          <Badge variant="cyan" className="mb-3">How it works</Badge>
          <h2 className="text-4xl font-extrabold text-white md:text-5xl">3 kroki dla każdego z agentów</h2>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {[
            {
              step: "01",
              icon: Database,
              title: "Index / Recon",
              desc: "Concierge: index workspace (vector + AST). AuditOps: recon DOM + headers + robots. Bez interakcji ofensywnej.",
              highlight: true,
            },
            {
              step: "02",
              icon: Sparkles,
              title: "Plan / Pick Tool",
              desc: "Concierge: wybierz tool (review/security/refactor/...). AuditOps: planner LLM dobiera OWASP skills (A01/A02/A03/A05).",
              highlight: false,
            },
            {
              step: "03",
              icon: Rocket,
              title: "Execute & Iterate",
              desc: "Concierge: SSE streaming, telemetria, copy-paste do PR. AuditOps: Playwright + wideo + OWASP report (JSON/MD).",
              highlight: false,
            },
          ].map((s, i) => (
            <motion.div
              key={s.step}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="relative"
            >
              <Card className={`relative overflow-hidden p-6 ${s.highlight ? "border-cnc-electric shadow-glow" : ""}`}>
                {s.highlight && (
                  <Badge variant="azure" className="absolute right-4 top-4">Foundation</Badge>
                )}
                <div className="mb-4 font-mono text-5xl font-black text-cnc-electric/30">{s.step}</div>
                <s.icon className="mb-3 h-8 w-8 text-cnc-cyan" />
                <h3 className="mb-2 text-xl font-bold text-white">{s.title}</h3>
                <p className="text-sm text-cnc-muted">{s.desc}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* TOOLS PREVIEW */}
      <section className="container py-16">
        <div className="mb-12 text-center">
          <Badge variant="default" className="mb-3">The Toolbox</Badge>
          <h2 className="text-4xl font-extrabold text-white md:text-5xl">
            Specialists, <span className="text-gradient-azure">one workflow</span>
          </h2>
        </div>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
          {[
            { i: GitBranch, n: "Review PR" },
            { i: Microscope, n: "Analyze" },
            { i: Code2, n: "Generate" },
            { i: Workflow, n: "Refactor" },
            { i: ShieldAlert, n: "Security" },
            { i: Sparkles, n: "Ask" },
            { i: Radar, n: "Recon" },
            { i: Brain, n: "Planner" },
            { i: Camera, n: "Playwright" },
            { i: FileText, n: "OWASP Report" },
            { i: BookOpen, n: "Skills V1" },
            { i: Database, n: "Wiki V2/V3" },
          ].map((t, i) => (
            <motion.div
              key={t.n}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.04 }}
              className="group flex flex-col items-center justify-center gap-2 rounded-2xl border border-cnc-border bg-cnc-surface/40 p-5 hover-rise hover:border-cnc-cyan/50 hover:shadow-glow-cyan"
            >
              <t.i className="h-7 w-7 text-cnc-electric2 transition-colors group-hover:text-cnc-cyan" />
              <span className="text-xs font-bold text-white">{t.n}</span>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="container pb-32 pt-12">
        <Card className="relative overflow-hidden border-2 border-cnc-electric/30 bg-gradient-to-br from-cnc-azure/20 via-cnc-surface to-cnc-cyan/10 p-12 text-center md:p-20 shadow-glow">
          <div className="relative">
            <Sparkles className="mx-auto mb-4 h-12 w-12 text-cnc-cyan animate-float" />
            <h2 className="text-balance text-4xl font-extrabold text-white md:text-5xl">
              Gotów na <span className="text-gradient-azure">10× szybszy</span> workflow?
            </h2>
            <p className="mx-auto mt-5 max-w-xl text-cnc-muted">
              Otwórz Studio dla code intelligence albo Audit dla pentestu webapki.
              Wszystko lokalnie, z pełną telemetrią.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <Button size="xl" asChild>
                <Link to="/studio">Launch Studio <ArrowRight className="h-5 w-5" /></Link>
              </Button>
              <Button size="xl" variant="outline" asChild>
                <Link to="/audit">Launch AuditOps <Shield className="h-5 w-5" /></Link>
              </Button>
            </div>
          </div>
        </Card>
      </section>

      <footer className="container border-t border-cnc-border py-8 text-center text-xs text-cnc-muted">
        Built with FastAPI · React · Tailwind · Augment Code SDK · Google ADK · Playwright
      </footer>
    </motion.div>
  );
}
