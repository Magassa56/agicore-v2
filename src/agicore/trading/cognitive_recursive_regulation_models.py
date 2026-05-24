"""Models for offline cognitive recursive regulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from agicore.trading.cognitive_alignment_models import CognitiveAlignmentResult
from agicore.trading.cognitive_coherence_models import CognitiveCoherenceResult
from agicore.trading.cognitive_consensus_models import CognitiveConsensusResult
from agicore.trading.cognitive_executive_control_models import CognitiveExecutiveControlResult
from agicore.trading.cognitive_memory_consolidation_models import CognitiveMemoryConsolidationResult
from agicore.trading.cognitive_meta_supervision_models import CognitiveMetaSupervisionResult
from agicore.trading.cognitive_safety_orchestrator_models import CognitiveSafetyOrchestratorResult
from agicore.trading.intent_integrity_models import IntentIntegrityResult
from agicore.trading.recursive_world_model_models import RecursiveWorldModelResult
from agicore.trading.self_reflection_audit_models import SelfReflectionAuditResult


class RecursiveRegulationState(str, Enum):
    RECURSION_STABLE = "RECURSION_STABLE"
    RECURSION_MONITORING = "RECURSION_MONITORING"
    RECURSION_THROTTLED = "RECURSION_THROTTLED"
    RECURSION_DEGRADED = "RECURSION_DEGRADED"
    RECURSION_CRITICAL = "RECURSION_CRITICAL"
    RECURSION_LOCKED = "RECURSION_LOCKED"
    RECURSION_RECOVERING = "RECURSION_RECOVERING"


class RecursiveRegulationMode(str, Enum):
    NORMAL_RECURSIVE_REGULATION = "NORMAL_RECURSIVE_REGULATION"
    RECURSIVE_MONITORING = "RECURSIVE_MONITORING"
    RECURSIVE_THROTTLING = "RECURSIVE_THROTTLING"
    FEEDBACK_LOOP_CONTROL = "FEEDBACK_LOOP_CONTROL"
    PROPAGATION_CONTROL = "PROPAGATION_CONTROL"
    RECURSIVE_STABILIZATION = "RECURSIVE_STABILIZATION"
    RECURSIVE_SAFE_MODE = "RECURSIVE_SAFE_MODE"
    RECURSIVE_LOCKDOWN = "RECURSIVE_LOCKDOWN"


class RecursiveRegulationRisk(str, Enum):
    RUNAWAY_RECURSION = "RUNAWAY_RECURSION"
    RECURSIVE_FEEDBACK_LOOP = "RECURSIVE_FEEDBACK_LOOP"
    COGNITIVE_SIGNAL_AMPLIFICATION = "COGNITIVE_SIGNAL_AMPLIFICATION"
    WORLD_MODEL_RECURSIVE_DRIFT = "WORLD_MODEL_RECURSIVE_DRIFT"
    SELF_REFERENCE_COLLAPSE = "SELF_REFERENCE_COLLAPSE"
    META_LOOP_INSTABILITY = "META_LOOP_INSTABILITY"
    CROSS_ENGINE_RECURSIVE_PROPAGATION = "CROSS_ENGINE_RECURSIVE_PROPAGATION"
    EXECUTIVE_RECURSION_LOCK = "EXECUTIVE_RECURSION_LOCK"
    RECURSIVE_CONSENSUS_CASCADE = "RECURSIVE_CONSENSUS_CASCADE"
    UNBOUNDED_REASONING_EXPANSION = "UNBOUNDED_REASONING_EXPANSION"


class RecursiveRegulationDirective(str, Enum):
    CONTINUE_RECURSIVE_MONITORING = "CONTINUE_RECURSIVE_MONITORING"
    LIMIT_RECURSIVE_DEPTH = "LIMIT_RECURSIVE_DEPTH"
    THROTTLE_RECURSIVE_SIGNALS = "THROTTLE_RECURSIVE_SIGNALS"
    BREAK_FEEDBACK_LOOP = "BREAK_FEEDBACK_LOOP"
    STABILIZE_WORLD_MODEL_RECURSION = "STABILIZE_WORLD_MODEL_RECURSION"
    PROTECT_SELF_REFERENCE = "PROTECT_SELF_REFERENCE"
    CONTAIN_CROSS_ENGINE_PROPAGATION = "CONTAIN_CROSS_ENGINE_PROPAGATION"
    PROTECT_EXECUTIVE_CONTROL = "PROTECT_EXECUTIVE_CONTROL"
    PROTECT_RECURSIVE_CONSENSUS = "PROTECT_RECURSIVE_CONSENSUS"
    LOCK_RECURSIVE_EXPANSION = "LOCK_RECURSIVE_EXPANSION"


class RecursiveRegulationRecommendation(str, Enum):
    MAINTAIN_RECURSIVE_OBSERVATION = "MAINTAIN_RECURSIVE_OBSERVATION"
    REDUCE_RECURSIVE_DEPTH = "REDUCE_RECURSIVE_DEPTH"
    SLOW_REASONING_EXPANSION = "SLOW_REASONING_EXPANSION"
    REBUILD_RECURSIVE_CHAIN = "REBUILD_RECURSIVE_CHAIN"
    REALIGN_WORLD_MODEL_RECURSION = "REALIGN_WORLD_MODEL_RECURSION"
    STABILIZE_SELF_REFERENCE = "STABILIZE_SELF_REFERENCE"
    ISOLATE_RECURSIVE_ENGINE = "ISOLATE_RECURSIVE_ENGINE"
    RECHECK_EXECUTIVE_RECURSION = "RECHECK_EXECUTIVE_RECURSION"
    REBUILD_RECURSIVE_CONSENSUS = "REBUILD_RECURSIVE_CONSENSUS"
    REQUIRE_MANUAL_RECURSION_REVIEW = "REQUIRE_MANUAL_RECURSION_REVIEW"


@dataclass(frozen=True)
class RecursiveRegulationEvent:
    name: str
    detail: str
    severity: str = "INFO"


@dataclass(frozen=True)
class RecursiveRegulationScore:
    recursion_depth_score: int = 80
    feedback_loop_score: int = 80
    amplification_score: int = 80
    world_model_recursion_score: int = 80
    self_reference_score: int = 80
    meta_loop_score: int = 80
    propagation_score: int = 80
    executive_recursion_score: int = 80
    consensus_recursion_score: int = 80
    reasoning_expansion_score: int = 80
    overall_score: int = 80


@dataclass(frozen=True)
class RecursiveChainNode:
    name: str
    recursion_depth: int
    score: int
    throttled: bool = False
    risk: str = ""


@dataclass(frozen=True)
class RecursiveRegulationGraph:
    nodes: tuple[RecursiveChainNode, ...] = ()
    edges: tuple[tuple[str, str, str], ...] = ()
    feedback_loops: tuple[tuple[str, str], ...] = ()
    propagation_paths: tuple[tuple[str, str, str], ...] = ()
    throttled_nodes: tuple[str, ...] = ()
    locked_nodes: tuple[str, ...] = ()
    max_depth: int = 3


@dataclass(frozen=True)
class RecursiveStabilizationPlan:
    max_allowed_depth: int = 3
    throttle_active: bool = False
    propagation_contained: bool = False
    consensus_protected: bool = False
    executive_protected: bool = False
    world_model_stabilized: bool = False
    steps: tuple[str, ...] = ()
    directives: tuple[RecursiveRegulationDirective, ...] = ()


@dataclass(frozen=True)
class CognitiveRecursiveRegulationInput:
    cognitive_meta_supervision: Optional[CognitiveMetaSupervisionResult] = None
    cognitive_safety_orchestrator: Optional[CognitiveSafetyOrchestratorResult] = None
    cognitive_consensus: Optional[CognitiveConsensusResult] = None
    cognitive_coherence: Optional[CognitiveCoherenceResult] = None
    cognitive_alignment: Optional[CognitiveAlignmentResult] = None
    cognitive_executive_control: Optional[CognitiveExecutiveControlResult] = None
    recursive_world_model: Optional[RecursiveWorldModelResult] = None
    intent_integrity: Optional[IntentIntegrityResult] = None
    cognitive_memory_consolidation: Optional[CognitiveMemoryConsolidationResult] = None
    self_reflection_audit: Optional[SelfReflectionAuditResult] = None
    requested_recursive_depth: int = 2
    max_allowed_depth: int = 3
    recursive_cycle_count: int = 1
    signal_amplification_factor: float = 1.0


@dataclass(frozen=True)
class CognitiveRecursiveRegulationResult:
    state: RecursiveRegulationState
    mode: RecursiveRegulationMode
    recursive_regulation_score: int
    score_breakdown: RecursiveRegulationScore
    graph: RecursiveRegulationGraph = field(default_factory=RecursiveRegulationGraph)
    stabilization_plan: RecursiveStabilizationPlan = field(default_factory=RecursiveStabilizationPlan)
    risks: tuple[RecursiveRegulationRisk, ...] = ()
    directives: tuple[RecursiveRegulationDirective, ...] = ()
    recommendations: tuple[RecursiveRegulationRecommendation, ...] = ()
    events: tuple[RecursiveRegulationEvent, ...] = ()
    summary: str = ""
