"""Distinct recovery reducer with exact indicator injection and append-only history.

Frozen record constructors, Open execution, stops, risk, costs and raw predicates
are reused unchanged. The three prefix-consuming Close paths have explicit exact
incremental equivalents. A bounded live book never rescans archived decisions;
the append-only version ledger reconstructs every original native history.
"""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

from . import ema_pullback_regime_gated_baseline_v2 as ref
from .ema_pullback_v2_recovery_indicators import ExactIncrementalIndicatorsV1


def _pullback(context, k, bars, indicators):
    p, c = ref.pullback, ref.context
    bar = bars[k]
    def result(status, qualified=False, reference=None):
        return p.EMA20PullbackEvaluationV2(
            status, qualified, k, bar.timestamp_utc, context.source_event_types,
            context.source_event_direction, context.source_event_bar_index,
            context.source_event_timestamp, reference,
        )
    if context.state is not c.RegimeContextLifetimeState.ACTIVE:
        return result(p.EMA20PullbackStatusV2.INELIGIBLE_CONTEXT)
    if k < p.EMA_PERIOD:
        return result(p.EMA20PullbackStatusV2.INSUFFICIENT_EMA_WARMUP)
    ema = indicators.ema20(previous=True, before_timestamp=bar.timestamp_utc)
    if ema.status is not p.EMA20StatusV2.EVALUATED:
        return result(p.EMA20PullbackStatusV2(ema.status.value))
    line = ema.ema20
    close = p._exact_price(bar.close)
    if close is None:
        return result(p.EMA20PullbackStatusV2.INVALID_EMA_INPUT, reference=line)
    o, h, l = (p._exact_price(value) for value in (bar.open, bar.high, bar.low))
    if o is None or h is None or l is None or h < max(o, close) or l > min(o, close) or h < l:
        return result(p.EMA20PullbackStatusV2.INVALID_OHLC, reference=line)
    qualified = (
        ema.last_close > line and o >= line and l <= line and close > line
        if context.source_event_direction is c.RegimeDirection.LONG
        else ema.last_close < line and o <= line and h >= line and close < line
    )
    return result(p.EMA20PullbackStatusV2.EVALUATED, qualified, line)


def _advance_position(previous, index, timestamp, bars, indicators, impulse=None, reversal=None):
    p, c = ref.position, ref.context
    # These reference paths have no eligible indicator consumer.
    if previous.active_position is not None:
        return p.advance_open_position_signal_policy_v2(
            previous=previous, closed_bar_index=index, closed_bar_timestamp=timestamp,
            source_bar_closed=True, bars_by_index=bars,
            directional_impulse_event=impulse, reversal_transition_event=reversal,
        )
    p._require_book(previous)
    p._require_clock(index, timestamp)
    pullback = None
    def predicate(context, k, stamp):
        nonlocal pullback
        if bars[k].timestamp_utc != stamp:
            raise ref.pullback.EMA20PullbackV2Error(
                "candidate timestamp must match the lifetime closed bar")
        pullback = _pullback(context, k, bars, indicators)
        return pullback.pullback_qualified
    lifetime = c.advance_regime_context_v2(
        previous=previous.lifetime, closed_bar_index=index, closed_bar_timestamp=timestamp,
        source_bar_closed=True, directional_impulse_event=impulse,
        reversal_transition_event=reversal, ema20_pullback_qualified=predicate,
    )
    if pullback is not None and pullback.pullback_qualified:
        lifetime = replace(lifetime, context=replace(
            lifetime.context, ema_reference=pullback.ema_reference))
    composition = lifetime.composition
    status = {
        c.RegimeContextStatus.UNQUALIFIED: p.PositionSignalAdmissionStatusV2.NO_REGIME_EVENT,
        c.RegimeContextStatus.QUALIFIED: p.PositionSignalAdmissionStatusV2.ADMITTED,
        c.RegimeContextStatus.AMBIGUOUS: p.PositionSignalAdmissionStatusV2.AMBIGUOUS,
    }[composition.status]
    evaluation = ref.pullback.EMA20PullbackContextEvaluationV2(lifetime, pullback)
    decision = p.PositionSignalDecisionV2(
        composition, p.PositionStateV2.FLAT, status, pullback=evaluation)
    return replace(previous, lifetime=lifetime,
                   signal_decisions=(*previous.signal_decisions, decision))


