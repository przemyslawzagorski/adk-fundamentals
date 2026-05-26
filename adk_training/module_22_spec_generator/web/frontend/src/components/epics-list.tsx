import * as React from "react";
import {
  Layers,
  Tag,
  GitMerge,
  Target,
  Pencil,
  Save,
  X,
  Plus,
  Trash2,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import type { Epic } from "@/api/client";

interface Props {
  epics: Epic[];
  editable?: boolean;
  onChange?: (next: Epic[]) => void;
}

const PRIORITIES: Epic["priority"][] = ["Highest", "High", "Medium", "Low"];

const PRIORITY_VARIANT: Record<Epic["priority"], "default" | "secondary" | "destructive" | "warning"> = {
  Highest: "destructive",
  High: "warning",
  Medium: "default",
  Low: "secondary",
};

export function EpicsList({ epics, editable = false, onChange }: Props) {
  const [editingIdx, setEditingIdx] = React.useState<number | null>(null);

  const update = (idx: number, patch: Partial<Epic>) => {
    if (!onChange) return;
    onChange(epics.map((e, i) => (i === idx ? { ...e, ...patch } : e)));
  };

  const remove = (idx: number) => {
    if (!onChange) return;
    onChange(epics.filter((_, i) => i !== idx));
    setEditingIdx(null);
  };

  const addEmpty = () => {
    if (!onChange) return;
    onChange([
      ...epics,
      {
        title: "Nowy epik",
        summary: "",
        acceptance_criteria: [],
        priority: "Medium",
        labels: [],
        estimated_story_points: 3,
        dependencies: [],
      },
    ]);
    setEditingIdx(epics.length);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2 text-lg">
            <Layers className="h-4 w-4 text-primary" /> Epiki
          </span>
          <div className="flex items-center gap-2">
            <Badge variant="outline">{epics.length}</Badge>
            {editable && (
              <Button size="sm" variant="outline" onClick={addEmpty}>
                <Plus className="h-3 w-3" /> Dodaj epik
              </Button>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {epics.length === 0 && (
          <p className="text-sm text-muted-foreground">Brak epikow do wyswietlenia.</p>
        )}
        {epics.map((epic, idx) =>
          editingIdx === idx ? (
            <EpicEditor
              key={idx}
              epic={epic}
              onCancel={() => setEditingIdx(null)}
              onSave={(next) => {
                update(idx, next);
                setEditingIdx(null);
              }}
              onDelete={() => remove(idx)}
            />
          ) : (
            <EpicCard
              key={idx}
              epic={epic}
              editable={editable}
              onEdit={() => setEditingIdx(idx)}
            />
          ),
        )}
      </CardContent>
    </Card>
  );
}

function EpicCard({
  epic,
  editable,
  onEdit,
}: {
  epic: Epic;
  editable: boolean;
  onEdit: () => void;
}) {
  return (
    <article className="group rounded-lg border border-border/60 bg-background/30 p-4 transition-colors hover:border-primary/40">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <h3 className="text-sm font-semibold leading-tight">{epic.title}</h3>
          <p className="text-sm text-muted-foreground">{epic.summary}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={PRIORITY_VARIANT[epic.priority] ?? "default"}>{epic.priority}</Badge>
          <Badge variant="secondary">{epic.estimated_story_points} SP</Badge>
          {editable && (
            <Button size="icon" variant="ghost" onClick={onEdit} aria-label="Edytuj">
              <Pencil className="h-4 w-4" />
            </Button>
          )}
        </div>
      </header>

      {epic.acceptance_criteria?.length > 0 && (
        <>
          <Separator className="my-3" />
          <div className="space-y-1.5">
            <div className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              <Target className="h-3 w-3" /> Acceptance criteria
            </div>
            <ul className="list-disc space-y-1 pl-5 text-sm">
              {epic.acceptance_criteria.map((c, i) => (
                <li key={i}>{c}</li>
              ))}
            </ul>
          </div>
        </>
      )}

      {(epic.labels?.length || epic.dependencies?.length) ? (
        <>
          <Separator className="my-3" />
          <div className="flex flex-wrap gap-4 text-xs">
            {epic.labels?.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5">
                <Tag className="h-3 w-3 text-muted-foreground" />
                {epic.labels.map((l) => (
                  <Badge key={l} variant="outline" className="font-normal">
                    {l}
                  </Badge>
                ))}
              </div>
            )}
            {epic.dependencies?.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5">
                <GitMerge className="h-3 w-3 text-muted-foreground" />
                {epic.dependencies.map((d) => (
                  <Badge key={d} variant="outline" className="font-normal">
                    {d}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </>
      ) : null}
    </article>
  );
}

function EpicEditor({
  epic,
  onSave,
  onCancel,
  onDelete,
}: {
  epic: Epic;
  onSave: (next: Epic) => void;
  onCancel: () => void;
  onDelete: () => void;
}) {
  const [draft, setDraft] = React.useState<Epic>(() => ({
    ...epic,
    acceptance_criteria: [...(epic.acceptance_criteria ?? [])],
    labels: [...(epic.labels ?? [])],
    dependencies: [...(epic.dependencies ?? [])],
  }));

  return (
    <article className="rounded-lg border border-primary/40 bg-background/40 p-4 ring-1 ring-primary/20">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_120px_100px]">
        <div className="space-y-1.5">
          <Label htmlFor="ed-title">Tytul</Label>
          <Input
            id="ed-title"
            value={draft.title}
            onChange={(e) => setDraft({ ...draft, title: e.target.value })}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="ed-prio">Priorytet</Label>
          <select
            id="ed-prio"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            value={draft.priority}
            onChange={(e) => setDraft({ ...draft, priority: e.target.value as Epic["priority"] })}
          >
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="ed-sp">SP</Label>
          <Input
            id="ed-sp"
            type="number"
            min={0}
            value={draft.estimated_story_points}
            onChange={(e) =>
              setDraft({ ...draft, estimated_story_points: Number(e.target.value) })
            }
          />
        </div>
      </div>

      <div className="mt-3 space-y-1.5">
        <Label htmlFor="ed-summary">Summary</Label>
        <Textarea
          id="ed-summary"
          rows={2}
          value={draft.summary}
          onChange={(e) => setDraft({ ...draft, summary: e.target.value })}
        />
      </div>

      <div className="mt-3 space-y-1.5">
        <Label htmlFor="ed-ac">Acceptance criteria (po jednym w linii)</Label>
        <Textarea
          id="ed-ac"
          rows={4}
          value={draft.acceptance_criteria.join("\n")}
          onChange={(e) =>
            setDraft({
              ...draft,
              acceptance_criteria: e.target.value
                .split("\n")
                .map((s) => s.trim())
                .filter(Boolean),
            })
          }
        />
      </div>

      <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="ed-labels">Labels (CSV)</Label>
          <Input
            id="ed-labels"
            value={draft.labels.join(", ")}
            onChange={(e) =>
              setDraft({
                ...draft,
                labels: e.target.value
                  .split(",")
                  .map((s) => s.trim())
                  .filter(Boolean),
              })
            }
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="ed-deps">Dependencies (CSV)</Label>
          <Input
            id="ed-deps"
            value={draft.dependencies.join(", ")}
            onChange={(e) =>
              setDraft({
                ...draft,
                dependencies: e.target.value
                  .split(",")
                  .map((s) => s.trim())
                  .filter(Boolean),
              })
            }
          />
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between gap-2">
        <Button size="sm" variant="ghost" onClick={onDelete} className="text-destructive">
          <Trash2 className="h-4 w-4" /> Usun
        </Button>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={onCancel}>
            <X className="h-4 w-4" /> Anuluj
          </Button>
          <Button size="sm" onClick={() => onSave(draft)}>
            <Save className="h-4 w-4" /> Zapisz
          </Button>
        </div>
      </div>
    </article>
  );
}
