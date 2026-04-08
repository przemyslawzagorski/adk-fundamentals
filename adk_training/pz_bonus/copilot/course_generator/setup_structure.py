#!/usr/bin/env python3
"""
Script to create directory structure for course_generator
"""

from pathlib import Path

# Base directory
base_dir = Path(__file__).parent

# Directories to create
directories = [
    "agents/ingestion",
    "agents/evaluation",
    "agents/planning",
    "agents/repository",
    "agents/content",
    "tools",
    "config",
    "output",
    "prompts/ingestion",
    "prompts/evaluation",
    "prompts/planning",
    "prompts/repository",
    "prompts/content",
]

# Create directories
for dir_path in directories:
    full_path = base_dir / dir_path
    full_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created: {dir_path}")

# Create __init__.py files
init_files = [
    "agents/__init__.py",
    "agents/ingestion/__init__.py",
    "agents/evaluation/__init__.py",
    "agents/planning/__init__.py",
    "agents/repository/__init__.py",
    "agents/content/__init__.py",
    "tools/__init__.py",
]

for init_file in init_files:
    full_path = base_dir / init_file
    full_path.touch()
    print(f"✅ Created: {init_file}")

print("\n🎉 Directory structure created successfully!")

