"""E2E: health / ready / metrics (sciezki publiczne — bez auth)."""

from __future__ import annotations


def test_should_return_200_when_health_without_auth(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_should_return_200_when_ready_without_auth(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert "ready" in r.json()


def test_should_return_prometheus_text_when_metrics_requested(client):
    r = client.get("/metrics")
    # Gdy prometheus_client nie jest zainstalowany - endpoint nie istnieje (404).
    if r.status_code == 404:
        return
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    # Typowa metryka Pythona z default registry
    assert "python_info" in r.text or "process_" in r.text


def test_should_set_request_id_header_on_every_response(client):
    r = client.get("/health")
    assert r.headers.get("x-request-id"), "middleware nie dodal X-Request-ID"
