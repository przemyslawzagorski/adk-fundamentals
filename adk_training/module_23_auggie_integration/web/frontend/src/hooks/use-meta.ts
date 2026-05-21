import * as React from "react";
import { fetchConfig, fetchTools, fetchTelemetry, fetchCost, type ConfigSnapshot, type ToolMeta, type TelemetrySnapshot, type CostSnapshot } from "@/api/client";

export function useConfig() {
  const [data, setData] = React.useState<ConfigSnapshot | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const refresh = React.useCallback(async () => {
    try { setData(await fetchConfig()); }
    catch (e: any) { setError(e?.message ?? "config fetch failed"); }
  }, []);
  React.useEffect(() => { refresh(); }, [refresh]);
  return { config: data, error, refresh };
}

export function useTools() {
  const [tools, setTools] = React.useState<ToolMeta[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  React.useEffect(() => {
    fetchTools().then((r) => setTools(r.tools)).catch((e) => setError(e.message));
  }, []);
  return { tools, error };
}

export function useTelemetry(intervalMs = 5000) {
  const [telemetry, setTelemetry] = React.useState<TelemetrySnapshot | null>(null);
  const [cost, setCost] = React.useState<CostSnapshot | null>(null);

  const tick = React.useCallback(async () => {
    try {
      const [t, c] = await Promise.all([fetchTelemetry(), fetchCost()]);
      setTelemetry(t);
      setCost(c);
    } catch { /* ignore */ }
  }, []);

  React.useEffect(() => {
    tick();
    const id = setInterval(tick, intervalMs);
    return () => clearInterval(id);
  }, [tick, intervalMs]);

  return { telemetry, cost, refresh: tick };
}
