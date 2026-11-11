"""Document the actual direct-call boundary for a nonfinancial Gate 1 mission."""

from __future__ import annotations

import pytest

from agicore.trading import ema_pullback_fees_and_slippage_v2 as accounting
from agicore.trading import ema_pullback_regime_gated_baseline_v2 as baseline


def test_frozen_baseline_initialization_attempts_accounting_before_any_observation(monkeypatch):
    """The existing full V2 loop cannot be started under RC1's accounting guard."""

    class AccountingBlocked(RuntimeError):
        pass

    attempts = []

    def reject_accounting(*_args, **_kwargs):
        attempts.append("FeesAndSlippageBookV2")
        raise AccountingBlocked("accounting is forbidden in Gate 1")

    # Stop at the accounting constructor, before it can process any financial
    # value or observation. No market data is needed for this test.
    monkeypatch.setattr(accounting.FeesAndSlippageBookV2, "__post_init__", reject_accounting)
    with pytest.raises(AccountingBlocked, match="accounting is forbidden"):
        baseline.begin_regime_gated_baseline_v2(
            strategy_instance_id="gate1-boundary-test", series_id="invented-only"
        )
    assert attempts == ["FeesAndSlippageBookV2"]
