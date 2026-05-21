"""
File tools — read files, write documents to output directory.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_BLOCKED_PATTERNS = ("/etc/shadow", "/etc/passwd", "\\windows\\system32")


def read_file(file_path: str) -> dict:
    """Read content of a file from the project.

    Args:
        file_path: Absolute or relative path to the file to read.

    Returns:
        dict with 'status', 'content', and 'path' or 'error_message'.
    """
    try:
        path = Path(file_path).resolve()
        path_lower = str(path).lower()
        if any(blocked in path_lower for blocked in _BLOCKED_PATTERNS):
            logger.warning("read_file: blocked path %s", file_path)
            return {"status": "error", "error_message": f"Access denied: {file_path}"}
        if not path.is_file():
            return {"status": "error", "error_message": f"File not found: {file_path}"}
        content = path.read_text(encoding="utf-8")
        return {"status": "ok", "content": content, "path": str(path)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def write_document(
    file_name: str,
    content: str,
    subdirectory: str = "",
) -> dict:
    """Write a generated document to the output directory.

    The output directory is configured via OUTPUT_DIR env var (default: ./output).

    Args:
        file_name: Name of the file to write (e.g. 'hld-billing.md').
        content: Full content to write.
        subdirectory: Optional subdirectory under OUTPUT_DIR (e.g. 'epics').

    Returns:
        dict with 'status' and 'path' or 'error_message'.
    """
    try:
        base = Path(os.environ.get("OUTPUT_DIR", "./output")).resolve()
        target_dir = (base / subdirectory).resolve() if subdirectory else base
        target_path = (target_dir / file_name).resolve()

        # Security: ensure resolved path stays within OUTPUT_DIR
        if not str(target_path).startswith(str(base)):
            logger.warning("write_document: path escape blocked: %s", target_path)
            return {"status": "error", "error_message": f"Access denied: path escapes output directory"}
        if not str(target_dir).startswith(str(base)):
            logger.warning("write_document: subdirectory escape blocked: %s", target_dir)
            return {"status": "error", "error_message": f"Access denied: subdirectory escapes output directory"}

        target_dir.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        return {"status": "ok", "path": str(target_path)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_files(directory: str, pattern: str = "*.md") -> dict:
    """List files in a directory matching a glob pattern.

    Args:
        directory: Path to the directory to list.
        pattern: Glob pattern to match (default: '*.md').

    Returns:
        dict with 'status' and 'files' list or 'error_message'.
    """
    try:
        path = Path(directory).resolve()
        if not path.is_dir():
            return {"status": "error", "error_message": f"Directory not found: {directory}"}
        files = sorted(str(f.relative_to(path)) for f in path.rglob(pattern))
        return {"status": "ok", "files": files, "count": len(files)}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
