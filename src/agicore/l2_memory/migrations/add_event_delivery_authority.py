"""Additive migration for the durable EventBus delivery authority."""
from __future__ import annotations

import re
from collections.abc import Mapping

from sqlalchemy import inspect, text
from sqlalchemy.schema import CreateIndex, CreateTable

from ..adapters.sqlalchemy_engine import SqlAlchemyEngine
from ..models.event_delivery import EventDeliveryBase


_TABLES = frozenset(
    {
        "event_handler_manifests",
        "event_handler_manifest_entries",
        "event_bus_emissions",
        "event_handler_deliveries",
        "event_delivery_journal",
        "event_delivery_anchor",
    }
)
_INDEXES = frozenset(
    index.name
    for table in EventDeliveryBase.metadata.tables.values()
    for index in table.indexes
    if index.name is not None
)


def _normalized_sql(definition: str) -> str:
    tokens = re.findall(
        r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|[a-z_][a-z0-9_]*|"
        r"!=|<>|<=|>=|==|[(),.=;]|\S",
        definition.lower(),
    )
    if tokens and tokens[-1] == ";":
        tokens.pop()
    return " ".join(tokens).replace('"', "")


def _sqlite_object(connection, *, name: str) -> Mapping[str, object] | None:
    return connection.execute(
        text("SELECT type, name, tbl_name, sql FROM sqlite_master WHERE name = :name"),
        {"name": name},
    ).mappings().one_or_none()


def _validate_sqlite(connection) -> None:
    dialect = connection.dialect
    for table in EventDeliveryBase.metadata.sorted_tables:
        existing = _sqlite_object(connection, name=table.name)
        expected = str(CreateTable(table).compile(dialect=dialect))
        if (
            existing is None
            or existing["type"] != "table"
            or existing["tbl_name"] != table.name
            or not isinstance(existing["sql"], str)
            or _normalized_sql(existing["sql"]) != _normalized_sql(expected)
        ):
            raise RuntimeError(f"incompatible SQLite delivery table {table.name}")

        triggers = connection.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'trigger' AND tbl_name = :table_name"
            ),
            {"table_name": table.name},
        ).all()
        if triggers:
            raise RuntimeError(f"unexpected SQLite trigger on {table.name}")

        expected_indexes = {index.name: index for index in table.indexes}
        rows = connection.exec_driver_sql(
            f"PRAGMA index_list('{table.name}')"
        ).mappings().all()
        observed_created = {
            str(row["name"]): row for row in rows if str(row["origin"]).lower() == "c"
        }
        if set(observed_created) != set(expected_indexes):
            raise RuntimeError(f"incompatible SQLite indexes on {table.name}")
        for name, index in expected_indexes.items():
            row = observed_created[name]
            existing_index = _sqlite_object(connection, name=name)
            expected_index = str(CreateIndex(index).compile(dialect=dialect))
            if (
                int(row["unique"]) != int(index.unique)
                or int(row["partial"]) != 0
                or existing_index is None
                or existing_index["type"] != "index"
                or existing_index["tbl_name"] != table.name
                or not isinstance(existing_index["sql"], str)
                or _normalized_sql(existing_index["sql"])
                != _normalized_sql(expected_index)
            ):
                raise RuntimeError(f"incompatible SQLite delivery index {name}")
            info = connection.exec_driver_sql(
                f'PRAGMA index_xinfo("{name}")'
            ).mappings().all()
            keys = [item for item in info if int(item["key"]) == 1]
            expected_columns = [column.name for column in index.columns]
            if (
                [item["name"] for item in keys] != expected_columns
                or any(int(item["cid"]) < 0 for item in keys)
                or any(int(item["desc"]) != 0 for item in keys)
                or any(str(item["coll"]).upper() != "BINARY" for item in keys)
            ):
                raise RuntimeError(f"incompatible SQLite delivery index {name}")


def add_event_delivery_authority(engine: SqlAlchemyEngine) -> None:
    """Create or validate the complete delivery authority as one migration unit.

    SQLite journal and anchor reside in the same database. They detect accidental
    corruption and replay divergence, but cannot protect against an administrator
    who deliberately rewrites both the journal and its anchor.
    """
    if not engine.delivery_authority_enabled:
        raise RuntimeError("event delivery migration requires delivery authority mode")
    if engine.engine.dialect.name != "sqlite":
        raise RuntimeError(
            "EventDelivery B1 migration supports SQLite backends only"
        )
    with engine.engine.begin() as connection:
        dialect = connection.dialect.name
        if dialect != "sqlite":
            raise RuntimeError(f"unsupported event delivery backend: {dialect}")
        existing_tables = set(inspect(connection).get_table_names())
        present = existing_tables & _TABLES
        if present and present != _TABLES:
            raise RuntimeError("partial event delivery authority migration detected")

        collisions = connection.execute(
            text(
                "SELECT type, name, tbl_name FROM sqlite_master "
                "WHERE name IN ("
                + ",".join(f"'{name}'" for name in sorted(_INDEXES))
                + ")"
            )
        ).mappings().all()
        for item in collisions:
            expected_table = next(
                table.name
                for table in EventDeliveryBase.metadata.tables.values()
                if item["name"] in {index.name for index in table.indexes}
            )
            if item["type"] != "index" or item["tbl_name"] != expected_table:
                raise RuntimeError(
                    f"incompatible SQLite object named {item['name']}"
                )

        if not present:
            EventDeliveryBase.metadata.create_all(connection)

        _validate_sqlite(connection)


__all__ = ["add_event_delivery_authority"]
