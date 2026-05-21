# Path traversal — dlaczego `safe_resolve`

Jedna z najczęstszych podatności aplikacji z operacjami na plikach: użytkownik podaje `../../etc/passwd`, aplikacja naiwnie skleja ścieżki i czyta cudzy plik.

Code Analyst przechodzi **każdą** operację na pliku przez `security.safe_resolve` — i dopiero po walidacji dotyka dysku.

## Anatomia ataku

```
repo_path      = /app/repos/acme
file_path      = ../../etc/passwd
naive_join     = /app/repos/acme/../../etc/passwd
normpath       = /etc/passwd     ← upppps
open(normpath) → czytamy cudzy plik systemowy
```

Dodatkowe wektory:

- **Symlink escape**: w repo jest `link → /etc`, agent czyta `link/passwd`.
- **Prefix trap**: `repo_path = /repo`, napastnik prosi o plik spoza repo, ale w katalogu `/repo-evil/x` (oba zaczynają się od `/repo`).
- **Null byte injection**: `file.txt\x00.jpg` — stare API C.
- **Ścieżka absolutna**: użytkownik wysyła `/etc/passwd` bezpośrednio.

## Jak broni się `safe_resolve`

```python
def safe_resolve(repo_path: str, relative_path: str) -> str:
    if not relative_path or "\x00" in relative_path:
        raise PathSecurityError("Niepoprawna ścieżka (pusta lub zawiera NUL).")

    if os.path.isabs(relative_path):
        raise PathSecurityError("Ścieżka absolutna jest niedozwolona.")

    repo_real = os.path.realpath(repo_path)
    candidate = os.path.realpath(os.path.join(repo_real, relative_path))

    if not (candidate == repo_real or candidate.startswith(repo_real + os.sep)):
        raise PathSecurityError(f"Ścieżka poza repozytorium: {relative_path}")
    return candidate
```

### Co robi każda linia?

1. **NUL byte + empty check**: odrzucamy `""` i `"file\x00.txt"`.
2. **Absolute path check**: `os.path.isabs("/etc/passwd")` = `True` → odrzucamy.
3. **`realpath` na repo**: rozwijamy symlinki w samym `repo_path` (np. `/app/repos` → `/data/repos`).
4. **`realpath` na kandydacie**: rozwijamy symlinki w docelowym pliku — to ochrona przed symlink escape.
5. **Porównanie z separatorem**: `candidate.startswith(repo_real + os.sep)` — zapobiega atakom typu `/repo` ⊂ `/repo-evil/x`.

!!! warning "Pułapka `startswith` bez separatora"
    Gdyby kod sprawdzał `candidate.startswith(repo_real)`:

    ```
    repo_real = /app/repos/acme
    candidate = /app/repos/acme-evil/data.txt
    startswith? → TAK (bez separatora)
    ```

    Z `os.sep`:

    ```
    repo_real + os.sep = /app/repos/acme/
    candidate          = /app/repos/acme-evil/data.txt
    startswith?        → NIE
    ```

    Fix: zawsze porównuj z separatorem (lub użyj `os.path.commonpath`).

## Testy jednostkowe

Z [`tests/test_security.py`](../deweloper/testy.md):

```python
class TestSafeResolve:

    def test_blocks_parent_traversal(self, tmp_path):
        with pytest.raises(PathSecurityError):
            safe_resolve(str(tmp_path), "../../etc/passwd")

    def test_blocks_absolute_path(self, tmp_path):
        with pytest.raises(PathSecurityError):
            safe_resolve(str(tmp_path), "/etc/passwd")

    def test_blocks_null_byte(self, tmp_path):
        with pytest.raises(PathSecurityError):
            safe_resolve(str(tmp_path), "a\x00b")

    def test_blocks_prefix_trap(self, tmp_path):
        # /tmp/xxx/repo i /tmp/xxx/repo-evil
        (tmp_path / "repo-evil").mkdir()
        (tmp_path / "repo").mkdir()
        repo = str(tmp_path / "repo")
        with pytest.raises(PathSecurityError):
            safe_resolve(repo, "../repo-evil/data.txt")

    def test_allows_valid_relative(self, tmp_path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("x=1")
        result = safe_resolve(str(tmp_path), "src/main.py")
        assert result.endswith("main.py")

    @pytest.mark.skipif(os.name == "nt", reason="symlinks nie sa dostepne")
    def test_blocks_symlink_escape(self, tmp_path):
        # repo/link -> /etc
        outside = tmp_path.parent / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("secret")
        link = tmp_path / "link"
        os.symlink(str(outside), str(link))
        with pytest.raises(PathSecurityError):
            safe_resolve(str(tmp_path), "link/secret.txt")
```

## Drugi mur — `is_secret_file`

Nawet jeśli path traversal zostanie pominięty (np. symlink z repo do `.env` wewnątrz repo), `file_tools.read_project_file` wywoła `is_secret_file(full_path)`:

```python
SECRET_FILE_NAMES = frozenset({
    ".env", ".env.local", ".env.production", ".env.template",
    "credentials.json", "service-account.json",
    "id_rsa", "id_ed25519", ".netrc", ".pgpass",
})

def is_secret_file(filename: str) -> bool:
    base = os.path.basename(filename).lower()
    return base in SECRET_FILE_NAMES or base.endswith(".pem") or base.endswith(".key")
```

Reguła: **jeśli wygląda jak sekret, nie tykamy**. Zarówno przy odczycie, zapisie, jak i listowaniu.

## Trzeci mur — symlink escape w `write_project_file`

```python
if dir_path:
    os.makedirs(dir_path, exist_ok=True)
    repo_real = os.path.realpath(repo_path)
    if not os.path.realpath(dir_path).startswith(repo_real):
        return _err("Utworzono symlink poza repo — odmowa zapisu.")
```

Po `makedirs` sprawdzamy ponownie — bo `makedirs` mogło przejść przez symlink (np. katalog docelowy istniał jako symlink stworzony wcześniej).

## Podsumowanie

| Wektor | Ochrona |
|--------|---------|
| `../../etc/passwd` | `realpath` + `startswith(repo_real + os.sep)` |
| Symlink escape | `realpath` po obu stronach |
| Prefix trap | `os.sep` w porównaniu |
| Null byte | Explicit check `\x00` |
| Ścieżka absolutna | `os.path.isabs` check |
| Pliki sekretów | `is_secret_file` blacklist |
| Symlink przed zapisem | Ponowny `realpath` po `makedirs` |

Następnie: [Prompt injection](prompt-injection.md).
