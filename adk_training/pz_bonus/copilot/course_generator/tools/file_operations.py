"""
📁 File Operations Tool
Narzędzie do operacji na plikach dla course_generator
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def create_file(file_path: str, content: str) -> str:
    """
    Creates a file with the given content.

    Args:
        file_path: ABSOLUTE or relative path to the file (e.g., "output/copilot_training/tier_1_critical/module_01/README.md")
        content: File content

    Returns:
        Success message with full path

    Note:
        Agent should provide FULL path including output directory.
        No base_dir manipulation to avoid double nesting (output/output/...).
    """
    try:
        full_path = Path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        full_path.write_text(content, encoding='utf-8')

        logger.info(f"Created file: {full_path}")
        return f"✅ Created: {full_path}"

    except Exception as e:
        logger.error(f"Error creating file {file_path}: {e}")
        return f"❌ Error: {e}"


def create_directory(dir_path: str) -> str:
    """
    Creates a directory.

    Args:
        dir_path: ABSOLUTE or relative path to the directory

    Returns:
        Success message with full path

    Note:
        Agent should provide FULL path including output directory.
        No base_dir manipulation to avoid double nesting.
    """
    try:
        full_path = Path(dir_path)
        full_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created directory: {full_path}")
        return f"✅ Created directory: {full_path}"

    except Exception as e:
        logger.error(f"Error creating directory {dir_path}: {e}")
        return f"❌ Error: {e}"


def read_file(file_path: str) -> str:
    """
    Reads content from a file.

    Args:
        file_path: ABSOLUTE or relative path to the file

    Returns:
        File content or error message
    """
    try:
        full_path = Path(file_path)

        if not full_path.exists():
            return f"❌ File not found: {full_path}"

        content = full_path.read_text(encoding='utf-8')
        return content

    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"❌ Error: {e}"


def list_files(directory: str = ".") -> str:
    """
    Lists all files in a directory.

    Args:
        directory: ABSOLUTE or relative directory path (default: ".")

    Returns:
        Formatted list of files
    """
    try:
        full_path = Path(directory)

        if not full_path.exists():
            return f"❌ Directory not found: {full_path}"

        files = []
        for item in full_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(full_path)
                files.append(str(rel_path))

        if not files:
            return f"No files found in {full_path}"

        formatted = f"Files in {full_path}:\n\n"
        for f in sorted(files):
            formatted += f"- {f}\n"

        return formatted

    except Exception as e:
        logger.error(f"Error listing files in {directory}: {e}")
        return f"❌ Error: {e}"

