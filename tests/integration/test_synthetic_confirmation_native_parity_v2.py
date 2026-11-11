"""Cross-check the new causal handoff against the frozen synthetic native replay.

Only pre-existing invented fixtures are used; no real dataset, broker or OOS.
The native replay also calculates synthetic accounting as part of its contract.
"""

from fractions import Fraction

import pytest

from agicore.trading import ema_pullback_v2_development_replay as frozen
from agicore.trading.regime_context_v2 import RegimeDirection
from agicore.trading.synthetic_confirmation_replay_v2 import replay_confirmation_native
from tests.unit.trading.test_ema_pullback_v2_development_replay import _raw
from tests.unit.trading.test_ema_pullback_v2_pending_opportunity_audit import _bars


def _fraction(value):
    return Fraction(value["numerator"], value["denominator"])


@pytest.mark.parametrize("direction", [RegimeDirection.LONG, RegimeDirection.SHORT])
def test_confirmation_provenance_matches_native_full_replay(direction):
    raw = _raw(_bars(direction))
    handoff = replay_confirmation_native(raw)
    assert handoff.summary["stop_reason"] == "CONFIRMED_BEFORE_RISK"
    assert handoff.summary["processed_observations"] == 36
    assert handoff.native_confirmation is not None
    observed = handoff.native_confirmation.confirmation
    assert observed is not None

    result = frozen.evaluate_synthetic_development_replay_v2(
        raw, bindings=frozen.read_frozen_replay_bindings_v2()
    ).document
    assert len(result["open_trade_records"]) == 1
    reference = result["open_trade_records"][0]["immutable_provenance"]["confirmation"]
    assert reference["source_regime_event_bar_index"] == observed.source_regime_event_bar_index
    assert (
        reference["source_regime_event_direction"] == observed.source_regime_event_direction.value
    )
    assert reference["pullback_bar_index"] == observed.pullback_bar_index
    assert reference["confirmation_bar_index"] == observed.confirmation_bar_index
    for field in ("source_regime_event_timestamp", "pullback_timestamp", "confirmation_timestamp"):
        assert reference[field] == getattr(observed, field).isoformat().replace("+00:00", "Z")
    for field in (
        "ema_reference",
        "macd",
        "signal",
        "histogram",
        "previous_macd",
        "previous_histogram",
    ):
        assert _fraction(reference[field]) == getattr(observed, field)
