"""DryRunHealthChecker — Phase 9A.

Detects feed stalls, repeated order rejects, and order-queue congestion
by inspecting a DryRunSessionSnapshot and the DryRunRecorder.

Returns a list of HealthReport objects (one per detected condition).
An empty list means the session is healthy.

Stall detection rules
---------------------
- stall_tick_threshold == 0: flag STALLED_FEED when ticks_processed == 0
- stall_tick_threshold > 0 : flag STALLED_FEED when
                             ticks_processed < stall_tick_threshold

Reject detection
----------------
- Flag REPEATED_REJECTS when rejects / orders > reject_rate_threshold
  (only evaluated when orders > 0)

Congestion detection
--------------------
- backlog = orders_submitted - fills - rejects
- Flag QUEUE_CONGESTION when backlog > backlog_order_threshold
"""
from __future__ import annotations

from agicore.metrics.health import HealthReport, HealthStatus

from .models import DryRunSessionSnapshot, DryRunState
from .recorder import DryRunRecorder


class DryRunHealthChecker:
    """Health checker for a live dry-run session.

    Parameters
    ----------
    stall_tick_threshold:
        Minimum number of ticks expected before the session is considered
        active. 0 means "flag any session with zero ticks".
    backlog_order_threshold:
        Maximum number of pending (unfilled, unrejected) orders before
        QUEUE_CONGESTION is flagged.
    reject_rate_threshold:
        Maximum acceptable ratio rejects / orders_submitted before
        REPEATED_REJECTS is flagged.
    """

    def __init__(
        self,
        *,
        stall_tick_threshold: int = 0,
        backlog_order_threshold: int = 1_000,
        reject_rate_threshold: float = 0.5,
    ) -> None:
        self._stall_threshold = stall_tick_threshold
        self._backlog_threshold = backlog_order_threshold
        self._reject_threshold = reject_rate_threshold

    def check(
        self,
        snap: DryRunSessionSnapshot,
        recorder: DryRunRecorder,
    ) -> list[HealthReport]:
        """Evaluate all health checks and return a list of HealthReport.

        Parameters
        ----------
        snap:
            Current session snapshot (lightweight, cheap to produce).
        recorder:
            The event recorder (used for future deep-inspection checks).

        Returns
        -------
        list[HealthReport]
            Empty list if everything is healthy; one entry per problem found.
        """
        reports: list[HealthReport] = []

        reports.extend(self._check_stall(snap))
        reports.extend(self._check_rejects(snap))
        reports.extend(self._check_congestion(snap))

        return reports

    # ---------------------------------------------------------------- checkers

    def _check_stall(self, snap: DryRunSessionSnapshot) -> list[HealthReport]:
        """Flag STALLED_FEED when the session is RUNNING but ticks are low."""
        if snap.state != DryRunState.RUNNING:
            return []

        ticks = snap.ticks_processed
        threshold = self._stall_threshold

        # Stall condition:
        # - threshold == 0: stall only when ticks == 0
        # - threshold > 0 : stall when ticks < threshold (boundary is OK)
        if threshold == 0:
            stalled = ticks == 0
        else:
            stalled = ticks < threshold

        if stalled:
            return [
                HealthReport(
                    status=HealthStatus.STALLED_FEED,
                    detail=(
                        f"ticks_processed={ticks} is below "
                        f"stall_tick_threshold={threshold}"
                    ),
                )
            ]
        return []

    def _check_rejects(self, snap: DryRunSessionSnapshot) -> list[HealthReport]:
        """Flag REPEATED_REJECTS when reject rate exceeds threshold."""
        orders = snap.orders_submitted
        if orders == 0:
            return []

        rate = snap.rejects / orders
        if rate > self._reject_threshold:
            return [
                HealthReport(
                    status=HealthStatus.REPEATED_REJECTS,
                    detail=(
                        f"reject_rate={rate:.2%} exceeds "
                        f"threshold={self._reject_threshold:.2%} "
                        f"(rejects={snap.rejects}, orders={orders})"
                    ),
                )
            ]
        return []

    def _check_congestion(self, snap: DryRunSessionSnapshot) -> list[HealthReport]:
        """Flag QUEUE_CONGESTION when unfilled order backlog is too large."""
        backlog = snap.orders_submitted - snap.fills - snap.rejects
        if backlog > self._backlog_threshold:
            return [
                HealthReport(
                    status=HealthStatus.QUEUE_CONGESTION,
                    detail=(
                        f"order backlog={backlog} exceeds "
                        f"threshold={self._backlog_threshold}"
                    ),
                )
            ]
        return []


__all__ = ["DryRunHealthChecker"]