def _advance_confirmation(previous, index, timestamp, bars, indicators):
    c = ref.confirmation
    if previous.state is not c.EntryConfirmationStateV2.AWAITING_CONFIRMATION:
        return previous
    c._validate_clock(index, timestamp, True)
    opportunity = previous.opportunity
    context = opportunity.consumed_context
    k = context.pullback_bar_index
    if index == k and previous.closed_bar_index == k and timestamp == context.pullback_timestamp:
        return previous
    if index <= previous.closed_bar_index or timestamp <= previous.closed_bar_timestamp:
        raise c.EntryConfirmationV2Error("confirmation closes must advance causally")
    if timestamp - context.pullback_timestamp > c.MAX_CONFIRMATION_ELAPSED_TIME:
        return c.EntryConfirmationEvaluationV2(
            c.EntryConfirmationStateV2.EXPIRED_CONFIRMATION_ELAPSED_TIME,
            opportunity, index, timestamp)
    if index > opportunity.last_confirmation_bar:
        return c.EntryConfirmationEvaluationV2(
            c.EntryConfirmationStateV2.EXPIRED_NO_ENTRY_CONFIRMATION,
            opportunity, index, timestamp)
    if index != previous.closed_bar_index + 1:
        raise c.EntryConfirmationV2Error("eligible confirmation candidates must be processed in order")
    bar = bars.get(index)
    if not isinstance(bar, ref.pullback.EMA20PullbackBarV2) or not bar.is_closed:
        candidate = c.EntryConfirmationCandidateV2(
            c.EntryConfirmationStatusV2.INVALID_CONFIRMATION_INPUT, index, timestamp)
    else:
        if (bar.bar_index, bar.timestamp_utc) != (index, timestamp):
            raise c.EntryConfirmationV2Error("confirmation candidate must match the observed close")
        macd = indicators.macd(at_timestamp=timestamp)
        o, close = ref.pullback._exact_price(bar.open), ref.pullback._exact_price(bar.close)
        if o is None or close is None:
            status = (c.EntryConfirmationStatusV2.INVALID_MACD_INPUT
                      if macd.status is c.MACDStatusV2.INVALID_MACD_INPUT
                      else c.EntryConfirmationStatusV2.INVALID_CONFIRMATION_INPUT)
            candidate = c.EntryConfirmationCandidateV2(status, index, timestamp,
                                                       macd_evaluation=macd)
        else:
            price = (close > o and close > opportunity.pullback_body_high
                     if context.source_event_direction is ref.context.RegimeDirection.LONG
                     else close < o and close < opportunity.pullback_body_low)
            momentum = c.evaluate_macd_momentum_v2(
                direction=context.source_event_direction, macd=macd)
            candidate = c.EntryConfirmationCandidateV2(
                c.EntryConfirmationStatusV2(macd.status.value), index, timestamp,
                price, momentum, price and momentum, macd)
    record = None
    if candidate.entry_confirmation:
        m = candidate.macd_evaluation
        record = c.EntryConfirmationRecordV2(
            context.source_event_types, context.source_event_direction,
            context.source_event_bar_index, context.source_event_timestamp,
            k, context.pullback_timestamp, context.ema_reference, index, timestamp,
            m.macd, m.signal, m.histogram, m.previous_macd, m.previous_histogram)
        state = c.EntryConfirmationStateV2.CONFIRMED
    elif index == opportunity.last_confirmation_bar:
        state = c.EntryConfirmationStateV2.EXPIRED_NO_ENTRY_CONFIRMATION
    else:
        state = c.EntryConfirmationStateV2.AWAITING_CONFIRMATION
    return c.EntryConfirmationEvaluationV2(state, opportunity, index, timestamp, candidate, record)


