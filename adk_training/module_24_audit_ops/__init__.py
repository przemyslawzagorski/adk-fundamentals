"""
Module 24 — AuditOps: Autonomous Web Security Agent

LLM-driven penetration testing platform built on top of:
- Playwright (Python) — browser automation + video evidence
- Module 23 Auggie integration — LLM scenario generation (Claude Sonnet 4.5)
- ADK SequentialAgent pattern — recon → plan → write → execute → report

Two modes:
- Mode A (Auto-Pentest): give URL only, agent generates scenarios from OWASP Top 10
- Mode B (Guided): user describes a scenario in NL, agent translates to Playwright

Safety: domain allowlist, rate limiting, mandatory legal disclaimer acknowledgment.
"""

__version__ = "0.1.0"
