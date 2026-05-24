"""Models for the offline Autonomous Cognitive Policy Engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .cognitive_governance_models import CognitiveGovernanceResult
from .collective_consensus_models import ConsensusResult
from .global_orchestrator_models import GlobalOrchestratorResult
from .intent_alignment_models import IntentAlignmentResult
from .learning_governance_models import LearningGovernanceResult
from .operational_awareness_models import OperationalAwarenessResult
from .recursive_world_model_models import RecursiveWorldModelResult
from .self_reflection_audit_models import SelfReflectionAuditResult
from .strategic_arbitration_models import ArbitrationResult
from .system_integrity_models import SystemIntegrityResult


class CognitivePolicyMode(StrEnum):
    """Operating mode selected by the cognitive policy layer."""

    POLICY_NORMAL = "POLICY_NORMAL"
    POLICY_RESTRICTED = "POLICY_RESTRICTED"
    POLICY_SAFE_MODE = "POLICY_SAFE_MODE"
    POLICY_AUDIT_REQUIRED = "POLICY_AUDIT_REQUIRED"
    POLICY_LEARNING_FROZEN = "POLICY_LEARNING_FROZEN"
    POLICY_WORLD_MODEL_PROTECTED = "POLICY_WORLD_MODEL_PROTECTED"
    POLICY_LOCKED = "POLICY_LOCKED"


class CognitivePolicyScope(StrEnum):
    """Scope controlled by one cognitive policy rule."""

    ANALYSIS = "ANALYSIS"
    PLANNING = "PLANNING"
    FORECASTING = "FORECASTING"
    STRATEGY_EVOLUTION = "STRATEGY_EVOLUTION"
    RECURSIVE_WORLD_MODEL = "RECURSIVE_WORLD_MODEL"
    SELF_REFLECTION = "SELF_REFLECTION"
    LEARNING = "LEARNING"
    EXECUTION_ROUTING = "EXECUTION_ROUTING"
    AUTONOMY_EXPANSION = "AUTONOMY_EXPANSION"
    SAFETY_CRITICAL = "SAFETY_CRITICAL"


class CognitivePolicyDecision(StrEnum):
    """Decision applied to a policy scope."""

    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTIONS = "ALLOW_WITH_RESTRICTIONS"
    DENY = "DENY"
    REQUIRE_AUDIT = "REQUIRE_AUDIT"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    FREEZE = "FREEZE"
    LOCKDOWN = "LOCKDOWN"


class CognitivePolicyAction(StrEnum):
    """Action enforced by the cognitive policy layer."""

    ENFORCE_RESTRICTION = "ENFORCE_RESTRICTION"
    DENY_HIGH_RISK_ACTION = "DENY_HIGH_RISK_ACTION"
    REQUIRE_TRACEABILITY = "REQUIRE_TRACEABILITY"
    FREEZE_LEARNING = "FREEZE_LEARNING"
    PROTECT_WORLD_MODEL = "PROTECT_WORLD_MODEL"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    ENTER_SAFE_MODE = "ENTER_SAFE_MODE"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"


class CognitivePolicyRisk(StrEnum):
    """Risks detected while translating governance into policy."""

    POLICY_CONFLICT = "POLICY_CONFLICT"
    UNSAFE_PERMISSION = "UNSAFE_PERMISSION"
    MISSING_AUDIT_TRACE = "MISSING_AUDIT_TRACE"
    AUTONOMY_POLICY_DRIFT = "AUTONOMY_POLICY_DRIFT"
    WORLD_MODEL_UNPROTECTED = "WORLD_MODEL_UNPROTECTED"
    LEARNING_POLICY_VIOLATION = "LEARNING_POLICY_VIOLATION"
    STRATEGY_EVOLUTION_UNSAFE = "STRATEGY_EVOLUTION_UNSAFE"
    EXECUTION_ROUTING_UNSAFE = "EXECUTION_ROUTING_UNSAFE"
    SAFETY_CRITICAL_BYPASS = "SAFETY_CRITICAL_BYPASS"
    GOVERNANCE_POLICY_MISMATCH = "GOVERNANCE_POLICY_MISMATCH"


@dataclass(frozen=True)
class CognitivePolicyRule:
    """One explainable policy rule for a controlled cognitive scope."""

    rule_id: str
    scope: CognitivePolicyScope
    decision: CognitivePolicyDecision
    actions: tuple[CognitivePolicyAction, ...]
    restrictions: tuple[str, ...]
    reason: str
    priority: int = 50


@dataclass(frozen=True)
class CognitivePolicyViolation:
    """One detected policy violation."""

    scope: CognitivePolicyScope
    risk: CognitivePolicyRisk
    severity_score: int
    message: str


@dataclass(frozen=True)
class CognitivePolicyScore:
    """Policy score components normalized to 0..100."""

    governance_alignment_score: int
    audit_trace_score: int
    world_model_protection_score: int
    learning_control_score: int
    execution_safety_score: int
    autonomy_control_score: int
    policy_consistency_score: int


@dataclass(frozen=True)
class CognitivePolicySet:
    """Policy set generated from cognitive governance and safety evidence."""

    mode: CognitivePolicyMode
    rules: tuple[CognitivePolicyRule, ...]
    allowed_scopes: tuple[CognitivePolicyScope, ...]
    restricted_scopes: tuple[CognitivePolicyScope, ...]
    denied_scopes: tuple[CognitivePolicyScope, ...]
    frozen_scopes: tuple[CognitivePolicyScope, ...]
    audit_required_scopes: tuple[CognitivePolicyScope, ...]


@dataclass(frozen=True)
class CognitivePolicyInput:
    """Inputs consumed by the offline cognitive policy engine."""

    cognitive_governance: CognitiveGovernanceResult | None = None
    self_reflection_audit: SelfReflectionAuditResult | None = None
    recursive_world_model: RecursiveWorldModelResult | None = None
    global_orchestrator: GlobalOrchestratorResult | None = None
    strategic_arbitration: ArbitrationResult | None = None
    collective_consensus: ConsensusResult | None = None
    intent_alignment: IntentAlignmentResult | None = None
    learning_governance: LearningGovernanceResult | None = None
    system_integrity: SystemIntegrityResult | None = None
    operational_awareness: OperationalAwarenessResult | None = None


@dataclass(frozen=True)
class CognitivePolicyEvent:
    """Auditable cognitive policy event."""

    mode: CognitivePolicyMode
    message: str
    timestamp: datetime


@dataclass(frozen=True)
class CognitivePolicyResult:
    """Final autonomous cognitive policy result."""

    mode: CognitivePolicyMode
    policy_set: CognitivePolicySet
    decisions: tuple[CognitivePolicyDecision, ...]
    violations: tuple[CognitivePolicyViolation, ...]
    risks: tuple[CognitivePolicyRisk, ...]
    enforced_actions: tuple[CognitivePolicyAction, ...]
    cognitive_policy_score: int
    score_breakdown: CognitivePolicyScore
    recommendations: tuple[str, ...]
    events: tuple[CognitivePolicyEvent, ...]
    summary: str


__all__ = [
    "CognitivePolicyAction",
    "CognitivePolicyDecision",
    "CognitivePolicyEvent",
    "CognitivePolicyInput",
    "CognitivePolicyMode",
    "CognitivePolicyResult",
    "CognitivePolicyRisk",
    "CognitivePolicyRule",
    "CognitivePolicyScope",
    "CognitivePolicyScore",
    "CognitivePolicySet",
    "CognitivePolicyViolation",
]
