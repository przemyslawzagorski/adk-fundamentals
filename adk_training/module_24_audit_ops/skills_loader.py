"""Skills loader — progressive disclosure (L1 manifest / L2 instructions / L3 resources).

Inspired by ADK ``SkillToolset`` (module_14) and Andrej Karpathy's LLM-Wiki
schema pattern. Module_24 uses the raw Anthropic-via-auggie path (no ADK
``Agent`` runtime), so we ship a small standalone loader that follows the same
contract:

    L1  list_skills()                  → [{"name", "description"}]   (always cheap)
    L2  load_skill(name)               → str (instructions body)     (on demand)
    L3  load_resource(name, rel_path)  → str (reference material)    (on demand)

A skill is a directory containing a ``SKILL.md`` whose front-matter is YAML
with at least ``name`` and ``description``. Optional ``references/`` holds
arbitrary markdown / text files that the model can request via L3.

Skills under :mod:`module_24_audit_ops.skills` are loaded eagerly on import
(metadata only) so the planner can include the manifest without paying the
full token cost. Skills under ``cfg.artifacts_dir/wiki/<target>/skills/``
(see :mod:`wiki`) are loaded *lazily* per-target as a dynamic ``audit-history``
skill — that is V3 of the plan.
"""
from __future__ import annotations

import logging
import pathlib
import re
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


# ----------------------------- types ----------------------------------------


@dataclass
class Skill:
    name: str
    description: str
    instructions: str
    directory: pathlib.Path
    triggers: List[str]  # recon-signal hints used for deterministic selection

    def manifest(self) -> Dict[str, str]:
        return {"name": self.name, "description": self.description}

    def list_resources(self) -> List[str]:
        ref_dir = self.directory / "references"
        if not ref_dir.is_dir():
            return []
        out: List[str] = []
        for p in sorted(ref_dir.rglob("*")):
            if p.is_file():
                out.append(str(p.relative_to(ref_dir)).replace("\\", "/"))
        return out

    def load_resource(self, rel_path: str) -> str:
        # Prevent path traversal — resource paths must stay under references/.
        ref_dir = (self.directory / "references").resolve()
        target = (ref_dir / rel_path).resolve()
        if not str(target).startswith(str(ref_dir)):
            raise ValueError(f"resource path escapes skill: {rel_path!r}")
        if not target.is_file():
            raise FileNotFoundError(f"no such resource: {rel_path!r}")
        return target.read_text(encoding="utf-8")


# ----------------------------- registry -------------------------------------


class SkillRegistry:
    """Thread-safe in-process registry of loaded skills."""

    def __init__(self) -> None:
        self._skills: Dict[str, Skill] = {}
        self._lock = threading.Lock()

    def register(self, skill: Skill) -> None:
        with self._lock:
            self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        with self._lock:
            if name not in self._skills:
                raise KeyError(f"unknown skill: {name!r}")
            return self._skills[name]

    def list(self) -> List[Skill]:
        with self._lock:
            return list(self._skills.values())

    def manifest(self) -> List[Dict[str, str]]:
        return [s.manifest() for s in self.list()]

    def by_triggers(self, signals: List[str]) -> List[Skill]:
        """Return skills whose triggers intersect the recon signals."""
        wanted = {s.lower().strip() for s in signals if s}
        out: List[Skill] = []
        for sk in self.list():
            if any(t.lower() in wanted for t in sk.triggers):
                out.append(sk)
        return out


# ----------------------------- parser ---------------------------------------


def _parse_frontmatter(text: str) -> tuple[Dict[str, object], str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("SKILL.md missing YAML front-matter (--- ... ---)")
    raw, body = m.group(1), m.group(2)
    meta: Dict[str, object] = {}
    # Tiny YAML subset (key: value / key: [a, b, c]) — avoids a hard PyYAML dep.
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid YAML line: {line!r}")
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            meta[k] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
        else:
            meta[k] = v.strip('"').strip("'")
    return meta, body.strip()


def load_skill_from_dir(directory: pathlib.Path) -> Skill:
    """Load a single skill from a directory containing SKILL.md."""
    skill_md = directory / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"no SKILL.md in {directory}")
    meta, body = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    name = str(meta.get("name") or "").strip()
    desc = str(meta.get("description") or "").strip()
    if not name:
        raise ValueError(f"SKILL.md at {directory} missing 'name'")
    if not desc:
        raise ValueError(f"SKILL.md at {directory} missing 'description'")
    triggers = meta.get("triggers") or []
    if isinstance(triggers, str):
        triggers = [t.strip() for t in triggers.split(",") if t.strip()]
    return Skill(
        name=name,
        description=desc,
        instructions=body,
        directory=directory.resolve(),
        triggers=list(triggers) if isinstance(triggers, list) else [],
    )


# ----------------------------- default registry -----------------------------


