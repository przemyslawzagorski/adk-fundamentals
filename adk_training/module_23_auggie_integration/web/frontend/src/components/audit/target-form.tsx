import * as React from "react";
import { Bot, Pencil, Globe, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { AuditMode, AuditConfigInfo } from "@/api/audit-client";

interface Props {
  url: string;
  setUrl: (v: string) => void;
  mode: AuditMode;
  setMode: (m: AuditMode) => void;
  scenarioNl: string;
  setScenarioNl: (v: string) => void;
  config: AuditConfigInfo | null;
  isRunning: boolean;
  onStart: () => void;
}

export function TargetForm({
  url, setUrl, mode, setMode, scenarioNl, setScenarioNl, config, isRunning, onStart,
}: Props) {
  const allowed = config?.allowed_domains ?? [];
  const playwrightOk = config?.playwright?.installed ?? false;

  return (
    <Card className="p-6 md:p-8">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <Badge variant="cyan" className="mb-2">Target</Badge>
          <h2 className="text-2xl font-extrabold text-white">Choose target & mode</h2>
          <p className="text-sm text-cnc-muted">Authorized URL only — disclaimer required.</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          {playwrightOk ? (
            <Badge variant="success">Playwright {config?.playwright.version ?? "ready"}</Badge>
          ) : (
            <Badge variant="danger">Playwright missing</Badge>
          )}
          <Badge variant="outline">{config?.llm_model ?? "llm: ?"}</Badge>
        </div>
      </div>

      <div className="mb-6">
        <Label htmlFor="audit-url" className="mb-2 flex items-center gap-2">
          <Globe className="h-3.5 w-3.5" /> Target URL
        </Label>
        <Input
          id="audit-url"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          spellCheck={false}
          autoComplete="off"
        />
        {allowed.length > 0 && (
          <p className="mt-2 text-xs text-cnc-muted">
            Allowed domains: <span className="font-mono text-cnc-cyan2">{allowed.join(", ")}</span>
          </p>
        )}
      </div>

      <div className="mb-5 grid grid-cols-1 gap-3 md:grid-cols-2">
        <ModeCard
          active={mode === "auto"}
          onClick={() => setMode("auto")}
          icon={<Bot className="h-5 w-5" />}
          title="Auto-Pentest"
          description="Recon + built-in OWASP scenarios. Fast, deterministic, no LLM cost."
          badge="Mode A"
        />
        <ModeCard
          active={mode === "guided"}
          onClick={() => setMode("guided")}
          icon={<Pencil className="h-5 w-5" />}
          title="Guided"
          description="Describe a scenario in natural language. LLM writes Playwright steps."
          badge="Mode B"
        />
      </div>

      {mode === "guided" && (
        <div className="mb-5">
          <Label htmlFor="scenario-nl" className="mb-2 flex items-center gap-2">
            <Sparkles className="h-3.5 w-3.5" /> Scenario (natural language)
          </Label>
          <Textarea
            id="scenario-nl"
            placeholder={"Try to log in as admin/admin and verify whether the login form rate-limits brute force."}
            rows={4}
            value={scenarioNl}
            onChange={(e) => setScenarioNl(e.target.value)}
          />
          <p className="mt-1 text-xs text-cnc-muted">
            The LLM will translate this into a Playwright step list and execute it on a fresh
            browser context with video recording.
          </p>
        </div>
      )}

      <div className="flex items-center justify-end gap-2">
        <Button
          variant="default"
          size="lg"
          disabled={isRunning || !url || (mode === "guided" && !scenarioNl)}
          onClick={onStart}
        >
          {isRunning ? "Audit running..." : "Start audit"}
        </Button>
      </div>
    </Card>
  );
}

interface ModeCardProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  title: string;
  description: string;
  badge: string;
}
function ModeCard({ active, onClick, icon, title, description, badge }: ModeCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "group rounded-2xl border p-4 text-left transition-all",
        active
          ? "border-cnc-electric/70 bg-cnc-electric/10 shadow-glow"
          : "border-cnc-border bg-cnc-surface/40 hover:border-cnc-electric/60 hover:bg-cnc-surface/70",
      )}
    >
      <div className="mb-2 flex items-center justify-between">
        <div
          className={cn(
            "flex h-10 w-10 items-center justify-center rounded-xl",
            active ? "bg-cnc-electric/20 text-cnc-electric2" : "bg-cnc-surface2 text-cnc-muted",
          )}
        >
          {icon}
        </div>
        <Badge variant={active ? "default" : "muted"}>{badge}</Badge>
      </div>
      <div className="text-base font-bold text-white">{title}</div>
      <div className="text-xs text-cnc-muted">{description}</div>
    </button>
  );
}
