import * as React from "react";
import { CheckCircle2, FileJson, FileText, Loader2, Save, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, type Epic } from "@/api/client";
import { useToast } from "@/components/toast";

interface Props {
  sessionId: string;
  epics: Epic[];
  hldMarkdown: string;
  dirty: boolean;
  onSaved: () => void;
}

export function ActionsBar({ sessionId, epics, hldMarkdown, dirty, onSaved }: Props) {
  const toast = useToast();
  const [saving, setSaving] = React.useState(false);
  const [publishing, setPublishing] = React.useState(false);
  const [published, setPublished] = React.useState(false);

  const onSave = async () => {
    setSaving(true);
    try {
      await api.saveEdits(sessionId, epics, hldMarkdown);
      onSaved();
      toast.push("Zmiany zapisane", "success");
    } catch (e) {
      toast.push((e as Error).message, "error");
    } finally {
      setSaving(false);
    }
  };

  const onPublish = async () => {
    setPublishing(true);
    try {
      const res = await api.publish(sessionId, epics);
      setPublished(true);
      toast.push(`Publish OK (${res.mode}) · ${res.epics_count} epikow`, "success");
      onSaved();
    } catch (e) {
      toast.push((e as Error).message, "error");
    } finally {
      setPublishing(false);
    }
  };

  const downloadExport = (fmt: "md" | "json") => {
    const a = document.createElement("a");
    a.href = api.exportUrl(sessionId, fmt);
    a.download = `spec-${sessionId}.${fmt}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    toast.push(`Pobrano spec.${fmt}`, "info");
  };

  return (
    <div className="sticky top-20 z-30 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-zagi-surface/80 p-3 backdrop-blur-xl shadow-card-up">
      <div className="flex items-center gap-2 px-2 text-sm">
        {dirty ? (
          <span className="flex items-center gap-2 rounded-full bg-zagi-gold/15 px-3 py-1 text-xs font-semibold text-zagi-gold">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-zagi-gold" />
            Niezapisane zmiany
          </span>
        ) : published ? (
          <span className="flex items-center gap-1.5 rounded-full bg-zagi-neon/15 px-3 py-1 text-xs font-semibold text-zagi-neon">
            <CheckCircle2 className="h-3 w-3" /> Opublikowane
          </span>
        ) : (
          <span className="flex items-center gap-2 rounded-full bg-white/[0.04] px-3 py-1 text-xs text-zagi-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-zagi-neon" />
            Wszystko zapisane
          </span>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          className="text-zagi-muted hover:bg-white/5 hover:text-white"
          onClick={() => downloadExport("md")}
        >
          <FileText className="h-4 w-4" /> MD
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="text-zagi-muted hover:bg-white/5 hover:text-white"
          onClick={() => downloadExport("json")}
        >
          <FileJson className="h-4 w-4" /> JSON
        </Button>
        <div className="mx-1 h-5 w-px bg-white/10" />
        <Button
          variant="outline"
          size="sm"
          onClick={onSave}
          disabled={!dirty || saving}
          className="border-white/15 text-white hover:bg-white/5"
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
          Zapisz
        </Button>
        <Button
          size="sm"
          onClick={onPublish}
          disabled={publishing}
          className="bg-gradient-to-r from-zagi-crimson2 to-zagi-crimson font-semibold shadow-glow-sm hover:shadow-glow"
        >
          {publishing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
          Approve & Publish
        </Button>
      </div>
    </div>
  );
}
