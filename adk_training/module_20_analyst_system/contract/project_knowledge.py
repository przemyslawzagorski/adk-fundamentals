"""
ProjectKnowledgeContract — Pydantic model for project-agnostic configuration.

Defines the "contract" between the project and the analyst agent system.
Any project can fill in this contract to get analyst support without code changes.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DocumentationType(str, Enum):
    """Supported documentation frameworks."""
    DIATAXIS = "diataxis"
    CUSTOM = "custom"


class DocumentLanguage(str, Enum):
    """Languages for generated documents."""
    POLISH = "pl"
    ENGLISH = "en"


class JiraConfig(BaseModel):
    """Jira integration settings."""
    project_key: str = Field(description="Jira project key, e.g. 'CLM6'")
    issue_types: list[str] = Field(
        default=["Epic", "Story", "Task"],
        description="Available issue types",
    )
    custom_fields: dict[str, str] = Field(
        default_factory=dict,
        description="Custom field mappings, e.g. {'acceptance_criteria': 'customfield_12345'}",
    )


class WikiConfig(BaseModel):
    """Confluence/Wiki integration settings."""
    space_key: str = Field(description="Wiki space key, e.g. 'TelcoBSSIoTConnect'")
    base_url: Optional[str] = Field(
        default=None,
        description="Wiki base URL override (uses env var if not set)",
    )


class DocumentationConfig(BaseModel):
    """Documentation conventions for the project."""
    framework: DocumentationType = Field(
        default=DocumentationType.DIATAXIS,
        description="Documentation framework used by the project",
    )
    primary_language: DocumentLanguage = Field(
        default=DocumentLanguage.POLISH,
        description="Primary language for generated documents",
    )
    docs_dir: str = Field(
        default="docs/",
        description="Path to documentation directory relative to project root",
    )
    style_notes: list[str] = Field(
        default_factory=list,
        description="Project-specific style conventions, e.g. ['Use active voice', 'No emoji']",
    )


class DomainContext(BaseModel):
    """Business domain context for the project."""
    domain: str = Field(description="Business domain, e.g. 'IoT Connectivity Management'")
    key_entities: list[str] = Field(
        default_factory=list,
        description="Core domain entities, e.g. ['SIM Card', 'Business Partner', 'Product Offering']",
    )
    glossary: dict[str, str] = Field(
        default_factory=dict,
        description="Term → definition mapping for domain-specific terms",
    )
    bounded_contexts: list[str] = Field(
        default_factory=list,
        description="DDD bounded contexts or module areas, e.g. ['Census', 'Catalog', 'Iungo']",
    )


class ProjectKnowledgeContract(BaseModel):
    """
    Root contract describing a project for the analyst agent system.

    This is the single configuration point that makes the system project-agnostic.
    Fill it once per project, and all orchestrators (analyze_requirement, create_epic,
    generate_document, etc.) adapt their behavior accordingly.
    """
    project_name: str = Field(description="Human-readable project name")
    project_description: str = Field(description="One-paragraph project summary")
    domain: DomainContext
    documentation: DocumentationConfig = Field(default_factory=DocumentationConfig)
    jira: Optional[JiraConfig] = Field(
        default=None,
        description="Jira config (None if Jira not used)",
    )
    wiki: Optional[WikiConfig] = Field(
        default=None,
        description="Wiki/Confluence config (None if not used)",
    )
    tech_stack: list[str] = Field(
        default_factory=list,
        description="Key technologies, e.g. ['Scala 2.13', 'Cats Effect 3', 'Angular 17']",
    )
    team_conventions: list[str] = Field(
        default_factory=list,
        description="Team-specific rules, e.g. ['Conventional Commits', 'PR required for all changes']",
    )
