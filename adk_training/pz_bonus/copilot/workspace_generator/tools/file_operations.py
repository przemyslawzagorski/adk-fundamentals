"""
📁 File Operations Tool
Narzędzie do operacji na plikach (tworzenie, zapis, odczyt)
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def create_file(file_path: str, content: str, base_dir: str = "./output") -> str:
    """
    Creates a file with the given content.
    
    Args:
        file_path: Relative path to the file (e.g., "module1/src/Main.java")
        content: File content
        base_dir: Base directory for output (default: "./output")
    
    Returns:
        Success message with full path
    """
    try:
        full_path = Path(base_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        full_path.write_text(content, encoding='utf-8')
        
        logger.info(f"Created file: {full_path}")
        return f"✅ Created: {full_path}"
        
    except Exception as e:
        logger.error(f"Error creating file {file_path}: {e}")
        return f"❌ Error: {e}"


def read_file(file_path: str, base_dir: str = "./output") -> str:
    """
    Reads content from a file.
    
    Args:
        file_path: Relative path to the file
        base_dir: Base directory (default: "./output")
    
    Returns:
        File content or error message
    """
    try:
        full_path = Path(base_dir) / file_path
        
        if not full_path.exists():
            return f"❌ File not found: {full_path}"
        
        content = full_path.read_text(encoding='utf-8')
        return content
        
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"❌ Error: {e}"


def list_files(directory: str = ".", base_dir: str = "./output") -> str:
    """
    Lists all files in a directory.
    
    Args:
        directory: Relative directory path (default: ".")
        base_dir: Base directory (default: "./output")
    
    Returns:
        Formatted list of files
    """
    try:
        full_path = Path(base_dir) / directory
        
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


def create_directory(directory: str, base_dir: str = "./output") -> str:
    """
    Creates a directory.
    
    Args:
        directory: Relative directory path
        base_dir: Base directory (default: "./output")
    
    Returns:
        Success message
    """
    try:
        full_path = Path(base_dir) / directory
        full_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created directory: {full_path}")
        return f"✅ Created directory: {full_path}"
        
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return f"❌ Error: {e}"

