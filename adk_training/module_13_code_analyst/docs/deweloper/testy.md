# Testy

Suite: 50+ testów, [`pytest`](https://docs.pytest.org), `pytest-asyncio` dla endpointów async. Cel — coverage bezpieczeństwa i regresja RAG.

## Uruchamianie

```powershell
# cała suite
pytest

# zatrzymaj się na pierwszym fail
pytest -x

# verbose
pytest -v

# tylko bezpieczeństwo
pytest -k "security"

# konkretna klasa
pytest tests/test_security.py::TestSafeResolve

# coverage
pytest --cov=. --cov-report=html
# otwórz htmlcov/index.html
```

## Struktura

```
tests/
├── __init__.py
├── test_config.py          # Settings validation
├── test_security.py        # safe_resolve, sanitize, is_secret
└── test_file_tools.py      # read/write/list + guardy
```

!!! note "Dlaczego nie ma `test_agent.py`?"
    Testowanie agentów LLM wymaga mocka `Runner` i jest kruche. Zamiast testów unit
    mamy **smoke-testy manualne** w [ścieżce krytycznej](#smoke-testy-manualne).

## test_security.py — przykłady

### `TestSafeResolve`

```python
def test_blocks_parent_traversal(tmp_path):
    with pytest.raises(PathSecurityError):
        safe_resolve(str(tmp_path), "../../etc/passwd")

def test_blocks_absolute_path(tmp_path):
    with pytest.raises(PathSecurityError):
        safe_resolve(str(tmp_path), "/etc/passwd")

def test_blocks_null_byte(tmp_path):
    with pytest.raises(PathSecurityError):
        safe_resolve(str(tmp_path), "a\x00b")

def test_blocks_prefix_trap(tmp_path):
    (tmp_path / "repo-evil").mkdir()
    (tmp_path / "repo").mkdir()
    with pytest.raises(PathSecurityError):
        safe_resolve(str(tmp_path / "repo"), "../repo-evil/data.txt")
```

### `TestSecretFileDetection`

```python
@pytest.mark.parametrize("name", [".env", "id_rsa", "key.pem", "credentials.json"])
def test_detects_secret(name):
    assert is_secret_file(f"/x/{name}") is True

@pytest.mark.parametrize("name", ["main.py", "README.md", "config.toml"])
def test_allows_regular(name):
    assert is_secret_file(f"/x/{name}") is False
```

### `TestSanitizeInput`

```python
def test_limits_length():
    text = "x" * 5000
    assert len(sanitize_user_input(text)) <= 2000

def test_escapes_braces():
    assert "{{" in sanitize_user_input("{leak}")

def test_strips_control_chars():
    assert "\x00" not in sanitize_user_input("a\x00b")
```

## test_file_tools.py — przykłady

```python
class TestRead:
    def test_reads_file(self, tmp_path):
        (tmp_path / "a.py").write_text("x=1")
        result = read_project_file(str(tmp_path), "a.py")
        assert result["ok"] is True
        assert "x=1" in result["content"]

    def test_blocks_secret_file(self, tmp_path):
        (tmp_path / ".env").write_text("SECRET=1")
        result = read_project_file(str(tmp_path), ".env")
        assert result["ok"] is False
        assert "sekret" in result["error"].lower()

    def test_blocks_path_traversal(self, tmp_path):
        result = read_project_file(str(tmp_path), "../../etc/passwd")
        assert result["ok"] is False
```

## test_config.py — przykłady

```python
def test_port_validation():
    with pytest.raises(ValidationError):
        Settings(port=99999)

def test_defaults():
    s = Settings()
    assert s.chunk_size == 768
    assert s.rate_limit_index == "2/minute"
```

## Fixtures

W `conftest.py` (generowany implicit w pytest — u nas brak, bo proste fixtures):

```python
@pytest.fixture
def tmp_repo(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def f(): return 42")
    (tmp_path / "README.md").write_text("# Demo")
    return tmp_path
```

## Smoke-testy manualne

Dla agenta LLM nie ma zautomatyzowanych testów — zamiast tego checklist po każdej
większej zmianie:

1. `python -m uvicorn web.app:app` — aplikacja wstaje.
2. `/health` zwraca `{"status":"ok"}`.
3. `/ready` zwraca `ready: true` (wymaga skonfigurowanego LLM).
4. Dodaj repo, zaindeksuj — widać statystyki.
5. Search: zapytanie → wyniki z kodem + ścieżki.
6. Chat: "gdzie jest autoryzacja" → sensowna odpowiedź z referencjami.
7. Workflow `code_review` → multi-step response.
8. Wyślij w chat: `<script>alert(1)</script>` → wyświetla jako tekst.
9. Wyślij: `../../etc/passwd` jako path — odmowa.
10. 30 requestów w sekundę do `/search` — 429 po limicie.

## CI — GitHub Actions

`.github/workflows/code-analyst.yml`:

```yaml
- name: Install
  run: pip install -r requirements.txt -r requirements-dev.txt
- name: Lint
  run: ruff check .
- name: Format check
  run: ruff format --check .
- name: Tests
  run: pytest --cov=. --cov-report=xml
- name: Docker build
  run: docker build -t code-analyst:ci .
```

CI działa na push do `main` i PR. Green CI = mergeable.

## Coverage baseline

Obecny stan (orientacyjnie, bez LLM):

| Moduł | Coverage |
|-------|----------|
| `security.py` | 95%+ |
| `file_tools.py` | 90% |
| `config.py` | 85% |
| `code_indexer.py` | ~40% (wymaga LLM) |
| `web/app.py` | ~50% (wymaga Runner mock) |

Nie gonimy za 100% — gonimy **coverage bezpieczeństwa**.

Następnie: [Rozszerzanie](rozszerzanie.md).
