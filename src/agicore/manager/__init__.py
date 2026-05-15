"""AGIcore-v2 — manager package (Phase 9B)."""
from .agicore_manager import AGIcoreManager
from .manager_models import ManagerConfig, ManagerState
from .system_manager import SystemManager

__all__ = ["AGIcoreManager", "ManagerConfig", "ManagerState", "SystemManager"]