def _close_pending(previous, index, timestamp, bars, indicators, raw_supplier):
    p, pos, ctx = ref.pending, ref.position, ref.context
    active = previous.active_opportunity
    opportunities, stops, risks, clock_policy = (
        previous.opportunities, previous.initial_stops, previous.risks, None)
    if active is not None:
        if active.state is p.PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION:
            raise p.PendingOpportunityPolicyV2Error(
                "resolve the mandatory next Open before a later Close")
        confirmation = _advance_confirmation(active.confirmation, index, timestamp, bars, indicators)
        state = p.PendingOpportunityStateV2.AWAITING_CONFIRMATION
        risk = execution = None
        if confirmation.state in p._CONFIRMATION_EXPIRED:
            state = p.PendingOpportunityStateV2.TERMINAL_CONFIRMATION_EXPIRED
        elif confirmation.entry_confirmation:
            stops = ref.initial_stop.register_initial_stop_v2(
                previous=stops, confirmation=confirmation, bars_by_index=bars)
            clock_policy = _advance_position(previous.positions, index, timestamp, bars, indicators)
            risks = ref.risk.register_risk_position_sizing_v2(
                previous=risks, position_policy=clock_policy, instrument=ref.risk.INSTRUMENT,
                closed_bar_index=index, closed_bar_timestamp=timestamp, source_bar_closed=True,
                confirmation=confirmation, initial_stop=stops.for_confirmation(
                    confirmation.confirmation), bars_by_index=bars)
            risk = risks.decisions[-1]
            if risk.decision is ref.risk.RiskSizingDecisionV2.APPROVE:
                state = p.PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION
                execution = risks.executions.for_confirmation(confirmation.confirmation)
            else:
                state = p.PendingOpportunityStateV2.TERMINAL_RISK_REJECTED
                clock_policy = None
        owner = p.PendingOpportunityRecordV2(state, confirmation, risk, execution)
        opportunities = (*opportunities[:-1], owner)
    owner = opportunities[-1] if opportunities and opportunities[-1].state in p._PENDING else None
    positions = previous.positions
    state = (p.PendingOpportunityStateV2.POSITION_OWNED
             if positions.position_state is not pos.PositionStateV2.FLAT
             else p.PendingOpportunityStateV2.IDLE if owner is None else owner.state)
    impulse, reversal = raw_supplier()
    composition = ctx.compose_regime_context_v2(
        closed_bar_index=index, closed_bar_timestamp=timestamp, source_bar_closed=True,
        directional_impulse_event=impulse, reversal_transition_event=reversal)
    suppressions = ()
    if owner is not None:
        source = owner.consumed_context
        suppressions = tuple(p.PendingSignalSuppressionV2(
            index, timestamp, direction,
            tuple(e.event_type for e in composition.events if e.event_direction is direction),
            source.source_event_bar_index, source.pullback_bar_index,
            source.source_event_direction, owner.state)
            for direction in ctx.RegimeDirection
            if any(e.event_direction is direction for e in composition.events))
        status = (p.PendingSignalAdmissionStatusV2.SUPPRESSED_PENDING_OPPORTUNITY
                  if composition.events else p.PendingSignalAdmissionStatusV2.NO_REGIME_EVENT)
        impulse = reversal = None
    elif positions.position_state is not pos.PositionStateV2.FLAT:
        status = (p.PendingSignalAdmissionStatusV2.SUPPRESSED_POSITION_OPEN
                  if composition.events else p.PendingSignalAdmissionStatusV2.NO_REGIME_EVENT)
    else:
        status = {
            ctx.RegimeContextStatus.UNQUALIFIED: p.PendingSignalAdmissionStatusV2.NO_REGIME_EVENT,
            ctx.RegimeContextStatus.QUALIFIED: p.PendingSignalAdmissionStatusV2.ADMITTED,
            ctx.RegimeContextStatus.AMBIGUOUS: p.PendingSignalAdmissionStatusV2.AMBIGUOUS,
        }[composition.status]
    positions = clock_policy or _advance_position(
        positions, index, timestamp, bars, indicators, impulse, reversal)
    p._require_healthy_position(positions)
    pullback = positions.signal_decisions[-1].pullback
    if owner is None and pullback is not None and pullback.pullback is not None and (
        pullback.pullback.pullback_qualified
    ):
        confirmation = ref.confirmation.begin_entry_confirmation_momentum_v2(
            pullback=pullback, pullback_bar=bars[index])
        opportunities = (*opportunities, p.PendingOpportunityRecordV2(
            p.PendingOpportunityStateV2.AWAITING_CONFIRMATION, confirmation))
    decision = p.PendingSignalDecisionV2(composition, state, status, suppressions)
    return replace(previous, positions=positions, risks=risks, initial_stops=stops,
                   opportunities=opportunities, signal_decisions=(*previous.signal_decisions, decision))