_DEFAULT_SKILLS_DIR = pathlib.Path(__file__).parent / "skills"
_default_registry: Optional[SkillRegistry] = None
_default_lock = threading.Lock()


def default_registry(reload: bool = False) -> SkillRegistry:
    """Return the process-wide registry of bundled module_24 skills."""
    global _default_registry
    with _default_lock:
        if _default_registry is None or reload:
            reg = SkillRegistry()
            if _DEFAULT_SKILLS_DIR.is_dir():
                for child in sorted(_DEFAULT_SKILLS_DIR.iterdir()):
                    if not child.is_dir():
                        continue
                    if not (child / "SKILL.md").is_file():
                        continue
                    try:
                        reg.register(load_skill_from_dir(child))
                    except Exception:
                        logger.exception("failed to load skill from %s", child)
            _default_registry = reg
        return _default_registry


# ----------------------------- recon → triggers -----------------------------


def recon_signals(recon: Optional[Dict[str, object]]) -> List[str]:
    """Map a recon dict to a list of skill trigger keywords.

    Pure function, deterministic — no LLM. Used by ``select_skills_for_recon``
    so the planner only carries L2 for relevant categories.

    Accepts both schemas:
      - ``security_headers`` (dict header→value/None, as ReconResult emits)
      - ``missing_headers``  (list of header names — convenience for callers)
      - form inputs may be under ``inputs`` *or* ``fields``
    """
    if not recon:
        return ["baseline"]
    out: List[str] = ["baseline"]

    missing_headers: List[str] = []
    headers = recon.get("security_headers") or {}
    if isinstance(headers, dict):
        for h, present in headers.items():
            if not present:
                missing_headers.append(h.lower())
    extra_missing = recon.get("missing_headers") or []
    if isinstance(extra_missing, list):
        for h in extra_missing:
            if isinstance(h, str):
                missing_headers.append(h.lower())
    for h in missing_headers:
        out.append(f"missing:{h}")
        if h == "strict-transport-security":
            out.append("crypto")
        if h in ("content-security-policy", "x-frame-options",
                 "x-content-type-options"):
            out.append("misconfig")

    forms = recon.get("forms") or []
    if isinstance(forms, list) and forms:
        out.append("forms")
        for f in forms:
            if not isinstance(f, dict):
                continue
            inputs = f.get("inputs") or f.get("fields") or []
            for i in inputs:
                if isinstance(i, dict) and (i.get("type") or "").lower() == "password":
                    out.append("auth")
                    out.append("access-control")
                    break
            method = (f.get("method") or "").upper()
            action = (f.get("action") or "").lower()
            if method in ("POST", "PUT", "PATCH"):
                out.append("injection")
            if "login" in action or "auth" in action or "signin" in action:
                out.append("auth")
                out.append("access-control")
    if recon.get("technologies"):
        out.append("misconfig")
    return out


def select_skills_for_recon(
    recon: Optional[Dict[str, object]],
    registry: Optional[SkillRegistry] = None,
) -> List[Skill]:
    """Deterministically pick which skills to inject into the planner prompt."""
    reg = registry or default_registry()
    signals = recon_signals(recon)
    picked = reg.by_triggers(signals)
    # Always include the recon-helpers skill if available — it's the cheapest L2.
    by_name = {s.name: s for s in reg.list()}
    if "recon-helpers" in by_name and by_name["recon-helpers"] not in picked:
        picked.insert(0, by_name["recon-helpers"])
    # Stable ordering by name for reproducibility (pytest snapshots).
    return sorted(picked, key=lambda s: s.name)


# ----------------------------- prompt rendering -----------------------------


def render_manifest_block(registry: Optional[SkillRegistry] = None) -> str:
    reg = registry or default_registry()
    lines = ["AVAILABLE SKILLS (L1 manifest — names + one-liner each):"]
    for m in reg.manifest():
        lines.append(f"- {m['name']}: {m['description']}")
    return "\n".join(lines)


def render_skill_block(skill: Skill, *, max_chars: int = 4000) -> str:
    body = skill.instructions
    if len(body) > max_chars:
        body = body[:max_chars] + "\n... [truncated]"
    return f"### SKILL: {skill.name}\n{skill.description}\n\n{body}\n"


def render_planner_context(
    recon: Optional[Dict[str, object]],
    registry: Optional[SkillRegistry] = None,
    extra_skills: Optional[List[Skill]] = None,
) -> str:
    """Compose the L1 manifest + L2 of the skills selected for this recon."""
    reg = registry or default_registry()
    picked = select_skills_for_recon(recon, registry=reg)
    seen = {s.name for s in picked}
    for s in extra_skills or []:
        if s.name not in seen:
            picked.append(s)
            seen.add(s.name)
    blocks = [render_manifest_block(reg), ""]
    blocks.append("LOADED L2 INSTRUCTIONS (selected by recon signals):")
    blocks.append("")
    for s in picked:
        blocks.append(render_skill_block(s))
    return "\n".join(blocks)
