"""The component registry + demo concept catalog — the catalog the Composer selects from
(ADR-009 / D-02 / D-13).

The backend holds only metadata (pattern id, prop schema, which topics/strategies each pattern
serves; plus the 12 locked demo concepts). The React implementations live in
`frontend/components/library/`.
"""

from app.components.registry import (
    CONCEPTS,
    REGISTRY,
    ComponentPattern,
    Concept,
    concepts_for_subject,
    find_pattern_for,
    get_concept,
    get_pattern,
)

__all__ = [
    "CONCEPTS",
    "REGISTRY",
    "ComponentPattern",
    "Concept",
    "concepts_for_subject",
    "find_pattern_for",
    "get_concept",
    "get_pattern",
]
