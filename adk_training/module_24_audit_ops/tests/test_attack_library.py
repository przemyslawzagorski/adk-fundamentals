"""Tests for the deterministic attack library scenario factories."""
from __future__ import annotations

from adk_training.module_24_audit_ops.attack_library import (
    build_default_pack,
    scenario_clickjacking,
    scenario_cookie_flags,
    scenario_exposed_files,
    scenario_open_redirect,
    scenario_security_headers,
    scenario_smoke_navigation,
    scenario_xss_reflected,
)
from adk_training.module_24_audit_ops.recon import ReconResult


def _empty_recon(url: str = "https://example.com/") -> ReconResult:
    return ReconResult(target_url=url, final_url=url, status_code=200)


def _all_steps_have_action(scenario):
    for step in scenario["steps"]:
        assert "action" in step, f"step missing action: {step}"


def test_smoke_scenario_shape():
    sc = scenario_smoke_navigation("https://example.com/")
    assert sc["id"] == "smoke_navigation"
    _all_steps_have_action(sc)
    actions = [s["action"] for s in sc["steps"]]
    assert "goto" in actions
    assert "screenshot" in actions


def test_security_headers_scenario_has_findings():
    sc = scenario_security_headers("https://example.com/")
    assert sc["owasp"].startswith("A05")
    fail_findings = [s for s in sc["steps"] if "fail_finding" in s]
    assert len(fail_findings) >= 4
    for s in fail_findings:
        assert s["fail_finding"]["title"]
        assert s["fail_finding"]["severity"] in {"critical", "high", "medium", "low", "info"}


def test_open_redirect_scenario_uses_target_origin():
    sc = scenario_open_redirect("https://example.com/")
    expects = [s for s in sc["steps"] if s["action"] == "expect_origin"]
    assert expects
    for s in expects:
        assert s["equals"] == "https://example.com"


def test_clickjacking_scenario_minimal():
    sc = scenario_clickjacking("https://example.com/")
    assert sc["steps"][0]["action"] == "goto"
    assert any(s["action"] == "expect_frame_ancestors_or_xfo" for s in sc["steps"])


def test_cookie_scenario_has_assertion():
    sc = scenario_cookie_flags("https://example.com/")
    assert any(s["action"] == "expect_cookies_secure" for s in sc["steps"])


def test_exposed_files_only_includes_sensitive_200_paths():
    recon = _empty_recon()
    recon.interesting_paths = [
        {"path": "/.git/config", "url": "https://example.com/.git/config", "status": 200, "content_type": "text/plain", "size": 100},
        {"path": "/healthz", "url": "https://example.com/healthz", "status": 200, "content_type": "text/plain", "size": 2},
        {"path": "/.env", "url": "https://example.com/.env", "status": 401, "content_type": "text/plain", "size": 0},
    ]
    sc = scenario_exposed_files("https://example.com/", recon)
    fetch_urls = [s["url"] for s in sc["steps"] if s["action"] == "fetch_url"]
    # /.git/config should be there, /healthz is not in sensitive list, /.env was 401
    assert "https://example.com/.git/config" in fetch_urls
    assert "https://example.com/healthz" not in fetch_urls
    assert "https://example.com/.env" not in fetch_urls


def test_xss_skipped_when_no_forms():
    recon = _empty_recon()
    sc = scenario_xss_reflected("https://example.com/", recon)
    assert "skipped" in sc["name"].lower()
    assert sc["severity"] == "info"


def test_xss_includes_canary_when_form_present():
    recon = _empty_recon()
    recon.forms = [{
        "action": "https://example.com/search",
        "method": "GET",
        "inputs": [{"name": "q", "type": "text"}],
    }]
    sc = scenario_xss_reflected("https://example.com/", recon)
    fills = [s for s in sc["steps"] if s["action"] == "fill"]
    assert fills
    assert any("audopsXSS" in s["value"] for s in fills)
    # Negated expect_text — canary must NOT be in response
    expects = [s for s in sc["steps"] if s["action"] == "expect_text"]
    assert any(s.get("negate") and "audopsXSS" in s["contains"] for s in expects)


def test_default_pack_respects_max_count():
    recon = _empty_recon()
    pack = build_default_pack("https://example.com/", recon, max_count=3)
    assert len(pack) == 3
    # Smoke first
    assert pack[0]["id"] == "smoke_navigation"


def test_default_pack_full():
    recon = _empty_recon()
    pack = build_default_pack("https://example.com/", recon, max_count=99)
    ids = [s["id"] for s in pack]
    for expected in ("smoke_navigation", "headers_baseline", "cookie_flags",
                     "clickjacking", "exposed_files", "open_redirect", "xss_reflected"):
        assert expected in ids, f"{expected} missing from default pack"