def _close_exit(previous, index, timestamp, bar, indicators):
    x = ref.exits
    position = previous.positions.active_position
    if position is None or previous.end_of_data:
        return previous
    stop = previous.positions.active_stop
    if stop.stop_execution_state is not ref.stop.StructuralStopExecutionStateV2.ARMED:
        return previous
    opening = previous.latest_open
    if opening is None or (opening.bar_index, opening.timestamp_utc) != (index, timestamp):
        raise x.ExitPolicyV2Error("a closed exit observation must follow its own processed Open")
    is_long = position.entry.execution_side is ref.context.RegimeDirection.LONG
    adverse = "low" if is_long else "high"
    observation = SimpleNamespace(bar_index=index, timestamp_utc=timestamp, open=opening.open,
                                  **{adverse: getattr(bar, adverse, None)})
    current = x._resolve_stop(previous, index, timestamp, observation)
    if current.positions.active_position is None or (
        current.positions.active_stop.stop_execution_state
        is not ref.stop.StructuralStopExecutionStateV2.ARMED
    ):
        return current
    ema = indicators.ema20()
    signal = None
    if ema.status is ref.pullback.EMA20StatusV2.EVALUATED:
        if ema.known_at_timestamp != timestamp:
            raise x.ExitPolicyV2Error("the current EMA must be known at this exact Close")
        qualifies = ema.last_close < ema.ema20 if is_long else ema.last_close > ema.ema20
        if qualifies:
            signal = x.EMA20ExitSignalRecordV2(position.initial_stop_at_entry,
                                             x._sized_entry(current).quantity,
                                             index, timestamp, ema.last_close, ema.ema20)
    decision = x.EMA20PositionExitCloseV2(position.initial_stop_at_entry, index, timestamp, ema, signal)
    return replace(current, close_decisions=(*current.close_decisions, decision),
                   ema_executions=current.ema_executions if signal is None else (
                       *current.ema_executions, x.EMA20ExitExecutionEvaluationV2(signal)))


_HISTORY_PATHS = (
    "closed_bars", "raw_decisions", "policy.opportunities", "policy.signal_decisions",
    "policy.initial_stops.entries", "policy.stop_activations.entries",
    "policy.positions.positions", "policy.positions.signal_decisions",
    "policy.risks.decisions", "policy.risks.executions.entries", "policy.risks.filled_entries",
    "exits.costs.trades", "exits.close_decisions", "exits.ema_executions",
)


def _at(value, path):
    for part in path.split("."):
        value = getattr(value, part)
    return value


