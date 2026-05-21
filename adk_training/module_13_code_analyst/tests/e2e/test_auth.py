"""E2E: autoryzacja (X-API-Key / ?api_key=, constant-time)."""

from __future__ import annotations


def test_should_return_401_when_dashboard_without_key(client):
    r = client.get("/")
    assert r.status_code == 401
    assert "Invalid API key" in r.text


def test_should_return_200_when_dashboard_with_valid_header_key(client, auth_headers):
    r = client.get("/", headers=auth_headers)
    assert r.status_code == 200
    assert "<html" in r.text.lower() or "dashboard" in r.text.lower()


def test_should_return_200_when_dashboard_with_valid_query_key(client, api_key):
    r = client.get(f"/?api_key={api_key}")
    assert r.status_code == 200


def test_should_return_401_when_dashboard_with_wrong_key(client):
    r = client.get("/", headers={"x-api-key": "zle-zle-zle"})
    assert r.status_code == 401


def test_should_bypass_auth_for_public_paths(client):
    # public paths (prefix matching w _require_api_key)
    for path in ["/health", "/ready"]:
        r = client.get(path)
        assert r.status_code == 200, f"{path} powinno byc publiczne"


def test_should_accept_both_header_and_query_the_same_key(client, api_key):
    r1 = client.get("/", headers={"x-api-key": api_key})
    r2 = client.get(f"/?api_key={api_key}")
    assert r1.status_code == r2.status_code == 200
