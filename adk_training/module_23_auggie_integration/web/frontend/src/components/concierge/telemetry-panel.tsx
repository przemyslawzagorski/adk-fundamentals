import { Activity, DollarSign, Database, Shield, Zap, Clock } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useTelemetry } from "@/hooks/use-meta";
import { fmtUSD, fmtSeconds, cn } from "@/lib/utils";

export function TelemetryPanel({ className }: { className?: string }) {
  const { telemetry, cost } = useTelemetry(5000);

  if (!telemetry || !cost) {
    return (
      <Card className={cn("p-5 animate-pulse", className)}>
        <div className="h-4 w-1/3 rounded bg-cnc-surface2" />
        <div className="mt-3 grid grid-cols-2 gap-3">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-16 rounded-lg bg-cnc-surface2" />
          ))}
        </div>
      </Card>
    );
  }

  const breakerVariant =
    telemetry.circuit_breaker.state === "closed" ? "success" :
    telemetry.circuit_breaker.state === "half_open" ? "warning" : "danger";

  return (
    <Card className={cn("overflow-hidden", className)}>
      <div className="flex items-center justify-between border-b border-cnc-border bg-cnc-surface2/40 px-5 py-3">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-cnc-cyan animate-pulse" />
          <h3 className="text-sm font-bold uppercase tracking-widest text-white">Live Telemetry</h3>
        </div>
        <Badge variant={breakerVariant as any}>
          <Shield className="h-3 w-3" />
          {telemetry.circuit_breaker.state}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-3 p-5 lg:grid-cols-4">
        <Stat label="Total Calls" value={String(telemetry.summary.total)} icon={<Activity className="h-4 w-4" />} accent="electric" />
        <Stat
          label="Cache Hit Rate"
          value={`${(telemetry.cache.hit_rate * 100).toFixed(0)}%`}
          icon={<Zap className="h-4 w-4" />}
          accent="cyan"
          sub={`${telemetry.cache.hits}h / ${telemetry.cache.misses}m`}
        />
        <Stat
          label="Avg Duration"
          value={fmtSeconds(telemetry.summary.avg_duration_s)}
          icon={<Clock className="h-4 w-4" />}
          accent="azure"
        />
        <Stat
          label="Est. Cost"
          value={fmtUSD(cost.total_estimated_usd)}
          icon={<DollarSign className="h-4 w-4" />}
          accent="gold"
          sub={`avg ${fmtUSD(cost.avg_per_call_usd)} / call`}
        />
      </div>

      {/* Recent calls */}
      {telemetry.last_calls.length > 0 && (
        <div className="border-t border-cnc-border px-5 py-3">
          <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-cnc-muted">
            <Database className="h-3 w-3" /> Recent Calls
          </div>
          <ul className="space-y-1 font-mono text-[11px]">
            {telemetry.last_calls.slice(-5).reverse().map((c, i) => (
              <li key={i} className="flex items-center justify-between gap-2 rounded-md bg-cnc-bg/40 px-2 py-1.5">
                <span className="flex items-center gap-2">
                  <span className={cn(
                    "h-1.5 w-1.5 rounded-full",
                    c.success ? "bg-emerald-400" : "bg-cnc-rose",
                  )} />
                  <span className="font-bold text-cnc-ink">{c.tool}</span>
                  {c.cached && <Badge variant="cyan" className="text-[9px]">cache</Badge>}
                </span>
                <span className="text-cnc-muted">{fmtSeconds(c.duration_s)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}

function Stat({
  label, value, icon, accent, sub,
}: {
  label: string; value: string; icon: React.ReactNode;
  accent: "electric" | "cyan" | "azure" | "gold";
  sub?: string;
}) {
  const colors: Record<string, string> = {
    electric: "from-cnc-electric/20 to-cnc-electric/5 text-cnc-electric2",
    cyan: "from-cnc-cyan/20 to-cnc-cyan/5 text-cnc-cyan2",
    azure: "from-cnc-azure/30 to-cnc-azure/5 text-cnc-electric2",
    gold: "from-cnc-gold/20 to-cnc-gold/5 text-cnc-gold",
  };
  return (
    <div className={cn("relative overflow-hidden rounded-xl border border-cnc-border bg-gradient-to-br p-3", colors[accent])}>
      <div className="flex items-center justify-between text-[10px] uppercase tracking-widest opacity-80">
        <span>{label}</span>
        {icon}
      </div>
      <div className="mt-1 text-2xl font-extrabold text-white">{value}</div>
      {sub && <div className="text-[10px] text-cnc-muted">{sub}</div>}
    </div>
  );
}
