"""Tests for the new OWASP scenarios."""
from adk_training.module_24_audit_ops.attack_library import (
    build_default_pack, scenario_cors_misconfig, scenario_mixed_content,
    scenario_sensitive_storage, scenario_sqli_sniff,
)
from adk_training.module_24_audit_ops.dsl import validate_scenario
from adk_training.module_24_audit_ops.recon import ReconResult


def _empty_recon():
    return ReconResult(target_url="https://example.test")


def _recon_with_form():
    r = _empty_recon()
    r.forms.append({
        "action": "https://example.test/login",
        "method": "post",
        "inputs": [{"name": "q", "type": "text"}],
    })
    return r


def test_cors_scenario_passes_dsl_validation():
    sc = scenario_cors_misconfig("https://example.test/")
    validate_scenario(sc)
    assert sc["owasp"].startswith("A05")


def test_sqli_skips_when_no_forms():
    sc = scenario_sqli_sniff("https://example.test/", _empty_recon())
    validate_scenario(sc)
    assert "skipped" in sc["name"].lower()


def test_sqli_uses_first_form():
    sc = scenario_sqli_sniff("https://example.test/", _recon_with_form())
    validate_scenario(sc)
    actions = [s["action"] for s in sc["steps"]]
    assert "fill" in actions
    assert "expect_no_sql_error" in actions
    # Make sure we never craft anything more invasive than a single quote.
    fills = [s for s in sc["steps"] if s["action"] == "fill"]
    assert all(s["value"] == "'" for s in fills)


def test_mixed_content_scenario_shape():
    sc = scenario_mixed_content("https://example.test/")
    validate_scenario(sc)
    assert sc["owasp"].startswith("A02")


def test_sensitive_storage_scenario_shape():
    sc = scenario_sensitive_storage("https://example.test/")
    validate_scenario(sc)
    actions = [s["action"] for s in sc["steps"]]
    assert "expect_storage_clean" in actions


def test_default_pack_includes_new_scenarios_when_room():
    pack = build_default_pack("https://example.test/", _recon_with_form(), max_count=20)
    ids = {sc["id"] for sc in pack}
    for expected in {"cors_misconfig", "sqli_sniff", "mixed_content", "sensitive_storage"}:
        assert expected in ids


def test_default_pack_respects_max_count():
    pack = build_default_pack("https://example.test/", _empty_recon(), max_count=5)
    assert len(pack) == 5
    # Smoke navigation must always come first
    assert pack[0]["id"] == "smoke_navigation"


def test_every_default_pack_scenario_is_dsl_valid():
    pack = build_default_pack("https://example.test/", _recon_with_form(), max_count=20)
    for sc in pack:
        validate_scenario(sc)
