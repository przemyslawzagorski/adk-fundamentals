"""Tests for the auth vault."""
import pytest

from adk_training.module_24_audit_ops.auth import (
    AuthStore, make_auth, redact_for_logging,
)


def test_make_auth_validates_cookie_shape():
    with pytest.raises(ValueError):
        make_auth(cookies=[{"value": "x"}])  # no name


def test_make_auth_rejects_crlf_header():
    with pytest.raises(ValueError):
        make_auth(headers={"X-Inj": "v\r\nSet-Cookie: pwn"})


def test_make_auth_rejects_bad_header_name():
    with pytest.raises(ValueError):
        make_auth(headers={"X Bad": "v"})


def test_auth_store_roundtrip():
    s = AuthStore()
    ctx = make_auth(label="staging", cookies=[{"name": "sid", "value": "abc"}],
                    headers={"X-Trace": "1"})
    s.add(ctx)
    assert s.get(ctx.id) is ctx
    assert s.get("nope") is None


def test_auth_fingerprint_hides_values():
    ctx = make_auth(label="x",
                    cookies=[{"name": "sid", "value": "TOPSECRET"}],
                    headers={"Authorization": "Bearer TOPSECRET"})
    fp = ctx.fingerprint()
    assert fp["cookie_names"] == ["sid"]
    assert "Authorization" in fp["header_names"]
    # No raw values surface anywhere
    assert "TOPSECRET" not in repr(fp)


def test_auth_store_remove():
    s = AuthStore()
    ctx = make_auth(label="x", headers={"X-A": "1"})
    s.add(ctx)
    assert s.remove(ctx.id) is True
    assert s.remove(ctx.id) is False


def test_auth_store_list_returns_only_fingerprints():
    s = AuthStore()
    ctx = make_auth(label="x",
                    cookies=[{"name": "sid", "value": "secret"}])
    s.add(ctx)
    rows = s.list()
    assert rows[0]["cookie_names"] == ["sid"]
    # No "value" key and no secret bleed
    assert "secret" not in repr(rows)


def test_redact_for_logging_handles_nested():
    payload = {
        "url": "https://x",
        "headers": {"Authorization": "Bearer X"},
        "items": [{"api_key": "k", "label": "ok"}],
    }
    red = redact_for_logging(payload)
    assert red["headers"]["Authorization"] == "[REDACTED]"
    assert red["items"][0]["api_key"] == "[REDACTED]"
    assert red["items"][0]["label"] == "ok"
    assert red["url"] == "https://x"
