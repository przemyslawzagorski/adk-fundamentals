import * as React from "react";
import { Loader2, Sparkles, XCircle, PlayCircle, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { GenerateRequest } from "@/api/client";

interface Props {
  isStreaming: boolean;
  initialIssueKey?: string;
  onStart: (body: GenerateRequest) => void;
  onCancel: () => void;
}

const SUGGESTIONS = ["SWOK-1234", "DEMO-1", "BIL-501"];

export function GenerateForm({ isStreaming, initialIssueKey, onStart, onCancel }: Props) {
  const [issueKey, setIssueKey] = React.useState(initialIssueKey ?? "SWOK-1234");
  const [enableNotebookLm, setEnableNotebookLm] = React.useState(false);
  const [maxIter, setMaxIter] = React.useState(3);
  const [notebookUrl, setNotebookUrl] = React.useState("ec182696-22e7-4c58-9f85-6f7acc06cf8d");

  React.useEffect(() => {
    if (initialIssueKey) setIssueKey(initialIssueKey);
  }, [initialIssueKey]);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-zagi-surface/90 p-6 shadow-card-up">
      {/* gradient accent on top */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-zagi-crimson to-transparent" />

      <div className="mb-5 flex items-center gap-2">
        <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-zagi-crimson2 to-zagi-crimson shadow-glow-sm">
          <Wand2 className="h-4 w-4 text-white" />
        </div>
        <div>
          <div className="text-sm font-semibold text-white">Nowa specyfikacja</div>
          <div className="text-xs text-zagi-muted">Wpisz klucz Jira albo wybierz przyklad</div>
        </div>
      </div>

      <form
        className="space-y-5"
        onSubmit={(e) => {
          e.preventDefault();
          onStart({
            issue_key: issueKey.trim(),
            enable_notebooklm: enableNotebookLm,
            max_critique_iterations: maxIter,
            notebook_url: notebookUrl.trim() || null,
          });
        }}
      >
        <div className="space-y-2">
          <Label htmlFor="issue_key" className="text-zagi-muted">Issue key</Label>
          <Input
            id="issue_key"
            value={issueKey}
            onChange={(e) => setIssueKey(e.target.value)}
            placeholder="SWOK-1234"
            required
            autoFocus
            disabled={isStreaming}
            className="h-11 border-white/10 bg-zagi-bg font-mono text-base text-white placeholder:text-zagi-dim focus-visible:ring-zagi-crimson"
          />
          <div className="flex flex-wrap gap-1.5 pt-1">
            {SUGGESTIONS.map((s) => (
              <button
                type="button"
                key={s}
                disabled={isStreaming}
                onClick={() => setIssueKey(s)}
                className="rounded-full border border-white/10 bg-white/[0.02] px-2.5 py-0.5 font-mono text-[11px] text-zagi-muted transition hover:border-zagi-crimson/40 hover:text-white disabled:opacity-50"
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="max_iter" className="text-zagi-muted">Iteracje krytyki</Label>
            <Input
              id="max_iter"
              type="number"
              min={1}
              max={5}
              value={maxIter}
              onChange={(e) => setMaxIter(Number(e.target.value))}
              disabled={isStreaming}
              className="h-11 border-white/10 bg-zagi-bg text-white"
            />
          </div>
          <div className="space-y-2">
            <Label className="text-zagi-muted">NotebookLM</Label>
            <label className="flex h-11 cursor-pointer items-center gap-2 rounded-md border border-white/10 bg-zagi-bg px-3 text-xs">
              <input
                type="checkbox"
                className="h-4 w-4 accent-zagi-crimson"
                checked={enableNotebookLm}
                onChange={(e) => setEnableNotebookLm(e.target.checked)}
                disabled={isStreaming}
              />
              <span className="text-white">Wlacz</span>
            </label>
          </div>
        </div>

        {enableNotebookLm && (
          <div className="space-y-2">
            <Label htmlFor="notebook_url" className="text-zagi-muted">Notebook ID / URL</Label>
            <Input
              id="notebook_url"
              value={notebookUrl}
              onChange={(e) => setNotebookUrl(e.target.value)}
              placeholder="ec182696-22e7-4c58-9f85-6f7acc06cf8d"
              disabled={isStreaming}
              className="h-11 border-white/10 bg-zagi-bg font-mono text-xs text-white placeholder:text-zagi-dim focus-visible:ring-zagi-crimson"
            />
          </div>
        )}

        <div className="space-y-2">
          {isStreaming ? (
            <Button
              type="button"
              variant="outline"
              size="lg"
              className="h-12 w-full border-white/15 text-white hover:bg-white/5"
              onClick={onCancel}
            >
              <XCircle className="h-4 w-4" /> Anuluj
            </Button>
          ) : (
            <Button
              type="submit"
              size="lg"
              className="h-12 w-full bg-gradient-to-r from-zagi-crimson2 to-zagi-crimson text-base font-semibold shadow-glow-sm hover:shadow-glow"
            >
              <Sparkles className="h-4 w-4" /> Generuj HLD + Epiki
            </Button>
          )}

          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={isStreaming}
            onClick={() =>
              onStart({
                issue_key: "DEMO-1",
                enable_notebooklm: false,
                max_critique_iterations: 1,
              })
            }
            className="h-9 w-full text-xs text-zagi-muted hover:bg-white/5 hover:text-white"
          >
            {isStreaming ? <Loader2 className="h-3 w-3 animate-spin" /> : <PlayCircle className="h-3 w-3" />}
            Tryb demo (scaffold, ~2s)
          </Button>
        </div>
      </form>
    </div>
  );
}
