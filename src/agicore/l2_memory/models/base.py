"""Base déclarative SQLAlchemy pour la mémoire long terme (LTM)."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all LTM ORM models."""
    pass


__all__ = ["Base"]
