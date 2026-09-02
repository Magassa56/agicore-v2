"""ORM model for the durable EventBus delivery authority."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class EventDeliveryBase(DeclarativeBase):
    """Dedicated metadata so legacy L2 ``create_all`` cannot bypass migration."""


class EventHandlerManifest(EventDeliveryBase):
    """Immutable identity and canonical content of one bus-owned manifest."""

    __tablename__ = "event_handler_manifests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    authority_id: Mapped[str] = mapped_column(String(128), nullable=False)
    runtime_profile_id: Mapped[str] = mapped_column(String(128), nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    manifest_version: Mapped[str] = mapped_column(String(128), nullable=False)
    manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    canonical_json: Mapped[str] = mapped_column(Text, nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index(
            "ux_event_manifest_identity",
            "authority_id",
            "runtime_profile_id",
            "event_type",
            "manifest_version",
            unique=True,
        ),
        Index(
            "ux_event_manifest_hash",
            "authority_id",
            "manifest_hash",
            unique=True,
        ),
    )


class EventHandlerManifestEntry(EventDeliveryBase):
    """One immutable handler snapshot belonging to a manifest."""

    __tablename__ = "event_handler_manifest_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manifest_id: Mapped[int] = mapped_column(
        ForeignKey("event_handler_manifests.id"), nullable=False
    )
    handler_id: Mapped[str] = mapped_column(String(128), nullable=False)
    handler_version: Mapped[str] = mapped_column(String(128), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    dispatch_class: Mapped[str] = mapped_column(String(16), nullable=False)

    __table_args__ = (
        Index(
            "ux_event_manifest_handler_identity",
            "manifest_id",
            "handler_id",
            "handler_version",
            unique=True,
        ),
        Index(
            "ux_event_manifest_handler_ordinal",
            "manifest_id",
            "ordinal",
            unique=True,
        ),
        CheckConstraint("ordinal >= 0", name="ck_event_manifest_ordinal_nonnegative"),
        CheckConstraint(
            "dispatch_class IN ('direct', 'wildcard')",
            name="ck_event_manifest_dispatch_class",
        ),
    )


class EventBusEmission(EventDeliveryBase):
    """Durably accepted canonical emission and its manifest snapshot."""

    __tablename__ = "event_bus_emissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    authority_id: Mapped[str] = mapped_column(String(128), nullable=False)
    authority_version: Mapped[str] = mapped_column(String(128), nullable=False)
    source_identity: Mapped[str] = mapped_column(String(128), nullable=False)
    consumer_id: Mapped[str] = mapped_column(String(128), nullable=False)
    outcome_id: Mapped[str] = mapped_column(String(128), nullable=False)
    outcome_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    receipt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    runtime_profile_id: Mapped[str] = mapped_column(String(128), nullable=False)
    manifest_version: Mapped[str] = mapped_column(String(128), nullable=False)
    manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    emission_effect_id: Mapped[str] = mapped_column(String(64), nullable=False)
    accepted_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)

    __table_args__ = (
        Index(
            "ux_event_emission_source",
            "authority_id",
            "source_identity",
            unique=True,
        ),
        Index(
            "ux_event_emission_effect",
            "authority_id",
            "emission_effect_id",
            unique=True,
        ),
        Index(
            "ux_event_emission_source_sequence",
            "authority_id",
            "consumer_id",
            "source_sequence",
            unique=True,
        ),
        CheckConstraint("source_sequence > 0", name="ck_event_source_sequence_positive"),
        CheckConstraint("accepted_sequence > 0", name="ck_event_accepted_sequence_positive"),
        CheckConstraint(
            "status IN ('ACCEPTED', 'COMPLETED')",
            name="ck_event_emission_status",
        ),
    )


class EventHandlerDelivery(EventDeliveryBase):
    """Mutable projection of one immutable manifest handler delivery."""

    __tablename__ = "event_handler_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emission_id: Mapped[int] = mapped_column(
        ForeignKey("event_bus_emissions.id"), nullable=False
    )
    authority_id: Mapped[str] = mapped_column(String(128), nullable=False)
    emission_effect_id: Mapped[str] = mapped_column(String(64), nullable=False)
    handler_effect_id: Mapped[str] = mapped_column(String(64), nullable=False)
    handler_id: Mapped[str] = mapped_column(String(128), nullable=False)
    handler_version: Mapped[str] = mapped_column(String(128), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    dispatch_class: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    fencing_generation: Mapped[int] = mapped_column(Integer, nullable=False)
    worker_identity: Mapped[str | None] = mapped_column(String(128), nullable=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    result_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index(
            "ux_event_delivery_effect",
            "authority_id",
            "handler_effect_id",
            unique=True,
        ),
        Index(
            "ux_event_delivery_ordinal",
            "emission_id",
            "ordinal",
            unique=True,
        ),
        CheckConstraint("ordinal >= 0", name="ck_event_delivery_ordinal_nonnegative"),
        CheckConstraint(
            "fencing_generation >= 0",
            name="ck_event_delivery_fencing_nonnegative",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'CLAIMED', 'APPLIED', 'COMPLETED', 'CONFLICT')",
            name="ck_event_delivery_status",
        ),
        CheckConstraint(
            "dispatch_class IN ('direct', 'wildcard')",
            name="ck_event_delivery_dispatch_class",
        ),
        CheckConstraint(
            "(status = 'PENDING' AND worker_identity IS NULL AND claimed_at IS NULL "
            "AND result_status IS NULL AND result_hash IS NULL AND result_json IS NULL) OR "
            "(status = 'CLAIMED' AND worker_identity IS NOT NULL AND claimed_at IS NOT NULL "
            "AND result_status IS NULL AND result_hash IS NULL AND result_json IS NULL) OR "
            "(status IN ('APPLIED', 'COMPLETED', 'CONFLICT') "
            "AND worker_identity IS NOT NULL AND claimed_at IS NOT NULL "
            "AND result_status IS NOT NULL AND result_hash IS NOT NULL "
            "AND result_json IS NOT NULL)",
            name="ck_event_delivery_progress_shape",
        ),
    )


class EventDeliveryJournal(EventDeliveryBase):
    """Immutable hash-chained delivery transition."""

    __tablename__ = "event_delivery_journal"

    authority_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    sequence: Mapped[int] = mapped_column(Integer, primary_key=True)
    authority_version: Mapped[str] = mapped_column(String(128), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    emission_effect_id: Mapped[str] = mapped_column(String(64), nullable=False)
    handler_effect_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fencing_generation: Mapped[int] = mapped_column(Integer, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        Index(
            "ux_event_delivery_journal_hash",
            "authority_id",
            "event_hash",
            unique=True,
        ),
        CheckConstraint("sequence > 0", name="ck_event_journal_sequence_positive"),
        CheckConstraint(
            "fencing_generation >= 0",
            name="ck_event_journal_fencing_nonnegative",
        ),
        CheckConstraint(
            "event_type IN ('EMISSION_ACCEPTED', 'HANDLER_CLAIMED', "
            "'HANDLER_CLAIM_RECOVERED', 'HANDLER_APPLIED', "
            "'HANDLER_COMPLETED', 'EMISSION_COMPLETED')",
            name="ck_event_journal_type",
        ),
    )


class EventDeliveryAnchor(EventDeliveryBase):
    """Final journal anchor for one authority identity."""

    __tablename__ = "event_delivery_anchor"

    authority_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    authority_version: Mapped[str] = mapped_column(String(128), nullable=False)
    last_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    last_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        CheckConstraint("last_sequence >= 0", name="ck_event_anchor_sequence_nonnegative"),
    )


__all__ = [
    "EventBusEmission",
    "EventDeliveryAnchor",
    "EventDeliveryBase",
    "EventDeliveryJournal",
    "EventHandlerDelivery",
    "EventHandlerManifest",
    "EventHandlerManifestEntry",
]
