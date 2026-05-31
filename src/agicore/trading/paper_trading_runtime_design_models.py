"""Models for offline AGIcore paper trading runtime design."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PaperTradingRuntimeDesignState(StrEnum):
    NOT_READY = "NOT_READY"
    DESIGN_REVIEW_REQUIRED = "DESIGN_REVIEW_REQUIRED"
    PARTIALLY_DESIGNED = "PARTIALLY_DESIGNED"
    RUNTIME_DESIGN_READY = "RUNTIME_DESIGN_READY"
    READY_FOR_RUNTIME_IMPLEMENTATION = "READY_FOR_RUNTIME_IMPLEMENTATION"


class PaperTradingRuntimeDesignRisk(StrEnum):
    ARCHITECTURE_UNCLEAR = "ARCHITECTURE_UNCLEAR"
    STATE_MACHINE_INCOMPLETE = "STATE_MACHINE_INCOMPLETE"
    SESSION_CYCLE_AMBIGUOUS = "SESSION_CYCLE_AMBIGUOUS"
    INPUT_OUTPUT_CONTRACT_GAP = "INPUT_OUTPUT_CONTRACT_GAP"
    SAFETY_BOUNDARY_GAP = "SAFETY_BOUNDARY_GAP"
    OBSERVABILITY_HOOK_MISSING = "OBSERVABILITY_HOOK_MISSING"
    ROLLBACK_HOOK_MISSING = "ROLLBACK_HOOK_MISSING"
    KILL_SWITCH_HOOK_MISSING = "KILL_SWITCH_HOOK_MISSING"
    HUMAN_SUPERVISION_HOOK_MISSING = "HUMAN_SUPERVISION_HOOK_MISSING"
    ADAPTER_CONTRACT_INCOMPLETE = "ADAPTER_CONTRACT_INCOMPLETE"
    RUNTIME_SCOPE_DRIFT = "RUNTIME_SCOPE_DRIFT"
    PREMATURE_IMPLEMENTATION_RISK = "PREMATURE_IMPLEMENTATION_RISK"


class PaperTradingRuntimeDesignDecision(StrEnum):
    BLOCK_RUNTIME_IMPLEMENTATION = "BLOCK_RUNTIME_IMPLEMENTATION"
    REQUIRE_DESIGN_CLEANUP = "REQUIRE_DESIGN_CLEANUP"
    APPROVE_RUNTIME_DESIGN = "APPROVE_RUNTIME_DESIGN"
    APPROVE_RUNTIME_IMPLEMENTATION = "APPROVE_RUNTIME_IMPLEMENTATION"


class PaperTradingRuntimeDesignRecommendation(StrEnum):
    HOLD_RUNTIME_IMPLEMENTATION = "HOLD_RUNTIME_IMPLEMENTATION"
    CLARIFY_RUNTIME_ARCHITECTURE = "CLARIFY_RUNTIME_ARCHITECTURE"
    COMPLETE_RUNTIME_STATE_MACHINE = "COMPLETE_RUNTIME_STATE_MACHINE"
    CLARIFY_SESSION_CYCLE = "CLARIFY_SESSION_CYCLE"
    COMPLETE_INPUT_OUTPUT_CONTRACTS = "COMPLETE_INPUT_OUTPUT_CONTRACTS"
    COMPLETE_SAFETY_BOUNDARIES = "COMPLETE_SAFETY_BOUNDARIES"
    ADD_OBSERVABILITY_HOOKS = "ADD_OBSERVABILITY_HOOKS"
    ADD_ROLLBACK_HOOKS = "ADD_ROLLBACK_HOOKS"
    ADD_KILL_SWITCH_HOOKS = "ADD_KILL_SWITCH_HOOKS"
    ADD_HUMAN_SUPERVISION_HOOKS = "ADD_HUMAN_SUPERVISION_HOOKS"
    COMPLETE_ADAPTER_CONTRACTS = "COMPLETE_ADAPTER_CONTRACTS"
    FREEZE_RUNTIME_SCOPE = "FREEZE_RUNTIME_SCOPE"
    KEEP_IMPLEMENTATION_BLOCKED = "KEEP_IMPLEMENTATION_BLOCKED"
    RUN_RUNTIME_DESIGN_REVIEW_SUITE = "RUN_RUNTIME_DESIGN_REVIEW_SUITE"
    APPROVE_RUNTIME_DESIGN_AFTER_MANUAL_REVIEW = "APPROVE_RUNTIME_DESIGN_AFTER_MANUAL_REVIEW"
    APPROVE_IMPLEMENTATION_AFTER_MANUAL_REVIEW = "APPROVE_IMPLEMENTATION_AFTER_MANUAL_REVIEW"


@dataclass(frozen=True)
class PaperTradingRuntimeDesignInput:
    paper_runtime_decision_review: Any = None
    paper_runtime_pre_review: Any = None
    full_paper_session: Any = None
    simulated_market_session: Any = None
    mock_alpaca_session: Any = None
    mock_connectivity_layer: Any = None
    alpaca_paper_connectivity_readiness: Any = None
    broker_paper_sandbox: Any = None
    paper_trading_end_to_end: Any = None
    paper_dry_run: Any = None
    supervised_paper_trial: Any = None
    observability_verification: Any = None
    rollback_verification: Any = None
    kill_switch_verification: Any = None
    human_validated_paper_session: Any = None
    supervised_paper_session: Any = None
    architecture_components: tuple[str, ...] = ()
    runtime_states: tuple[str, ...] = ()
    session_cycle_steps: tuple[str, ...] = ()
    input_contracts: tuple[str, ...] = ()
    output_contracts: tuple[str, ...] = ()
    safety_boundaries: tuple[str, ...] = ()
    observability_hooks: tuple[str, ...] = ()
    rollback_hooks: tuple[str, ...] = ()
    kill_switch_hooks: tuple[str, ...] = ()
    human_supervision_hooks: tuple[str, ...] = ()
    adapter_contracts: tuple[str, ...] = ()
    runtime_entrypoint: str | None = None
    runtime_scope_locked: bool | None = None
    no_runtime_implementation_created: bool | None = None
    design_review_approved: bool | None = None
    ready_for_runtime_implementation: bool | None = None
    offline_mode_enforced: bool | None = None
    no_real_broker: bool | None = None
    no_api_key_read: bool | None = None
    no_http_transport: bool | None = None
    no_websocket_transport: bool | None = None
    no_socket_transport: bool | None = None
    no_external_api: bool | None = None
    no_real_order: bool | None = None
    architecture_score: int | None = None
    state_machine_score: int | None = None
    session_cycle_score: int | None = None
    inputs_outputs_score: int | None = None
    safety_boundaries_score: int | None = None
    observability_hooks_score: int | None = None
    rollback_hooks_score: int | None = None
    kill_switch_hooks_score: int | None = None
    human_supervision_hooks_score: int | None = None
    adapter_contracts_score: int | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperTradingRuntimeDesignSection:
    name: str
    score: int
    passed: bool
    risks: tuple[PaperTradingRuntimeDesignRisk, ...] = ()
    items: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperTradingRuntimeDesignScore:
    overall_score: int
    architecture_score: int
    state_machine_score: int
    session_cycle_score: int
    inputs_outputs_score: int
    safety_boundaries_score: int
    observability_hooks_score: int
    rollback_hooks_score: int
    kill_switch_hooks_score: int
    human_supervision_hooks_score: int
    adapter_contracts_score: int


@dataclass(frozen=True)
class PaperTradingRuntimeDesignResult:
    state: PaperTradingRuntimeDesignState
    decision: PaperTradingRuntimeDesignDecision
    runtime_design_score: int
    score_breakdown: PaperTradingRuntimeDesignScore
    risks: tuple[PaperTradingRuntimeDesignRisk, ...] = ()
    architecture: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("architecture", 0, False)
    )
    state_machine: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("state_machine", 0, False)
    )
    session_cycle: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("session_cycle", 0, False)
    )
    inputs_outputs: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("inputs_outputs", 0, False)
    )
    safety_boundaries: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("safety_boundaries", 0, False)
    )
    observability_hooks: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("observability_hooks", 0, False)
    )
    rollback_hooks: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("rollback_hooks", 0, False)
    )
    kill_switch_hooks: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("kill_switch_hooks", 0, False)
    )
    human_supervision_hooks: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("human_supervision_hooks", 0, False)
    )
    adapter_contracts: PaperTradingRuntimeDesignSection = field(
        default_factory=lambda: PaperTradingRuntimeDesignSection("adapter_contracts", 0, False)
    )
    recommendations: tuple[PaperTradingRuntimeDesignRecommendation, ...] = ()
    offline_only: bool = True
    summary: str = ""
