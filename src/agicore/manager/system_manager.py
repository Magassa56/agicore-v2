"""SystemManager — Phase 9B compatibility alias.

SystemManager is a thin alias for AGIcoreManager kept for backwards
compatibility with any code that imported the name before the Phase 9B
consolidation.
"""
from __future__ import annotations

from agicore.manager.agicore_manager import AGIcoreManager as SystemManager

__all__ = ["SystemManager"]
