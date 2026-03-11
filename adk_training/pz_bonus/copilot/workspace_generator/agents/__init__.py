"""
🤖 Agents Package
Wszystkie agenty systemu wieloagentowego
"""

from .planning.documentation_research_agent import (
    create_documentation_research_agent,
    ResearchResult
)
from .planning.module_structure_planner import (
    create_module_structure_planner,
    ModuleStructure,
    FileSpec,
    FileType,
    DifficultyLevel
)
from .planning.planning_aggregator import (
    create_planning_aggregator,
    ExecutionPlan
)

from .execution.module_generator import (
    create_module_generator,
    CodeCritique
)

from .validation.coherence_validator import (
    create_coherence_validator,
    CoherenceValidationResult
)
from .validation.pedagogical_reviewer import (
    create_pedagogical_reviewer,
    PedagogicalReviewResult
)
from .validation.final_reporter import (
    create_final_reporter,
    FinalReport
)

__all__ = [
    # Planning
    "create_documentation_research_agent",
    "ResearchResult",
    "create_module_structure_planner",
    "ModuleStructure",
    "FileSpec",
    "FileType",
    "DifficultyLevel",
    "create_planning_aggregator",
    "ExecutionPlan",
    # Execution
    "create_module_generator",
    "CodeCritique",
    # Validation
    "create_coherence_validator",
    "CoherenceValidationResult",
    "create_pedagogical_reviewer",
    "PedagogicalReviewResult",
    "create_final_reporter",
    "FinalReport",
]

