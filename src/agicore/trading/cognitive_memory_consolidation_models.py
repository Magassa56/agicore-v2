"""Models for offline cognitive memory consolidation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agicore.trading.cognitive_alignment_models import CognitiveAlignmentResult
from agicore.trading.cognitive_coherence_models import CognitiveCoherenceResult
from agicore.trading.cognitive_consensus_models import CognitiveConsensusResult
from agicore.trading.cognitive_continuity_models import CognitiveContinuityResult
from agicore.trading.cognitive_identity_models import CognitiveIdentityResult
from agicore.trading.cognitive_recovery_models import CognitiveRecoveryResult
from agicore.trading.cognitive_resilience_models import CognitiveResilienceResult
from agicore.trading.cognitive_stability_models import CognitiveStabilityResult
from agicore.trading.intent_integrity_models import IntentIntegrityResult
from agicore.trading.recursive_world_model_models import RecursiveWorldModelResult
from agicore.trading.self_reflection_audit_models import SelfReflectionAuditResult
from agicore.trading.session_replay_models import SessionReplayResult
from agicore.trading.strategic_memory_models import StrategicTimelineAnalysis
from agicore.trading.strategy_dna_models import StrategyDNA
from agicore.trading.trade_journal_models import JournalAnalysisResult


class MemoryConsolidationState(str, Enum):
    MEMORY_CONSOLIDATED = "MEMORY_CONSOLIDATED"
    MEMORY_WATCH = "MEMORY_WATCH"
    MEMORY_FRAGMENTED = "MEMORY_FRAGMENTED"
    MEMORY_CONFLICTED = "MEMORY_CONFLICTED"
    MEMORY_DEGRADED = "MEMORY_DEGRADED"
    MEMORY_AT_RISK = "MEMORY_AT_RISK"
    MEMORY_REPAIRING = "MEMORY_REPAIRING"
    MEMORY_LOCKED = "MEMORY_LOCKED"


class MemoryConsolidationMode(str, Enum):
    NORMAL_CONSOLIDATION = "NORMAL_CONSOLIDATION"
    TRACE_MERGING = "TRACE_MERGING"
    STRATEGIC_MEMORY_COMPRESSION = "STRATEGIC_MEMORY_COMPRESSION"
    INVARIANT_STABILIZATION = "INVARIANT_STABILIZATION"
    CONTRADICTION_CLEANUP = "CONTRADICTION_CLEANUP"
    LONG_TERM_MEMORY_SYNC = "LONG_TERM_MEMORY_SYNC"
    SAFE_MEMORY_MODE = "SAFE_MEMORY_MODE"
    LOCKED_MEMORY_MODE = "LOCKED_MEMORY_MODE"


class MemoryConsolidationRisk(str, Enum):
    MEMORY_FRAGMENTATION = "MEMORY_FRAGMENTATION"
    CONTRADICTORY_MEMORY_TRACE = "CONTRADICTORY_MEMORY_TRACE"
    REASONING_TRACE_LOSS = "REASONING_TRACE_LOSS"
    STRATEGIC_EXPERIENCE_LOSS = "STRATEGIC_EXPERIENCE_LOSS"
    INVARIANT_MEMORY_DRIFT = "INVARIANT_MEMORY_DRIFT"
    CONSOLIDATION_OVERWRITE_RISK = "CONSOLIDATION_OVERWRITE_RISK"
    LOW_MEMORY_CONFIDENCE = "LOW_MEMORY_CONFIDENCE"
    IDENTITY_MEMORY_MISMATCH = "IDENTITY_MEMORY_MISMATCH"
    CONTINUITY_MEMORY_BREAK = "CONTINUITY_MEMORY_BREAK"
    MEMORY_CORRUPTION_RISK = "MEMORY_CORRUPTION_RISK"


class MemoryConsolidationAction(str, Enum):
    PRESERVE_MEMORY_STATE = "PRESERVE_MEMORY_STATE"
    MERGE_REASONING_TRACES = "MERGE_REASONING_TRACES"
    COMPRESS_STRATEGIC_EXPERIENCE = "COMPRESS_STRATEGIC_EXPERIENCE"
    STABILIZE_INVARIANT_MEMORY = "STABILIZE_INVARIANT_MEMORY"
    CLEAN_CONTRADICTIONS = "CLEAN_CONTRADICTIONS"
    SYNC_LONG_TERM_MEMORY = "SYNC_LONG_TERM_MEMORY"
    PROTECT_MEMORY_SNAPSHOT = "PROTECT_MEMORY_SNAPSHOT"
    REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    LOCK_MEMORY_STATE = "LOCK_MEMORY_STATE"


class MemoryConsolidationRecommendation(str, Enum):
    CONTINUE_MEMORY_MONITORING = "CONTINUE_MEMORY_MONITORING"
    EXTEND_MEMORY_CHECKPOINTS = "EXTEND_MEMORY_CHECKPOINTS"
    MERGE_SAFE_TRACES_ONLY = "MERGE_SAFE_TRACES_ONLY"
    PRESERVE_STRATEGIC_SNAPSHOTS = "PRESERVE_STRATEGIC_SNAPSHOTS"
    RECHECK_IDENTITY_MEMORY = "RECHECK_IDENTITY_MEMORY"
    REPAIR_CONFLICTED_TRACES = "REPAIR_CONFLICTED_TRACES"
    AVOID_OVERWRITE = "AVOID_OVERWRITE"
    KEEP_AUTONOMY_REDUCED = "KEEP_AUTONOMY_REDUCED"
    REQUIRE_SUPERVISION = "REQUIRE_SUPERVISION"
    UPDATE_CONSOLIDATED_MEMORY = "UPDATE_CONSOLIDATED_MEMORY"


@dataclass(frozen=True)
class MemoryConsolidationEvent:
    name: str
    detail: str
    severity: str = "INFO"


@dataclass(frozen=True)
class MemoryConsolidationScore:
    trace_integrity_score: int = 80
    strategic_experience_score: int = 80
    invariant_stability_score: int = 80
    contradiction_cleanup_score: int = 80
    continuity_score: int = 80
    identity_memory_score: int = 80
    long_term_sync_score: int = 80
    snapshot_protection_score: int = 80
    overall_memory_score: int = 80


@dataclass(frozen=True)
class MemoryTrace:
    trace_id: str
    source: str
    content: str
    confidence_score: int = 80
    critical: bool = False
    contradicted: bool = False
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class MemoryCluster:
    name: str
    traces: tuple[MemoryTrace, ...] = ()
    consolidated_summary: str = ""
    confidence_score: int = 80
    conflict_count: int = 0
    protected: bool = False


@dataclass(frozen=True)
class ConsolidatedMemorySnapshot:
    summary: str
    clusters: tuple[MemoryCluster, ...] = ()
    preserved_invariants: tuple[str, ...] = ()
    critical_trace_ids: tuple[str, ...] = ()
    contradictions_cleaned: int = 0
    memory_confidence_score: int = 80
    protected: bool = False
    locked: bool = False


@dataclass(frozen=True)
class CognitiveMemoryConsolidationInput:
    cognitive_consensus: Optional[CognitiveConsensusResult] = None
    cognitive_coherence: Optional[CognitiveCoherenceResult] = None
    cognitive_alignment: Optional[CognitiveAlignmentResult] = None
    intent_integrity: Optional[IntentIntegrityResult] = None
    cognitive_identity: Optional[CognitiveIdentityResult] = None
    cognitive_continuity: Optional[CognitiveContinuityResult] = None
    cognitive_recovery: Optional[CognitiveRecoveryResult] = None
    cognitive_resilience: Optional[CognitiveResilienceResult] = None
    cognitive_stability: Optional[CognitiveStabilityResult] = None
    self_reflection_audit: Optional[SelfReflectionAuditResult] = None
    recursive_world_model: Optional[RecursiveWorldModelResult] = None
    strategic_timeline_analysis: Optional[StrategicTimelineAnalysis] = None
    session_replay: Optional[SessionReplayResult] = None
    trade_journal_result: Optional[JournalAnalysisResult] = None
    strategy_dna: Optional[StrategyDNA] = None
    manual_traces: tuple[MemoryTrace, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CognitiveMemoryConsolidationResult:
    state: MemoryConsolidationState
    mode: MemoryConsolidationMode
    memory_consolidation_score: int
    score_breakdown: MemoryConsolidationScore
    traces: tuple[MemoryTrace, ...] = ()
    clusters: tuple[MemoryCluster, ...] = ()
    snapshot: ConsolidatedMemorySnapshot = field(default_factory=lambda: ConsolidatedMemorySnapshot(summary=""))
    risks: tuple[MemoryConsolidationRisk, ...] = ()
    actions: tuple[MemoryConsolidationAction, ...] = ()
    recommendations: tuple[MemoryConsolidationRecommendation, ...] = ()
    events: tuple[MemoryConsolidationEvent, ...] = ()
    summary: str = ""
