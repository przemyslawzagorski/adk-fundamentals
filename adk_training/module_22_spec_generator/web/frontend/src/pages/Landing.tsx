import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  Sparkles,
  Bot,
  ShieldCheck,
  Zap,
  GitBranch,
  Boxes,
  CheckCircle2,
  PlayCircle,
} from "lucide-react";
import { AmbientBackground } from "@/components/zagi/ambient-background";
import { PipelineDiagram } from "@/components/zagi/pipeline-diagram";
import { Button } from "@/components/ui/button";

const FEATURES = [
  {
    icon: Bot,
    title: "Pipeline 5 agentow",
    desc: "Sekwencyjny SequentialAgent ADK: ticket → kontekst → HLD → krytyka → epiki.",
    accent: "from-zagi-crimson2 to-zagi-crimson",
  },
  {
    icon: Zap,
    title: "Live SSE progress",
    desc: "Server-Sent Events pokazuja kazdy etap w czasie rzeczywistym.",
    accent: "from-zagi-neon to-zagi-neon2",
  },
  {
    icon: ShieldCheck,
    title: "Human-in-the-Loop",
    desc: "LLM nie publikuje do Jira bez Twojej akceptacji. Kazdy epik edytujesz inline.",
    accent: "from-zagi-violet to-zagi-crimson2",
  },
  {
    icon: GitBranch,
    title: "Critique Loop",
    desc: "Krytyk i poprawiacz iteruja HLD do skutku. Konfigurowalna liczba przebiegow.",
    accent: "from-zagi-gold to-zagi-crimson",
  },
  {
    icon: Boxes,
    title: "Eksport MD / JSON",
    desc: "Jednym klikiem pobierasz spec do repo, wiki albo PR description.",
    accent: "from-zagi-neon2 to-zagi-violet",
  },
  {
    icon: Sparkles,
    title: "Demo bez konta",
    desc: "Tryb scaffold odpala pelny flow bez Vertex AI - testujesz UX od razu.",
    accent: "from-zagi-crimson to-zagi-violet",
  },
];

const HOW_STEPS = [
  {
    n: "01",
    title: "Wklej klucz Jira",
    desc: "SWOK-1234 albo dowolny ticket - ZAGI sam wyciagnie tytul, opis i akceptanci kryteria.",
  },
  {
    n: "02",
    title: "Ogladaj live",
    desc: "Pipeline 5 sub-agentow leci po kolei. Widzisz kazdy etap, czas trwania i preview wyjscia.",
  },
  {
    n: "03",
    title: "Edytuj i publikuj",
    desc: "HLD + epiki ladujesz w edytorze, poprawiasz, eksportujesz lub publikujesz do Jira.",
  },
];

