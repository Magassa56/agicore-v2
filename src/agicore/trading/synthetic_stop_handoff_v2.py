"""Handoff from a native V2 confirmation to an immutable structural stop.

This adapter is for already invented, validated observations.  It reads no
file or external service and does not establish that caller-supplied prices
are synthetic.  No entry, position, target, accounting or broker is invoked.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from .ema_pullback_entry_confirmation_v2 import EntryConfirmationEvaluationV2
from .ema_pullback_initial_stop_v2 import (
    InitialStopBookV2,
    InitialStopEvaluationV2,
    StructuralStopBarInputV2,
    register_initial_stop_v2,
)


class _ClosedWindow(Mapping[int, StructuralStopBarInputV2]):
    """Expose only k..q; never inspect the number or contents of later bars."""

    def __init__(self, first: int, last: int, observations: tuple) -> None:
        self._first = first
        self._last = last
        self._observations = observations

    def __getitem__(self, index: int) -> StructuralStopBarInputV2:
        if type(index) is not int or not self._first <= index <= self._last:
            raise ValueError("stop cannot read outside the confirmed closed window")
        offset = index - self._first
        if offset >= len(self._observations) or self._observations[offset] is None:
            raise KeyError(index)
        return self._observations[offset]

    def __iter__(self) -> Iterator[int]:
        raise TypeError("stop window enumeration is forbidden")

    def __len__(self) -> int:
        raise TypeError("stop window length is not exposed to the evaluator")


@dataclass(frozen=True)
class SyntheticStopHandoffV2:
    """The retained stop book and its immutable evaluation for one confirmation."""

    book: InitialStopBookV2
    evaluation: InitialStopEvaluationV2


def capture_synthetic_stop_v2(
    *,
    confirmation: EntryConfirmationEvaluationV2,
    closed_window: tuple[StructuralStopBarInputV2 | None, ...],
    previous: InitialStopBookV2 | None = None,
) -> SyntheticStopHandoffV2:
    """Register exactly once using only closed bars k..q from a native signal.

    The frozen stop function validates confirmation provenance and timestamps.
    Missing bars retain its explicit incomplete outcome; malformed inputs are
    rejected. Repeating a registered confirmation keeps its original snapshot
    without reading the replacement bars. Only unbound stop books are accepted.
    """
    if (
        not isinstance(confirmation, EntryConfirmationEvaluationV2)
        or not confirmation.entry_confirmation
    ):
        raise ValueError("a native, qualified confirmation is required")
    record = confirmation.confirmation
    k, q = record.pullback_bar_index, record.confirmation_bar_index
    if type(k) is not int or type(q) is not int or q - k not in (1, 2):
        raise ValueError("confirmation window must be k..k+1 or k..k+2")
    if type(closed_window) is not tuple or len(closed_window) > q - k + 1:
        raise ValueError("closed window cannot include bars after confirmation")
    book = InitialStopBookV2() if previous is None else previous
    if not isinstance(book, InitialStopBookV2):
        raise ValueError("previous stop book has an invalid type")
    if any(entry.at_entry is not None for entry in book.entries):
        raise ValueError("entry-bound stop books are outside this handoff")
    registered = register_initial_stop_v2(
        previous=book,
        confirmation=confirmation,
        bars_by_index=_ClosedWindow(k, q, closed_window),
    )
    return SyntheticStopHandoffV2(registered, registered.for_confirmation(record))
