"""E2E: CRUD repozytoriow (add / list / delete / dup / invalid path)."""

from __future__ import annotations


def test_should_add_repo_when_path_is_valid(client, sample_repo, auth_headers):
    r = client.post(
        "/repos",
        data={"path": str(sample_repo), "name": "sample-ok"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert "Dodano" in r.text


def test_should_return_400_when_path_is_invalid(client, auth_headers):
    r = client.post(
        "/repos",
        data={"path": "/nie/istnieje/zupelnie/nigdy", "name": ""},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "error" in r.text.lower() or "alert" in r.text.lower()


def test_should_return_400_when_duplicate_repo(client, sample_repo, auth_headers):
    # 1. dodaj
    client.post(
        "/repos",
        data={"path": str(sample_repo), "name": "dup1"},
        headers=auth_headers,
    )
    # 2. dodaj ponownie ten sam path
    r = client.post(
        "/repos",
        data={"path": str(sample_repo), "name": "dup2"},
        headers=auth_headers,
    )
    assert r.status_code == 400
    assert "juz zarejestrowane" in r.text.lower() or "rejestrowane" in r.text.lower()


def test_should_show_repo_on_dashboard_after_add(added_repo, client, auth_headers):
    r = client.get("/", headers=auth_headers)
    assert r.status_code == 200
    assert f"/repos/{added_repo['id']}" in r.text


def test_should_open_repo_detail_when_repo_exists(added_repo, client, auth_headers):
    r = client.get(f"/repos/{added_repo['id']}", headers=auth_headers)
    assert r.status_code == 200
    assert "sample" in r.text.lower() or "repo" in r.text.lower()


def test_should_return_404_when_repo_detail_not_found(client, auth_headers):
    r = client.get("/repos/deadbeef", headers=auth_headers)
    assert r.status_code == 404


def test_should_delete_repo_when_exists(added_repo, client, auth_headers):
    r = client.delete(f"/repos/{added_repo['id']}", headers=auth_headers)
    assert r.status_code == 200
    # Po usunieciu - szczegoly = 404
    r2 = client.get(f"/repos/{added_repo['id']}", headers=auth_headers)
    assert r2.status_code == 404


def test_should_return_404_when_deleting_nonexistent_repo(client, auth_headers):
    r = client.delete("/repos/00000000", headers=auth_headers)
    assert r.status_code == 404
