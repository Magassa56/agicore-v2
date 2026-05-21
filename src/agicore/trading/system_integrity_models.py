"""Models for the offline Autonomous System Integrity Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .behavioral_stability_models import BehavioralStabilityResult
from .cognitive_adaptation_models import CognitiveAdaptationResult
from .executive_brain_models import ExecutiveBrainResult
from .hierarchical_supervisor_models import SupervisorResult
from .learning_governance_models import LearningGovernanceResult
from .multi_agent_models import AgentCoordinationResult
from .recursive_self_evaluation_models import SelfEvaluationResult
from .safe_rl_models import SafeRLExperimentResult
from .scenario_replay_models import ReplayArenaResult
from .strategic_memory_models import StrategicTimelineAnalysis
from .strategic_planning_models import StrategicPlanningResult


class SystemIntegrityStatus(StrEnum):
    """Global integrity status for the autonomous offline stack."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNSTABLE = "UNSTABLE"
    COMPROMISED = "COMPROMISED"
    PROTECTION_MODE = "PROTECTION_MODE"
    ROLLBACK_RECOMMENDED = "ROLLBACK_RECOMMENDED"


class SystemIntegrityRisk(StrEnum):
    """Integrity risks detected across decision and governance layers."""

    LOGIC_CONFLICT = "LOGIC_CONFLICT"
    LAYER_CONTRADICTION = "LAYER_CONTRADICTION"
    RISK_ACCUMULATION = "RISK_ACCUMULATION"
    MODULE_INSTABILITY = "MODULE_INSTABILITY"
    GOVERNANCE_FAILURE = "GOVERNANCE_FAILURE"
    AUTONOMY_UNSAFE = "AUTONOMY_UNSAFE"
    STRATEGIC_DRIFT = "STRATEGIC_DRIFT"
    BEHAVIORAL_DRIFT = "BEHAVIORAL_DRIFT"
    COGNITIVE_OVERLOAD = "COGNITIVE_OVERLOAD"
    SAFETY_LOCKDOWN_REQUIRED = "SAFETY_LOCKDOWN_REQUIRED"
    LOW_SYSTEM_CONFIDENCE = "LOW_SYSTEM_CONFIDENCE"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class ModuleHealthStatus(StrEnum):
    """Health bucket for one autonomous trading module."""

    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    UNSTABLE = "UNSTABLE"
    BLOCKED = "BLOCKED"
    ISOLATE = "ISOLATE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ModuleIntegrityReport:
    """Health report for one module participating in the decision stack."""

    module_name: str
    health_status: ModuleHealthStatus
    health_score: int
    risks: tuple[SystemIntegrityRisk, ...]
    notes: tuple[str, ...]
    isolate_recommended: bool = False


@dataclass(frozen=True)
class SystemIntegrityInput:
    """Inputs consumed by the offline system integrity engine."""

    self_evaluation: SelfEvaluationResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    cognitive_adaptation: CognitiveAdaptationResult | None = None
    behavioral_stability: BehavioralStabilityResult | None = None
    executive_result: ExecutiveBrainResult | None = None
    supervisor_result: SupervisorResult | None = None
    agent_coordination: AgentCoordinationResult | None = None
    strategic_timeline_analysis: StrategicTimelineAnalysis | None = None
    strategic_result: StrategicPlanningResult | None = None
    safe_rl_result: SafeRLExperimentResult | None = None
    replay_arena: ReplayArenaResult | None = None


@dataclass(frozen=True)
class SystemIntegrityEvent:
    """Auditable integrity event."""

    status: SystemIntegrityStatus
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class SystemIntegrityResult:
    """Final autonomous system integrity output."""

    status: SystemIntegrityStatus
    integrity_score: int
    risks: tuple[SystemIntegrityRisk, ...]
    module_reports: tuple[ModuleIntegrityReport, ...]
    modules_to_isolate: tuple[str, ...]
    recommended_action: str
    recommended_actions: tuple[str, ...]
    events: tuple[SystemIntegrityEvent, ...]
    summary: str


__all__ = [
    "ModuleHealthStatus",
    "ModuleIntegrityReport",
    "SystemIntegrityEvent",
    "SystemIntegrityInput",
    "SystemIntegrityResult",
    "SystemIntegrityRisk",
    "SystemIntegrityStatus",
]
