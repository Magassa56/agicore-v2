"""Explicit offline L5 recovery, using canonical journals and SQLite CAS.

The local anchor detects partial corruption, not replacement by an older valid
whole database. Retain ``anchor`` independently and pass ``expected_anchor`` to
resume when rollback detection is required. Sink effects retain their own
idempotent authorities; this store never claims a distributed transaction.
CAS fences journal publication, not concurrent external callbacks: mandatory
sinks must themselves be idempotent. Whole-runtime bootstrap and completion of
the bus handlers are separate obligations, not certified by an L5 ACK.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from agicore.core.event_delivery_contracts import AnchorRecord, canonical_json_text
from agicore.l2_memory.models.event import Event
from agicore.l2_memory.schemas.event import prepare_idempotent_event
from agicore.l5_action.price_provider import L5PriceProvider

if TYPE_CHECKING:
    from agicore.l2_memory.adapters.sqlalchemy_engine import SqlAlchemyEngine
    from agicore.l2_memory.services.event_delivery_service import EventDeliveryService

from agicore.l5_action.execution_outbox import (
    L5ExecutionDeliveryEvent,
    L5ExecutionInboxEvent,
    L5ExecutionOutcomeInbox,
    replay_inbox_journal,
)
from agicore.l5_action.execution_transaction import (
    L5ExecutionAuthorityState,
    L5ExecutionTransactionEvent,
    L5ExecutionTransactionStore,
    replay_execution_transaction_journal,
    replay_l5_execution_delivery_journal,
)

SCHEMA = "agicore.offline-l5-recovery.v1"


class L5RecoveryError(ValueError):
    """Fail-closed durable recovery or writer conflict."""


@dataclass(frozen=True)
class L5RecoveryAnchor:
    """Version and digest suitable for retention outside the SQLite file."""

    version: int
    digest: str


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(encoded):
    return hashlib.sha256(encoded.encode()).hexdigest()


class _DurableInbox(L5ExecutionOutcomeInbox):
    def __init__(self, consumer_id, owner, state=None):
        super().__init__(consumer_id)
        self._owner = owner
        self._lock = owner._lock
        if state is not None:
            self._state = state

    def accept(self, outcome, *, required_effects=()):
        with self._lock:
            self._owner._assert_current()
            if tuple(sorted(set(required_effects))) != self._owner._manifest[self.consumer_id]:
                raise L5RecoveryError("CONSUMER_CONFIGURATION_CONFLICT")
            if self._owner.delivery_state.outcomes.get(outcome.outcome_id) != outcome:
                raise L5RecoveryError("INBOX_OUTCOME_CONFLICT")
            return super().accept(outcome, required_effects=required_effects)

    def apply_effect(self, receipt, effect_name, effect):
        with self._lock:
            self._owner._assert_current()
            return super().apply_effect(receipt, effect_name, effect)

    def _publish_state(self, next_state):
        self._owner._persist(self._owner.authority_state, {self.consumer_id: next_state})
        self._state = next_state


class SQLiteL5RecoveryStore(L5ExecutionTransactionStore):
    """Opt-in offline transaction store; construct with create() or resume()."""

    def __init__(self, *args, **kwargs):
        raise L5RecoveryError("USE_EXPLICIT_CREATE_OR_RESUME")

    @staticmethod
    def _manifest_value(consumers):
        if not isinstance(consumers, Mapping) or not consumers:
            raise L5RecoveryError("INVALID_CONSUMER_MANIFEST")
        result = {}
        for consumer, effects in consumers.items():
            if (not isinstance(consumer, str) or not consumer.strip()
                    or not isinstance(effects, tuple)
                    or any(not isinstance(item, str) or not item.strip() for item in effects)
                    or len(set(effects)) != len(effects)):
                raise L5RecoveryError("INVALID_CONSUMER_MANIFEST")
            result[consumer] = tuple(sorted(effects))
        return dict(sorted(result.items()))

    @staticmethod
    @contextmanager
    def _connect(path: str | os.PathLike[str]) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=rw", uri=True)
        try:
            connection.execute("PRAGMA synchronous=FULL")
            with connection:
                yield connection
        finally:
            connection.close()

    @classmethod
    def create(cls, path: str | os.PathLike[str], *,
               consumers: Mapping[str, tuple[str, ...]], bus_authority: EventDeliveryService | None = None,
               memory_engine: SqlAlchemyEngine | None = None, **initial: Any) -> SQLiteL5RecoveryStore:
        """Create exclusively a new explicit database; never overwrite an authority."""
        manifest = cls._manifest_value(consumers)
        instance = object.__new__(cls)
        L5ExecutionTransactionStore.__init__(instance, **initial)
        instance._manifest = manifest
        instance._bus_authority = bus_authority
        instance._memory_engine = memory_engine
        instance._path = Path(path).resolve()
        instance._consumer_inboxes = {
            key: _DurableInbox(key, instance) for key in manifest
        }
        # O_EXCL is necessary: SQLite CREATE alone silently opens an existing file.
        descriptor = os.open(instance._path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(descriptor)
        document = instance._document(instance.authority_state, {}, 0)
        encoded = _encode(document)
        with instance._connect(instance._path) as connection:
            connection.execute("CREATE TABLE recovery (id INTEGER PRIMARY KEY CHECK(id=1), "
                               "version INTEGER NOT NULL, digest TEXT NOT NULL, document TEXT NOT NULL)")
            connection.execute("INSERT INTO recovery VALUES (1, ?, ?, ?)", (0, _digest(encoded), encoded))
        instance._anchor = L5RecoveryAnchor(0, _digest(encoded))
        return instance

    @classmethod
    def resume(cls, path: str | os.PathLike[str], *,
               consumers: Mapping[str, tuple[str, ...]], price_provider: L5PriceProvider,
               expected_anchor: L5RecoveryAnchor | None = None,
               bus_authority: EventDeliveryService | None = None, expected_bus_anchor: AnchorRecord | None = None,
               memory_engine: SqlAlchemyEngine | None = None) -> SQLiteL5RecoveryStore:
        """Validate every journal before exposing a reconstructed runtime authority."""
        manifest = cls._manifest_value(consumers)
        with cls._connect(path) as connection:
            rows = connection.execute("SELECT version, digest, document FROM recovery").fetchall()
        if len(rows) != 1:
            raise L5RecoveryError("MISSING_RECOVERY_ANCHOR")
        version, digest, encoded = rows[0]
        anchor = L5RecoveryAnchor(version, digest)
        if _digest(encoded) != digest or (expected_anchor is not None and anchor != expected_anchor):
            raise L5RecoveryError("RECOVERY_ANCHOR_MISMATCH")
        try:
            document = json.loads(encoded)
            if (_encode(document) != encoded or document["schema"] != SCHEMA
                    or document["version"] != version or type(version) is not int or version < 0
                    or document["consumers"] != {key: list(value) for key, value in manifest.items()}
                    or set(document) != {"schema", "version", "consumers", "execution", "delivery", "inboxes"}
                    or set(document["inboxes"]) != set(manifest)):
                raise L5RecoveryError("RECOVERY_CONFIGURATION_CONFLICT")
            execution = tuple(L5ExecutionTransactionEvent(**value) for value in document["execution"])
            aggregate, _ = replay_execution_transaction_journal(
                execution, expected_final_hash=execution[-1].event_hash,
            )
            inbox_events = {
                key: tuple(L5ExecutionInboxEvent(**value) for value in values)
                for key, values in document["inboxes"].items()
            }
            inbox_states = {
                key: replay_inbox_journal(values, expected_final_hash=values[-1].event_hash)[0]
                for key, values in inbox_events.items()
            }
            delivery_events = tuple(L5ExecutionDeliveryEvent(**value) for value in document["delivery"])
            # This profile forbids legacy unanchored acknowledgements.
            for event in delivery_events:
                if (event.event_type == "OUTCOME_ACKNOWLEDGED"
                        and not event.payload["acknowledgement"]["emission_accepted_hash"]):
                    raise L5RecoveryError("CANONICAL_ACK_REQUIRED")
            delivery, _ = replay_l5_execution_delivery_journal(
                delivery_events, execution_events=execution,
                expected_final_hash=delivery_events[-1].event_hash,
                inbox_events=inbox_events,
                expected_inbox_hash={key: values[-1].event_hash for key, values in inbox_events.items()},
                bus_authority=bus_authority, expected_bus_anchor=expected_bus_anchor,
            )
            for key, state in inbox_states.items():
                for receipt in state.receipts.values():
                    outcome = delivery.outcomes.get(receipt.outcome_id)
                    if (receipt.consumer_id != key or receipt.required_effects != manifest[key]
                            or outcome is None or outcome.outcome_hash != receipt.outcome_hash):
                        raise L5RecoveryError("INBOX_OUTCOME_CONFLICT")
            cls._verify_completed_effects(delivery, inbox_states, memory_engine, bus_authority)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise L5RecoveryError(f"INVALID_RECOVERY_DOCUMENT: {exc}") from exc
        instance = object.__new__(cls)
        L5ExecutionTransactionStore.__init__(
            instance, initial_context=aggregate.risk_context,
            initial_risk_journal=aggregate.risk_journal, initial_positions=aggregate.positions,
            price_provider=price_provider,
        )
        instance._authority = L5ExecutionAuthorityState(aggregate, delivery)
        instance._path = Path(path).resolve()
        instance._manifest = manifest
        instance._bus_authority = bus_authority
        instance._memory_engine = memory_engine
        instance._anchor = anchor
        instance._consumer_inboxes = {
            key: _DurableInbox(key, instance, state) for key, state in inbox_states.items()
        }
        return instance

    @property
    def anchor(self) -> L5RecoveryAnchor:
        """Return the latest committed anchor for independent retention."""
        with self._lock:
            return self._anchor

    def consumer_inbox(self, consumer_id: str,
                       proposed: L5ExecutionOutcomeInbox | None = None) -> L5ExecutionOutcomeInbox:
        """Return only a consumer from the frozen durable manifest."""
        with self._lock:
            inbox = self._consumer_inboxes.get(consumer_id)
            if inbox is None or (proposed is not None and proposed is not inbox):
                raise L5RecoveryError("CONSUMER_CONFIGURATION_CONFLICT")
            return inbox

    def _document(self, authority, overrides, version):
        return {
            "schema": SCHEMA, "version": version,
            "consumers": {key: list(value) for key, value in self._manifest.items()},
            "execution": [event.canonical() for event in authority.aggregate_state.execution_journal],
            "delivery": [event.canonical() for event in authority.delivery_state.journal],
            "inboxes": {key: [event.canonical() for event in overrides.get(key, inbox.state).journal]
                        for key, inbox in self._consumer_inboxes.items()},
        }

    def _assert_current(self):
        with self._connect(self._path) as connection:
            row = connection.execute("SELECT version, digest, document FROM recovery WHERE id=1").fetchone()
        if (row is None or L5RecoveryAnchor(row[0], row[1]) != self._anchor
                or _digest(row[2]) != row[1]):
            raise L5RecoveryError("STALE_OR_CORRUPT_RECOVERY_AUTHORITY")

    def _persist(self, authority, overrides):
        self._verify_completed_effects(
            authority.delivery_state,
            {key: overrides.get(key, inbox.state) for key, inbox in self._consumer_inboxes.items()},
            self._memory_engine, self._bus_authority,
        )
        encoded = _encode(self._document(authority, overrides, self._anchor.version + 1))
        next_anchor = L5RecoveryAnchor(self._anchor.version + 1, _digest(encoded))
        with self._connect(self._path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT version, digest, document FROM recovery WHERE id=1").fetchone()
            if (row is None or L5RecoveryAnchor(row[0], row[1]) != self._anchor
                    or _digest(row[2]) != row[1]):
                raise L5RecoveryError("STALE_OR_CORRUPT_RECOVERY_AUTHORITY")
            changed = connection.execute(
                "UPDATE recovery SET version=?, digest=?, document=? WHERE id=1 AND version=? AND digest=?",
                (next_anchor.version, next_anchor.digest, encoded, self._anchor.version, self._anchor.digest),
            ).rowcount
            if changed != 1:
                raise L5RecoveryError("STALE_RECOVERY_WRITER")
        self._anchor = next_anchor

    @staticmethod
    def _verify_completed_effects(delivery, inbox_states, memory_engine, bus_authority):
        """Read exact D002/bus sink proofs before trusting a completed inbox effect.

        This validator covers execution_agent's canonical memory and bus effects;
        it never recreates missing sink state or certifies arbitrary callbacks.
        """
        bus_state = None
        for state in inbox_states.values():
            for receipt in state.receipts.values():
                completed = state.effect_event_hashes.get(receipt.receipt_id, {})
                outcome = delivery.outcomes[receipt.outcome_id]
                if "memory" in completed:
                    if memory_engine is None:
                        raise L5RecoveryError("MEMORY_AUTHORITY_REQUIRED")
                    if receipt.consumer_id != "execution_agent":
                        raise L5RecoveryError("UNSUPPORTED_MEMORY_EFFECT_PROFILE")
                    expected = prepare_idempotent_event(
                        effect_id=f"execution-memory-{receipt.receipt_hash}",
                        occurred_at=datetime.fromisoformat(outcome.request_payload["intent"]["timestamp"]),
                        event_type="agent.execution.order.processed", agent_id=receipt.consumer_id,
                        payload={"schema": "agicore.execution-memory-effect.v1",
                                 "receipt_id": receipt.receipt_id, "receipt_hash": receipt.receipt_hash,
                                 "outcome": outcome.canonical()},
                    )
                    with memory_engine.session() as session:
                        event = session.execute(select(Event).where(Event.effect_id == expected.effect_id)).scalar_one_or_none()
                        if event is None:
                            raise L5RecoveryError("MEMORY_EFFECT_MISSING")
                        observed_time = event.created_at
                        if observed_time.tzinfo is None:
                            observed_time = observed_time.replace(tzinfo=UTC)
                        if (event.payload_hash != expected.payload_hash or event.payload != expected.payload
                                or event.event_type != expected.event_type or event.agent_id != expected.agent_id
                                or event.task_id != expected.task_id or event.session_id != expected.session_id
                                or observed_time != expected.occurred_at):
                            raise L5RecoveryError("MEMORY_EFFECT_CONFLICT")
                if "event_bus" in completed:
                    if bus_authority is None:
                        raise L5RecoveryError("CANONICAL_BUS_AUTHORITY_REQUIRED")
                    if bus_state is None:
                        bus_state = bus_authority.replay(expected_anchor=bus_authority.anchor())
                    publications = [event for event in delivery.journal
                                    if event.event_type == "OUTCOME_PUBLISHED"
                                    and event.payload["outcome"]["outcome_id"] == outcome.outcome_id]
                    source_sequence = publications[0].sequence_number
                    expected_payload = {
                        "schema": "agicore.execution-outcome-emission.v1",
                        "consumer_id": receipt.consumer_id, "outcome_id": outcome.outcome_id,
                        "outcome_hash": outcome.outcome_hash, "receipt_id": receipt.receipt_id,
                        "receipt_hash": receipt.receipt_hash, "source_sequence": source_sequence,
                        "outcome": outcome.canonical(),
                    }
                    matches = [emission for emission in bus_state.emissions
                               if emission.source_identity == receipt.receipt_id
                               and emission.consumer_id == receipt.consumer_id
                               and emission.outcome_id == outcome.outcome_id
                               and emission.outcome_hash == outcome.outcome_hash
                               and emission.receipt_hash == receipt.receipt_hash
                               and emission.source_sequence == source_sequence
                               and emission.event_type == "agent.execution.order.processed"
                               and canonical_json_text(emission.payload) == canonical_json_text(expected_payload)
                               and emission.emission_effect_id in bus_state.acceptance_hashes]
                    if len(matches) != 1:
                        raise L5RecoveryError("UNVERIFIED_BUS_ACCEPTANCE")

    def _publish_state(self, next_state):
        authority = (next_state if isinstance(next_state, L5ExecutionAuthorityState)
                     else L5ExecutionAuthorityState(next_state, self._authority.delivery_state))
        for acknowledgement in authority.delivery_state.acknowledgements.values():
            if not acknowledgement.emission_accepted_hash:
                raise L5RecoveryError("CANONICAL_ACK_REQUIRED")
        if authority.delivery_state.acknowledgements != self._authority.delivery_state.acknowledgements:
            if self._bus_authority is None:
                raise L5RecoveryError("CANONICAL_BUS_AUTHORITY_REQUIRED")
            inbox_events = {key: inbox.state.journal for key, inbox in self._consumer_inboxes.items()}
            replay_l5_execution_delivery_journal(
                authority.delivery_state.journal,
                execution_events=authority.aggregate_state.execution_journal,
                expected_final_hash=authority.delivery_state.journal[-1].event_hash,
                inbox_events=inbox_events,
                expected_inbox_hash={key: events[-1].event_hash for key, events in inbox_events.items()},
                bus_authority=self._bus_authority, expected_bus_anchor=self._bus_authority.anchor(),
            )
        self._persist(authority, {})
        self._authority = authority
