"""Migration L2 — création initiale du schéma LTM.

Phase 2 : create_all sur Base.metadata. Phase ultérieure : Alembic.
"""
from __future__ import annotations

import structlog

from ..adapters.sqlalchemy_engine import SqlAlchemyEngine
from ..models.base import Base

logger = structlog.get_logger(__name__)


def init_schema(engine: SqlAlchemyEngine) -> list[str]:
    """Crée toutes les tables LTM. Idempotent (CREATE TABLE IF NOT EXISTS)."""
    # Importer les modèles pour qu'ils se déclarent dans Base.metadata
    from ..models import agent_state, event, execution_context, task  # noqa: F401

    engine.create_all(Base.metadata)
    from .add_idempotent_memory_effect import add_idempotent_memory_effect

    add_idempotent_memory_effect(engine)
    tables = list(Base.metadata.tables.keys())
    logger.info("ltm.migration.init_schema.completed", tables=tables)
    return tables


def drop_schema(engine: SqlAlchemyEngine) -> list[str]:
    """Supprime toutes les tables LTM. Réservé aux tests / reset."""
    from ..models import agent_state, event, execution_context, task  # noqa: F401

    tables = list(Base.metadata.tables.keys())
    engine.drop_all(Base.metadata)
    logger.warning("ltm.migration.drop_schema.completed", tables=tables)
    return tables


__all__ = ["init_schema", "drop_schema"]
