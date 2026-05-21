import * as React from "react";
import { ShieldCheck, ShieldAlert, FileText, ExternalLink, Film } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { AuditRun, AuditFinding, Severity } from "@/api/audit-client";

const SEV_VARIANT: Record<Severity, "danger" | "warning" | "default" | "cyan" | "muted"> = {
  critical: "danger",
  high: "danger",
  medium: "warning",
  low: "cyan",
  info: "muted",
};

const SEV_ORDER: Severity[] = ["critical", "high", "medium", "low", "info"];

interface Props {
  report: AuditRun | null;
  onPlayVideo: (url: string, title: string) => void;
}

export function FindingsList({ report, onPlayVideo }: Props) {
  if (!report) return null;
  const findings = [...report.findings].sort(
    (a, b) => SEV_ORDER.indexOf(a.severity) - SEV_ORDER.indexOf(b.severity),
  );
  const score = report.report?.score ?? 0;

  return (
    <Card className="p-6">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <Badge variant={findings.length > 0 ? "danger" : "success"} className="mb-2">
            {findings.length > 0 ? <ShieldAlert className="h-3 w-3" /> : <ShieldCheck className="h-3 w-3" />}
            {findings.length} findings
          </Badge>
          <h3 className="text-2xl font-extrabold text-white">Findings & evidence</h3>
          <p className="text-sm text-cnc-muted">
            Run <span className="font-mono">{report.run_id}</span> · {report.duration_s.toFixed(1)}s ·
            risk score <strong className="text-white">{score}/100</strong>
          </p>
        </div>
        {report.report?.markdown_url && (
          <a
            href={report.report.markdown_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-cnc-line bg-cnc-surface/40 px-3 text-xs font-semibold text-cnc-ink hover:border-cnc-electric/60 hover:text-white"
          >
            <FileText className="h-3.5 w-3.5" /> Markdown report
            <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>

      {findings.length === 0 ? (
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
          No findings detected by the built-in probes. This does NOT mean the target is secure —
          it only means the executed scenarios did not trigger.
        </div>
      ) : (
        <div className="space-y-3">
          {findings.map((f, idx) => (
            <FindingCard key={idx} finding={f} report={report} onPlayVideo={onPlayVideo} />
          ))}
        </div>
      )}

      {/* Scenarios summary */}
      <div className="mt-6">
        <h4 className="mb-2 text-xs font-bold uppercase tracking-wider text-cnc-muted">
          Scenarios executed ({report.scenarios.length})
        </h4>
        <div className="space-y-2">
          {report.scenarios.map((sc) => (
            <div
              key={sc.id}
              className="flex items-center justify-between gap-3 rounded-xl border border-cnc-line bg-cnc-bg/40 p-3 text-sm"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Badge variant={sc.passed ? "success" : "danger"}>
                  {sc.passed ? "PASS" : "FAIL"}
                </Badge>
                <span className="truncate font-semibold text-white">{sc.name}</span>
                <span className="hidden md:inline text-xs text-cnc-muted">{sc.owasp}</span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-xs text-cnc-muted">{sc.duration_s.toFixed(2)}s</span>
                {sc.video_url && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onPlayVideo(sc.video_url!, sc.name)}
                  >
                    <Film className="h-3.5 w-3.5" /> Video
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

function FindingCard({
  finding, report, onPlayVideo,
}: { finding: AuditFinding; report: AuditRun; onPlayVideo: (url: string, title: string) => void }) {
  const scenario = report.scenarios.find((s) => s.id === finding.scenario_id);
  return (
    <div className="rounded-2xl border border-cnc-line bg-cnc-surface/40 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <Badge variant={SEV_VARIANT[finding.severity]}>{finding.severity.toUpperCase()}</Badge>
            <span className="text-xs font-mono text-cnc-muted">{finding.owasp}</span>
          </div>
          <div className="text-base font-bold text-white">{finding.title}</div>
          <div className="text-xs text-cnc-muted">scenario: {finding.scenario_id}</div>
        </div>
        {scenario?.video_url && (
          <Button size="sm" variant="outline" onClick={() => onPlayVideo(scenario.video_url!, finding.title)}>
            <Film className="h-3.5 w-3.5" /> Replay
          </Button>
        )}
      </div>
      {Object.keys(finding.evidence ?? {}).length > 0 && (
        <pre className="mt-3 overflow-x-auto rounded-lg border border-cnc-line bg-cnc-bg/60 p-3 text-xs text-cnc-cyan2">
          {JSON.stringify(finding.evidence, null, 2)}
        </pre>
      )}
    </div>
  );
}
