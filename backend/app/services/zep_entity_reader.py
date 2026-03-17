"""
Entity reader types - re-exports for backward compatibility.
Use LocalEntityReader for all operations (Zep Cloud removed).
"""

from typing import Optional

from .entity_models import EntityNode, FilteredEntities

__all__ = ['EntityNode', 'FilteredEntities', 'ZepEntityReader']


class ZepEntityReader:
    """Deprecated: Zep Cloud removed. Use LocalEntityReader."""

    def __init__(self, api_key: Optional[str] = None):
        raise NotImplementedError(
            "Zep Cloud has been removed. Use LocalEntityReader for local graph operations."
        )