def _key(path, record):
    if path == "raw_decisions":
        return record.impulse.emerging_direction.impulse_candidate_bar_index
    if path == "closed_bars":
        return record.bar_index
    if path.endswith("signal_decisions"):
        return record.composition.closed_bar_index
    if path == "policy.opportunities":
        return record.consumed_context.pullback_bar_index
    if path.endswith("positions"):
        return record.entry.confirmation.confirmation_bar_index
    if path == "policy.risks.decisions":
        return record.confirmation_bar_index
    if path == "policy.risks.filled_entries":
        return record.execution.confirmation.confirmation_bar_index
    if path == "exits.costs.trades":
        return record.sized_entry.execution.confirmation.confirmation_bar_index
    if path == "exits.close_decisions":
        return record.closed_bar_index
    if path == "exits.ema_executions":
        return record.signal.exit_signal_bar_index
    if path == "policy.stop_activations.entries":
        return record.initial_stop_at_entry.execution.confirmation.confirmation_bar_index
    return record.confirmation.confirmation_bar_index


class _VersionLedger:
    def __init__(self):
        self.versions = []
        self.latest = {}
        self.order = []

    def capture(self, key, record):
        old = self.latest.get(key)
        if old is not None and self.versions[old][1] is record:
            return
        if key not in self.latest:
            self.order.append(key)
        self.latest[key] = len(self.versions)
        self.versions.append((key, record))

    def records(self):
        return tuple(self.versions[self.latest[k]][1] for k in self.order)


