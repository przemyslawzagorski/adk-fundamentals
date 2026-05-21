"""E2E: globalny handler bledow + kontent-negocjacja HTML/JSON."""

from __future__ import annotations


def test_should_return_json_error_when_accept_is_json(client, auth_headers):
    r = client.get(
        "/repos/deadbeef",
        headers={**auth_headers, "accept": "application/json"},
    )
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert "error" in body


def test_should_return_html_error_when_accept_is_html(client, auth_headers):
    r = client.get(
        "/repos/deadbeef",
        headers={**auth_headers, "accept": "text/html"},
    )
    assert r.status_code == 404
    assert "alert" in r.text.lower() or "error" in r.text.lower()


def test_should_return_401_json_when_no_key_and_json_accept(client):
    r = client.get(
        "/",
        headers={"accept": "application/json"},
    )
    assert r.status_code == 401
    body = r.json()
    assert body["ok"] is False
    assert "error" in body


def test_should_return_index_status_empty_when_no_indexing(
    added_repo, client, auth_headers
):
    r = client.get(
        f"/repos/{added_repo['id']}/index/status",
        headers=auth_headers,
    )
    assert r.status_code == 200
    # Pusty HTML gdy brak aktywnego indeksowania
    assert r.text == "" or "indexing-progress" not in r.text
