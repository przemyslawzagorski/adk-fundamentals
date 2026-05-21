import * as React from "react";
import { motion } from "framer-motion";
import { Shield, Radar, Brain, Camera, FileText, ShieldAlert, History } from "lucide-react";
import { AmbientBackground } from "@/components/concierge/ambient-background";
import { HelpPanel } from "@/components/concierge/help-panel";
import { TargetForm } from "@/components/audit/target-form";
import { LiveRun } from "@/components/audit/live-run";
import { FindingsList } from "@/components/audit/findings-list";
import { EvidencePlayer } from "@/components/audit/evidence-player";
import { DisclaimerModal } from "@/components/audit/disclaimer-modal";
import { Badge } from "@/components/ui/badge";
import { useAuditStream } from "@/hooks/use-audit-stream";
import {
  fetchAuditConfig,
  postDisclaimer,
  type AuditConfigInfo,
  type AuditMode,
} from "@/api/audit-client";

export function Audit() {
  const stream = useAuditStream();
  const [config, setConfig] = React.useState<AuditConfigInfo | null>(null);
  const [url, setUrl] = React.useState("");
  const [mode, setMode] = React.useState<AuditMode>("auto");
  const [scenarioNl, setScenarioNl] = React.useState("");
  const [showDisclaimer, setShowDisclaimer] = React.useState(false);
  const [evidence, setEvidence] = React.useState<{ url: string | null; title: string }>({ url: null, title: "" });

  React.useEffect(() => {
    fetchAuditConfig().then(setConfig).catch(console.warn);
  }, []);

  const handleStart = () => {
    if (!url) return;
    if (config?.require_disclaimer ?? true) {
      setShowDisclaimer(true);
    } else {
      runAudit(undefined);
    }
  };

  async function runAudit(ack_token: string | undefined) {
    try {
      await stream.start({ url, mode, scenario_nl: scenarioNl, ack_token });
    } catch (e) {
      console.error(e);
    }
  }

  const onAcceptDisclaimer = async () => {
    setShowDisclaimer(false);
    try {
      const ack = await postDisclaimer(url);
      runAudit(ack.token);
    } catch (e) {
      console.error("disclaimer failed", e);
    }
  };

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
              <Shield className="h-3 w-3" /> AuditOps
            </Badge>
            <h1 className="text-3xl font-extrabold text-white md:text-4xl">
              Web <span className="text-gradient-azure">Pentest Agent</span>
            </h1>
            <p className="mt-1 text-sm text-cnc-muted">
              Recon → LLM plan → Playwright execution → video evidence → OWASP report.
              Authorized targets only.
            </p>
          </div>
          {config?.allowed_domains && config.allowed_domains.length === 0 && (
            <Badge variant="warning">Allowlist empty — set AUDITOPS_ALLOWED_DOMAINS</Badge>
          )}
        </header>

        <HelpPanel
          storageKey="help.audit"
          summary="Uruchom audyt OWASP wybranego targetu — recon, planner LLM, egzekucja w Playwright, dowód wideo."
          items={[
            { icon: Radar, title: "Recon", desc: "Snapshot DOM, formularze, security headers, /robots.txt — bez interakcji ofensywnej." },
            { icon: Brain, title: "Planner LLM", desc: "Skills (A01/A02/A03/A05) wstrzykiwane progresywnie. Tryb auto/scenario." },
            { icon: Camera, title: "Playwright runner", desc: "Każdy krok scenariusza z artefaktami: wideo, screenshoty, request log." },
            { icon: FileText, title: "Findings + raport", desc: "OWASP-tagged findings z severity, evidence, remediation. JSON + Markdown." },
            { icon: History, title: "Wiki memory", desc: "Każdy run odkłada się w wiki targetu (V2/V3) — kolejny audyt rusza z kontekstem." },
            { icon: ShieldAlert, title: "Safety gates", desc: "Allowlist domen, disclaimer modal, depth limit, rate-limit. Tylko autoryzowane cele." },
          ]}
          footer={
            <>
              <strong className="text-white">Zasada autoryzacji:</strong> uruchamiaj wyłącznie na hostach,
              dla których masz pisemną zgodę właściciela. AuditOps nie obchodzi WAFów ani CAPTCHA.
            </>
          }
          className="mb-6"
        />

        <section className="mb-6">
          <TargetForm
            url={url}
            setUrl={setUrl}
            mode={mode}
            setMode={setMode}
            scenarioNl={scenarioNl}
            setScenarioNl={setScenarioNl}
            config={config}
            isRunning={stream.isRunning}
            onStart={handleStart}
          />
        </section>

        <section className="mb-6">
          <LiveRun
            events={stream.events}
            phase={stream.phase}
            isRunning={stream.isRunning}
            error={stream.error}
          />
        </section>

        {stream.report && (
          <section className="mb-12">
            <FindingsList
              report={stream.report}
              onPlayVideo={(url, title) => setEvidence({ url, title })}
            />
          </section>
        )}
      </div>

      <DisclaimerModal
        open={showDisclaimer}
        targetUrl={url}
        onAccept={onAcceptDisclaimer}
        onCancel={() => setShowDisclaimer(false)}
      />
      <EvidencePlayer
        open={!!evidence.url}
        url={evidence.url}
        title={evidence.title}
        onClose={() => setEvidence({ url: null, title: "" })}
      />
    </motion.div>
  );
}