class RecoveryLifecycleV1:
    """Caller-owned bounded live reducer; all native histories remain in the ledger."""

    def __init__(self, *, strategy_instance_id: str, series_id: str):
        self.live = ref.begin_regime_gated_baseline_v2(
            strategy_instance_id=strategy_instance_id, series_id=series_id)
        self.indicators = ExactIncrementalIndicatorsV1()
        self.histories = {p: _VersionLedger() for p in _HISTORY_PATHS}

    def _capture(self):
        for path, ledger in self.histories.items():
            for record in _at(self.live, path):
                ledger.capture(_key(path, record), record)

    def snapshot(self):
        """Reconstruct the exact full frozen book for bounded differential auditing."""
        h = lambda path: self.histories[path].records()
        b = self.live
        positions = replace(b.policy.positions, positions=h("policy.positions.positions"),
                            signal_decisions=h("policy.positions.signal_decisions"))
        risks = replace(b.policy.risks, decisions=h("policy.risks.decisions"),
                        executions=replace(b.policy.risks.executions,
                                           entries=h("policy.risks.executions.entries")),
                        filled_entries=h("policy.risks.filled_entries"))
        policy = replace(b.policy, positions=positions, risks=risks,
                         initial_stops=replace(b.policy.initial_stops,
                                               entries=h("policy.initial_stops.entries")),
                         stop_activations=replace(b.policy.stop_activations,
                                                  entries=h("policy.stop_activations.entries")),
                         opportunities=h("policy.opportunities"),
                         signal_decisions=h("policy.signal_decisions"))
        exits = replace(b.exits, positions=positions, risk_sizing=risks,
                        costs=replace(b.exits.costs, trades=h("exits.costs.trades")),
                        close_decisions=h("exits.close_decisions"),
                        ema_executions=h("exits.ema_executions"))
        return replace(b, policy=policy, exits=exits, closed_bars=h("closed_bars"),
                       raw_decisions=h("raw_decisions"))

    def _compact(self):
        b = self.live
        opportunity = b.policy.opportunities[-1:]
        position = b.policy.positions.positions[-1:]
        needed = {p.entry.confirmation.confirmation_bar_index for p in position}
        needed.update(o.confirmation.confirmation.confirmation_bar_index
                      for o in opportunity if o.confirmation.entry_confirmation)
        decisions = tuple(d for d in b.policy.risks.decisions if d.confirmation_bar_index in needed)
        approved = {d.confirmation_bar_index for d in decisions
                    if d.decision is ref.risk.RiskSizingDecisionV2.APPROVE}
        risks = replace(b.policy.risks, decisions=decisions,
                        executions=replace(b.policy.risks.executions, entries=tuple(
                            e for e in b.policy.risks.executions.entries
                            if e.confirmation.confirmation_bar_index in approved)),
                        filled_entries=tuple(e for e in b.policy.risks.filled_entries
                            if e.execution.confirmation.confirmation_bar_index in needed))
        consume_indices = {o.consumed_context.pullback_bar_index for o in opportunity}
        signals = b.policy.positions.signal_decisions
        signals = tuple(s for s in signals if s is signals[-1]
                        or s.composition.closed_bar_index in consume_indices) if signals else ()
        positions = replace(b.policy.positions, positions=position, signal_decisions=signals)
        policy = replace(b.policy, positions=positions, risks=risks,
                         opportunities=opportunity, signal_decisions=b.policy.signal_decisions[-1:],
                         initial_stops=replace(b.policy.initial_stops, entries=tuple(
                             e for e in b.policy.initial_stops.entries
                             if e.confirmation.confirmation_bar_index in needed)),
                         stop_activations=replace(b.policy.stop_activations, entries=tuple(
                             e for e in b.policy.stop_activations.entries
                             if e.initial_stop_at_entry.execution.confirmation.confirmation_bar_index
                             in needed)))
        entry_key = position[-1].entry.confirmation.confirmation_bar_index if position else None
        emas = tuple(e for e in b.exits.ema_executions
                     if e.signal.initial_stop_at_entry.execution.confirmation.confirmation_bar_index
                     == entry_key)[-1:]
        close_signals = {e.signal.exit_signal_bar_index for e in emas}
        closes = b.exits.close_decisions
        closes = tuple(d for d in closes if d is closes[-1]
                       or d.closed_bar_index in close_signals) if closes else ()
        exits = replace(b.exits, positions=positions, risk_sizing=risks,
                        costs=replace(b.exits.costs, trades=b.exits.costs.trades[-1:]),
                        close_decisions=closes, ema_executions=emas)
        self.live = replace(b, policy=policy, exits=exits,
                            closed_bars=b.closed_bars[-21:], raw_decisions=b.raw_decisions[-21:])

    def process_open(self, opening):
        """Resolve next-Open entry, breach, stop gap and then pending EMA exit."""
        self.live = ref.process_baseline_open_v2(previous=self.live, opening_bar=opening)
        self._capture()
        self._compact()

    def process_close(self, bar):
        """Consume one actual Close in frozen causal order, with exact cached prefixes."""
        b = self.live
        if b.end_of_data:
            return
        index = getattr(bar, "bar_index", None)
        if b.closed_bars and index == b.closed_bars[-1].bar_index:
            return
        opening = b.latest_open
        if not isinstance(bar, ref.impulse.DirectionalImpulseBarV2) or bar.is_closed is not True or (
            opening is None or (index, bar.timestamp_utc) !=
            (opening.bar_index, opening.timestamp_utc) or bar.open != opening.open
        ):
            raise ref.BaselineAssemblyV2Error("the completed bar must retain its own earlier Open")
        raw = {v.bar_index: v for v in (*b.closed_bars, bar)}
        prices = ref._price_views(raw)
        self.indicators.append_closed_bar(prices[index])
        exits = _close_exit(b.exits, index, bar.timestamp_utc, bar, self.indicators)
        policy = ref.pending.adopt_pending_position_resolution_v2(
            previous=b.policy, positions=exits.positions)
        telemetry = []
        def supplier():
            decision = ref._raw_regime_decision(raw, index)
            telemetry.append(decision)
            return (decision.impulse.event, None if decision.reversal is None
                    or decision.reversal.event is None
                    else decision.reversal.event.as_regime_event())
        policy = _close_pending(policy, index, bar.timestamp_utc, prices,
                                self.indicators, supplier)
        exits = replace(exits, positions=policy.positions, risk_sizing=policy.risks)
        self.live = replace(b, policy=policy, exits=exits,
                            closed_bars=(*b.closed_bars, bar),
                            raw_decisions=(*b.raw_decisions, telemetry[0]))
        self._capture()
        self._compact()

    def finish(self):
        """Preserve terminal histories and open unrealized positions, without a fill."""
        self.live = ref.finish_regime_gated_baseline_v2(previous=self.live)
        self._capture()
