"""
real_estate_app/main.py - Entry point for the Real Estate Property Management application.
This module primarily serves to launch the CLI.
Domain: Real Estate / Property Management
"""

from .cli import main as cli_main

# TODO: Explore GitHub.com integration for Copilot to suggest relevant CLI commands directly from this entry point.
# TODO: Use Copilot Agent Mode to refactor this to potentially launch a web interface instead of just the CLI, based on environment variables.

if __name__ == "__main__":
    cli_main()