export function Landing() {
  return (
    <motion.main
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="relative isolate"
    >
      {/* HERO */}
      <section className="relative pt-32 pb-24">
        <AmbientBackground />

        <div className="container relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="mx-auto flex max-w-5xl flex-col items-center text-center"
          >
            <motion.span
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-4 py-1.5 text-xs font-medium uppercase tracking-[0.2em] text-zagi-muted backdrop-blur"
            >
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-zagi-crimson" />
              Zero-touch · Agentic · Generation · Intelligence
            </motion.span>

            <h1 className="text-balance text-5xl font-extrabold leading-[0.95] tracking-tight text-white sm:text-7xl lg:text-[88px]">
              Z Jira ticketu
              <br />
              do gotowej{" "}
              <span className="text-gradient-brand">specyfikacji</span>
              <br />
              w 60 sekund.
            </h1>

            <p className="mt-8 max-w-2xl text-pretty text-lg text-zagi-muted sm:text-xl">
              ZAGI to agentowy system, ktory analizuje ticket, scala wiedze z Confluence,
              GitLaba i NotebookLM, pisze HLD, sam go krytykuje, a na koncu rozbija na
              epiki gotowe do publikacji. Ty tylko klikasz <em className="text-white">Approve</em>.
            </p>

            <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
              <Link to="/studio">
                <Button
                  size="lg"
                  className="group h-12 bg-gradient-to-r from-zagi-crimson2 to-zagi-crimson px-7 text-base font-semibold shadow-glow hover:shadow-[0_0_60px_-10px_rgba(229,9,20,0.8)]"
                >
                  Otworz Studio
                  <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
                </Button>
              </Link>
              <Link to="/studio?demo=1">
                <Button
                  size="lg"
                  variant="outline"
                  className="h-12 border-white/15 bg-white/[0.02] px-7 text-base font-medium text-white backdrop-blur hover:bg-white/[0.06]"
                >
                  <PlayCircle className="h-4 w-4" />
                  Zobacz demo
                </Button>
              </Link>
            </div>

            {/* social proof / metrics */}
            <div className="mt-14 grid w-full max-w-3xl grid-cols-3 gap-6">
              <Metric value="60s" label="Sredni czas generacji" />
              <Metric value="5" label="Sub-agentow ADK" />
              <Metric value="100%" label="HITL przed publish" />
            </div>
          </motion.div>

          {/* Pipeline preview */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="mx-auto mt-20 max-w-5xl"
          >
            <div className="mb-3 flex items-center gap-2 px-1 text-xs font-medium uppercase tracking-widest text-zagi-muted">
              <span className="h-px flex-1 bg-gradient-to-r from-transparent to-white/10" />
              Live pipeline
              <span className="h-px flex-1 bg-gradient-to-l from-transparent to-white/10" />
            </div>
            <PipelineDiagram />
          </motion.div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="relative py-24" id="features">
        <div className="container relative">
          <SectionHeader
            kicker="Capabilities"
            title="Wszystko czego potrzebuje analityk"
            subtitle="Niskopoziomowy kontrol nad agentami, wysokopoziomowa magia dla uzytkownika."
          />

          <div className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f, i) => (
              <motion.article
                key={f.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.45, delay: i * 0.06 }}
                className="group relative overflow-hidden rounded-2xl border border-white/[0.06] bg-zagi-surface/80 p-6 hover-rise hover:border-white/15 hover:shadow-card-up"
              >
                <div className={`mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${f.accent} shadow-glow-sm`}>
                  <f.icon className="h-5 w-5 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white">{f.title}</h3>
                <p className="mt-2 text-sm text-zagi-muted">{f.desc}</p>
                <div className="pointer-events-none absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 transition group-hover:opacity-100" />
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="relative py-24" id="how">
        <div className="container">
          <SectionHeader
            kicker="Workflow"
            title={
              <>
                Trzy kroki. Zero ceremonii.
              </>
            }
            subtitle="ZAGI nie zastapi analityka. Zabiera mu nudna czesc."
          />

          <div className="mt-16 grid grid-cols-1 gap-6 lg:grid-cols-3">
            {HOW_STEPS.map((step, i) => (
              <motion.div
                key={step.n}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                className="relative overflow-hidden rounded-2xl border border-white/5 bg-gradient-to-br from-zagi-surface to-zagi-bg p-8"
              >
                <div className="text-7xl font-black tracking-tighter text-gradient-brand opacity-90">
                  {step.n}
                </div>
                <h3 className="mt-2 text-xl font-bold text-white">{step.title}</h3>
                <p className="mt-3 text-sm text-zagi-muted">{step.desc}</p>
                <CheckCircle2 className="absolute right-6 top-6 h-5 w-5 text-zagi-neon" />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AUTHOR */}
      <section className="relative py-24" id="author">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="relative mx-auto max-w-4xl overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-zagi-surface to-zagi-bg p-10 shadow-card-up"
          >
            <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-zagi-crimson/30 blur-3xl" />
            <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-zagi-violet/25 blur-3xl" />

            <div className="relative grid grid-cols-1 items-center gap-8 sm:grid-cols-[180px_1fr]">
              <div className="relative mx-auto">
                <div className="grid h-40 w-40 place-items-center rounded-full bg-gradient-to-br from-zagi-crimson via-zagi-crimson2 to-zagi-violet text-5xl font-black text-white shadow-glow">
                  PZ
                </div>
                <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 rounded-full bg-zagi-bg px-3 py-1 text-[10px] font-semibold uppercase tracking-widest text-zagi-neon ring-1 ring-white/10">
                  Author
                </span>
              </div>
              <div>
                <div className="text-xs font-medium uppercase tracking-[0.25em] text-zagi-muted">
                  Built by
                </div>
                <h3 className="mt-1 text-3xl font-bold text-white">
                  Przemek Zagorski
                </h3>
                <p className="mt-3 text-zagi-muted">
                  Lead analityk biznesowy i builder narzedzi AI dla zespolow IT.
                  ZAGI to kontynuacja rodziny <strong className="text-white">SPECTRUM</strong> -
                  serii narzedzi ktore zamieniaja zmudna prace analityczna w decyzje.
                </p>
                <div className="mt-5 flex flex-wrap gap-2">
                  <Tag>Google ADK</Tag>
                  <Tag>Gemini 2.5</Tag>
                  <Tag>FastAPI</Tag>
                  <Tag>React 18</Tag>
                  <Tag>Framer Motion</Tag>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative pb-32 pt-12">
        <div className="container">
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="relative mx-auto max-w-4xl overflow-hidden rounded-3xl border border-zagi-crimson/30 bg-gradient-to-br from-zagi-crimson/15 via-zagi-bg to-zagi-violet/15 p-12 text-center shadow-glow"
          >
            <Sparkles className="mx-auto h-8 w-8 text-zagi-neon" />
            <h2 className="mt-4 text-balance text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
              Zobacz, jak ZAGI pisze spec za Ciebie.
            </h2>
            <p className="mt-3 text-zagi-muted">
              Bez instalacji. Bez konta. Tryb demo dziala w 5 sekund.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Link to="/studio?demo=1">
                <Button
                  size="lg"
                  className="h-12 bg-gradient-to-r from-zagi-crimson2 to-zagi-crimson px-8 text-base font-semibold shadow-glow"
                >
                  Odpal demo
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>

        <footer className="container mt-20 flex flex-wrap items-center justify-between gap-4 border-t border-white/5 pt-8 text-xs text-zagi-muted">
          <div>© 2026 Przemek Zagorski · ZAGI Spec Intelligence</div>
          <div className="flex gap-4">
            <span>Zero-touch · Agentic · Generation · Intelligence</span>
          </div>
        </footer>
      </section>
    </motion.main>
  );
}

function Metric({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-2xl border border-white/5 bg-white/[0.02] px-4 py-5 backdrop-blur">
      <div className="text-3xl font-extrabold text-gradient-brand">{value}</div>
      <div className="mt-1 text-xs uppercase tracking-widest text-zagi-muted">{label}</div>
    </div>
  );
}

function SectionHeader({
  kicker,
  title,
  subtitle,
}: {
  kicker: string;
  title: React.ReactNode;
  subtitle: string;
}) {
  return (
    <div className="mx-auto max-w-3xl text-center">
      <div className="text-xs font-semibold uppercase tracking-[0.25em] text-zagi-neon">
        {kicker}
      </div>
      <h2 className="mt-3 text-balance text-4xl font-bold tracking-tight text-white sm:text-5xl">
        {title}
      </h2>
      <p className="mt-4 text-pretty text-zagi-muted">{subtitle}</p>
    </div>
  );
}

function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs font-medium text-zagi-muted">
      {children}
    </span>
  );
}
