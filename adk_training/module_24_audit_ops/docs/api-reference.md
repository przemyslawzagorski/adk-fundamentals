# REST API Reference

The router is mounted at `/api/audit` from `adk_training.module_24_audit_ops.api`.
All routes return JSON unless noted.

## Disclaimer + start

| Method | Path | Body | Returns |
|--------|------|------|---------|
| `POST` | `/api/audit/disclaimer/ack` | `{ user_id, target_url, statement }` | `{ ack_id }` |
| `POST` | `/api/audit/start` | `{ ack_id, mode, target_url, scenario_nl?, auth? }` | SSE stream of run events |

## Runs

| Method | Path | Returns |
|--------|------|---------|
| `GET` | `/api/audit/runs` | `[{ run_id, target_url, finished_at, severity_max }]` |
| `GET` | `/api/audit/runs/{run_id}` | full audit dict |
| `GET` | `/api/audit/runs/{run_id}/report.md` | rendered Markdown |
| `GET` | `/api/audit/runs/{run_id}/junit?fail_on=high` | JUnit XML |
| `GET` | `/api/audit/runs/diff?a=<id>&b=<id>&fmt=json|markdown` | diff between two runs |

## Skills (V1)

| Method | Path | Returns |
|--------|------|---------|
| `GET` | `/api/audit/skills` | L1 manifest of all bundled skills + their resources |
| `GET` | `/api/audit/skills/{name}` | L2 — full instructions body |
| `GET` | `/api/audit/skills/{name}/resource?path=<rel>` | L3 — content of a reference file |

## Wiki (V2 / V3 / V4)

| Method | Path | Returns |
|--------|------|---------|
| `GET` | `/api/audit/wiki` | `[{ slug, runs, findings }]` for every target |
| `GET` | `/api/audit/wiki/{slug}/index` | `text/markdown` (the rendered TOC) |
| `GET` | `/api/audit/wiki/{slug}/file?path=<rel>` | any file inside the wiki, path-traversal-guarded |
| `GET` | `/api/audit/wiki/{slug}/lint` | `{ slug, issues: [{ kind, path, detail }] }` |
| `POST` | `/api/audit/wiki/synthesize` | LLM-authored synthesis page (HITL-gated) |

### `POST /api/audit/wiki/synthesize`

```jsonc
{
  "slug": "acme.test",
  "question": "What's our regression pattern this quarter?",
  "accept": false   // set true to persist
}
```

Response when `accept=false`:

```jsonc
{
  "accepted": false,
  "preview": "...the LLM-authored synthesis answer...",
  "note": "Set accept=true to persist this synthesis page."
}
```

When `accept=true`, the answer is written to
`wiki/<slug>/synthesis/<UTC_TIMESTAMP>.md` and the response includes
`{ accepted: true, path, url }`.

## Auth — passing cookies + headers

When starting a run, you can include an `auth` block:

```jsonc
{
  "ack_id": "...",
  "mode": "guided",
  "target_url": "https://staging.acme.test/admin",
  "scenario_nl": "Click the user list and verify only admins can edit.",
  "auth": {
    "label": "admin-session",
    "cookies": [{ "name": "session", "value": "...", "domain": ".acme.test" }],
    "headers": { "X-Audit-Run": "true" }
  }
}
```

The auth block is fingerprinted (SHA-256 of a normalized form) so secrets
don't leak into logs while still letting us prove the same auth was used
across two runs in a diff.

## SSE event vocabulary

`POST /api/audit/start` returns `text/event-stream`. Each frame is a JSON
object with at least a `type` field:

| `type` | When | Payload |
|--------|------|---------|
| `run_started` | always | `run_id, target_url, mode, auth` |
| `phase` | recon / planning / executing | `phase, message` |
| `recon_complete` | after passive recon | `summary, forms, technologies, paths` |
| `plan_ready` | after LLM translation (guided) or library build (auto) | `scenarios: [{id, name, severity}]` |
| `step_event` | each Playwright step | `scenario_id, step, ok, detail` |
| `finding` | each Finding emitted | `severity, title, scenario_id, owasp` |
| `report_ready` | end of run | `run_id, markdown_path, json_path, markdown_url, json_url` |
| `run_failed` | error path | `error` |
