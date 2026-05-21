"""
Build Tools — kompilacja i testy projektu (subprocess, shell=False).
====================================================================
Auto-detect: Maven / Gradle / Python / npm. Timeouty z konfiguracji.
"""

from __future__ import annotations

import os
import subprocess
from typing import Any

from config import get_settings
from logging_config import get_logger
from security import is_within

log = get_logger(__name__)


def _ok(**payload: Any) -> dict:
    return {"ok": True, **payload}


def _err(message: str, **extra: Any) -> dict:
    return {"ok": False, "error": message, **extra}


def _detect_build_system(repo_path: str) -> str:
    checks = [
        ("pom.xml", "maven"),
        ("build.gradle", "gradle"),
        ("build.gradle.kts", "gradle"),
        ("pyproject.toml", "python"),
        ("setup.py", "python"),
        ("requirements.txt", "python"),
        ("package.json", "npm"),
    ]
    for filename, system in checks:
        if os.path.isfile(os.path.join(repo_path, filename)):
            return system
    return "unknown"


def _run_cmd(repo_path: str, cmd: list[str], timeout: int) -> dict:
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        max_out = 8000
        stdout = result.stdout[-max_out:] if len(result.stdout) > max_out else result.stdout
        stderr = result.stderr[-max_out:] if len(result.stderr) > max_out else result.stderr
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "exit_code": -1, "stdout": "", "stderr": "TIMEOUT"}
    except FileNotFoundError as e:
        return {"success": False, "exit_code": -1, "stdout": "", "stderr": f"Komenda niedostępna: {e}"}


def run_build(repo_path: str) -> dict:
    """Kompilacja — auto-detect systemu budowania."""
    settings = get_settings()
    build_system = _detect_build_system(repo_path)

    if build_system == "maven":
        result = _run_cmd(repo_path, ["mvn", "compile", "-q"], settings.build_timeout)
    elif build_system == "gradle":
        wrapper = os.path.join(repo_path, "gradlew.bat" if os.name == "nt" else "gradlew")
        cmd = [wrapper] if os.path.isfile(wrapper) else ["gradle"]
        result = _run_cmd(repo_path, [*cmd, "compileJava", "-q"], settings.build_timeout)
    elif build_system == "python":
        py_files: list[str] = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [
                d for d in dirs
                if d not in {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache"}
            ]
            for f in files:
                if f.endswith(".py"):
                    full = os.path.join(root, f)
                    if is_within(repo_path, full):
                        py_files.append(full)

        total = len(py_files)
        limit = min(total, settings.max_py_compile_files)
        errors: list[str] = []
        for pf in py_files[:limit]:
            r = _run_cmd(repo_path, ["python", "-m", "py_compile", pf], timeout=10)
            if not r["success"]:
                rel = os.path.relpath(pf, repo_path)
                errors.append(f"{rel}: {r['stderr'].strip()}")

        result = {
            "success": len(errors) == 0,
            "exit_code": 0 if not errors else 1,
            "stdout": f"Sprawdzono {limit}/{total} plików Python",
            "stderr": "\n".join(errors),
        }
    else:
        return _err(
            "Nie rozpoznano systemu budowania (brak pom.xml, build.gradle, pyproject.toml…)",
            build_system="unknown",
        )

    if not result["success"]:
        log.warning("run_build FAILED (%s): %s", build_system, result["stderr"][:300])

    return _ok(
        success=result["success"],
        build_system=build_system,
        output=result["stdout"],
        errors=result["stderr"] if not result["success"] else "",
        message="BUILD SUCCESS" if result["success"] else "BUILD FAILED",
    )


def run_tests(repo_path: str, test_filter: str = "") -> dict:
    """Uruchom testy — auto-detect."""
    settings = get_settings()
    build_system = _detect_build_system(repo_path)
    test_filter = test_filter.strip()

    # Walidacja filtra — nie pozwól na wstrzyknięcie flag
    if test_filter and any(c in test_filter for c in (";", "|", "&", "$", "`", "\n")):
        return _err("Niedozwolone znaki w test_filter.")

    if build_system == "maven":
        cmd = ["mvn", "test", "-q"]
        if test_filter:
            cmd.append(f"-Dtest={test_filter}")
        result = _run_cmd(repo_path, cmd, settings.test_timeout)
    elif build_system == "gradle":
        wrapper = os.path.join(repo_path, "gradlew.bat" if os.name == "nt" else "gradlew")
        cmd = [wrapper] if os.path.isfile(wrapper) else ["gradle"]
        cmd += ["test"]
        if test_filter:
            cmd.append(f"--tests={test_filter}")
        result = _run_cmd(repo_path, cmd, settings.test_timeout)
    elif build_system == "python":
        cmd = ["python", "-m", "pytest", "-v", "--tb=short"]
        if test_filter:
            cmd += ["-k", test_filter]
        result = _run_cmd(repo_path, cmd, settings.test_timeout)
    else:
        return _err(
            "Nie rozpoznano systemu budowania dla testów.",
            build_system="unknown",
        )

    return _ok(
        success=result["success"],
        build_system=build_system,
        test_filter=test_filter or "(wszystkie)",
        output=result["stdout"],
        errors=result["stderr"] if not result["success"] else "",
        message="TESTS PASSED" if result["success"] else "TESTS FAILED",
    )
