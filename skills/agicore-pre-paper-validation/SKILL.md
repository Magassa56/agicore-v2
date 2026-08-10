---
name: agicore-pre-paper-validation
description: Validate an AGIcore trading change or candidate before any supervised paper-trading proposal. Use for pre-paper readiness reviews, causal replay checks, temporal train-validation-OOS separation, walk-forward validation, execution-cost modelling, chronological stability, mandatory risk gating, reproducibility evidence, and evidence-based PASS, FAIL, or BLOCKED decisions.
---

# AGIcore pre-paper validation

Validate only the minimum scope needed to decide whether a trading candidate is ready to be proposed for supervised paper trading. This Skill does not authorize paper trading, network access, broker access, or an order.

## Start safely

1. Read `AGENTS.md` first; it remains authoritative.
2. Read `docs/trading.md` and the directly relevant implementation, tests, and documentation.
3. Run `git status --short` and `git diff --check` before any change.
4. Do not read or modify `data/` or `reports/`; use only explicitly supplied permitted fixtures or synthetic inputs.
5. Do not create a strategy, optimize parameters, change trading thresholds, add ML/AlphaEvolve, weaken tests, access secrets, activate network transport, connect a broker, or submit an order.

If requested work exceeds this scope or requires an external connection, stop and request human authorization.

## Validate in this order

Record a command, test name, artifact hash, or diff location for every conclusion. A declaration, boolean readiness flag, or review-only module is not proof of runtime enforcement.

1. **Test harness reliability.** Run the smallest relevant test subset, then integration tests when applicable. Treat collection, fixture, permission, cache, or temporary-directory errors as BLOCKED until reproducibly resolved; never skip, disable, or hide them.
2. **Causality.** Confirm decisions use only information available at that timestamp; verify execution happens no earlier than the allowed next event/bar. Add or run a prefix-invariance test: changing future input cannot alter prior decisions or trades.
3. **Temporal separation.** Require chronological, non-overlapping train, validation, and OOS partitions. Freeze the candidate and its parameters before OOS. Keep OOS out of parameter selection and report each range, count, and boundary.
4. **Walk-forward.** When a model, calibration, or parameter selection exists, require repeated chronological train/validation/OOS windows with no overlap. When none exists, state `NOT_APPLICABLE` and prove that no parameter search or fit occurred.
5. **Execution costs.** Require explicit, configurable commission, spread, slippage, and adverse scenarios. Attribute each component to trades and aggregate gross/net performance. A single unspecified round-trip cost does not satisfy this gate.
6. **Chronological stability.** Test consecutive completed windows, resets at boundaries, and invariance of completed windows to later data. Report dispersion and adverse-window results; do not select a winner from retrospective results.
7. **Mandatory risk gate.** Trace `signal -> risk check -> simulated order -> fill/state -> journal`. Prove fail-closed behavior and that a bypassed, rejected, or limit-breaching order cannot mutate simulated state. Verify stop loss, position/exposure, drawdown, daily-loss, and kill-switch rules relevant to the candidate.
8. **Reproducibility.** Require hashes for every permitted input, frozen configuration/parameters, code revision, deterministic manifest, and repeat-run equivalence. Preserve timestamps, ordering rules, outputs, and failures without exposing sensitive values.
9. **Paper readiness.** Confirm a local simulated runtime is connected to the validated path, human supervision and stop conditions are operational, journaling/observability work, and no network/broker/account/order route exists. Do not claim that a contract audit or synthetic adapter is a broker connection.
10. **Claims discipline.** Never conclude profitability, future performance, or readiness for live trading from historical, synthetic, or paper evidence. State the evidence limits explicitly.

## Decision standard

Return exactly one decision with measurable evidence:

- `PASS`: every applicable gate passes; tests are executable; evidence includes commands/results and reproducible artifacts. This means only “eligible to be proposed for supervised paper trading”, never authorized or profitable.
- `FAIL`: an implemented gate or test produces a functional failure, look-ahead, temporal leak, missing cost component, risk bypass, nondeterminism, or unsafe route. Name the failed gate and the observed evidence.
- `BLOCKED`: evidence cannot be obtained safely or reproducibly, including broken test infrastructure, missing permitted input, absent OOS design, or missing human authorization. Name the blocker and the minimal next action.

Do not use a score to override a failed or blocked gate. Do not convert missing evidence into PASS.

## Required final report

Use the report format required by `AGENTS.md`. In `Résultat`, begin with `DECISION: PASS`, `DECISION: FAIL`, or `DECISION: BLOCKED`, then list each gate in the validation order with `PASS`, `FAIL`, `BLOCKED`, or `NOT_APPLICABLE`, its evidence, and its limitation. Include the exact commands/tests run, input/config/code hashes when permitted, and the reason no profitability claim is made.

Before finishing, run `git diff --check`, `git diff --name-only`, and `git status --short`; report any out-of-scope change as BLOCKED.
