"""Additive migration for the persistent idempotent memory-effect identity."""
from __future__ import annotations

import re
from collections.abc import Mapping

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection

from ..adapters.sqlalchemy_engine import SqlAlchemyEngine

_EFFECT_INDEX = "ux_events_effect_id"
_PAIR_CONSTRAINT = "ck_events_effect_identity_pair"
_SQLITE_INSERT_TRIGGER = "trg_events_effect_identity_insert"
_SQLITE_UPDATE_TRIGGER = "trg_events_effect_identity_update"

_EFFECT_INDEX_DDL = "CREATE UNIQUE INDEX ux_events_effect_id ON events (effect_id)"
_SQLITE_INSERT_TRIGGER_DDL = """
    CREATE TRIGGER trg_events_effect_identity_insert
    BEFORE INSERT ON events
    WHEN (NEW.effect_id IS NULL AND NEW.payload_hash IS NOT NULL)
      OR (NEW.effect_id IS NOT NULL AND NEW.payload_hash IS NULL)
    BEGIN
        SELECT RAISE(ABORT, 'events effect identity pair mismatch');
    END
"""
_SQLITE_UPDATE_TRIGGER_DDL = """
    CREATE TRIGGER trg_events_effect_identity_update
    BEFORE UPDATE OF effect_id, payload_hash ON events
    WHEN (NEW.effect_id IS NULL AND NEW.payload_hash IS NOT NULL)
      OR (NEW.effect_id IS NOT NULL AND NEW.payload_hash IS NULL)
    BEGIN
        SELECT RAISE(ABORT, 'events effect identity pair mismatch');
    END
"""
_POSTGRESQL_PAIR_CONSTRAINT_DDL = (
    "ALTER TABLE events ADD CONSTRAINT ck_events_effect_identity_pair "
    "CHECK ((effect_id IS NULL AND payload_hash IS NULL) OR "
    "(effect_id IS NOT NULL AND payload_hash IS NOT NULL))"
)
_PAIR_TOKEN = re.compile(
    r"\s*(effect_id|payload_hash|is|not|null|and|or|\(|\))",
    re.IGNORECASE,
)


def _columns(connection: Connection) -> Mapping[str, Mapping[str, object]]:
    return {item["name"]: item for item in inspect(connection).get_columns("events")}


def _validate_columns(connection: Connection) -> None:
    columns = _columns(connection)
    for name, minimum_length in (("effect_id", 128), ("payload_hash", 64)):
        column = columns.get(name)
        if column is None or not column.get("nullable", False):
            raise RuntimeError(f"incompatible events.{name} migration column")
        length = getattr(column.get("type"), "length", None)
        if length is not None and length < minimum_length:
            raise RuntimeError(f"events.{name} is shorter than the canonical schema")


def _normalized_sql(definition: str) -> str:
    tokens = re.findall(
        r"'(?:''|[^'])*'|[a-z_][a-z0-9_]*|!=|<>|<=|>=|==|[(),.=;]|\S",
        definition.lower(),
    )
    if tokens and tokens[-1] == ";":
        tokens.pop()
    return " ".join(tokens)


def _sqlite_named_object(
    connection: Connection, name: str
) -> Mapping[str, object] | None:
    return connection.execute(
        text(
            "SELECT type, name, tbl_name, sql FROM sqlite_master "
            "WHERE name = :name"
        ),
        {"name": name},
    ).mappings().one_or_none()


def _validate_sqlite_effect_index(connection: Connection) -> bool:
    rows = connection.exec_driver_sql("PRAGMA index_list('events')").mappings().all()
    index = next((row for row in rows if row["name"] == _EFFECT_INDEX), None)
    named_object = _sqlite_named_object(connection, _EFFECT_INDEX)
    if index is None:
        if named_object is not None:
            raise RuntimeError(f"incompatible SQLite object {_EFFECT_INDEX}")
        return False
    if (
        int(index["unique"]) != 1
        or int(index["partial"]) != 0
        or str(index["origin"]).lower() != "c"
    ):
        raise RuntimeError(f"incompatible SQLite index {_EFFECT_INDEX}")
    if (
        named_object is None
        or named_object["type"] != "index"
        or named_object["tbl_name"] != "events"
        or not isinstance(named_object["sql"], str)
        or _normalized_sql(named_object["sql"])
        != _normalized_sql(_EFFECT_INDEX_DDL)
    ):
        raise RuntimeError(f"incompatible SQLite index {_EFFECT_INDEX}")

    info = connection.exec_driver_sql(
        f'PRAGMA index_info("{_EFFECT_INDEX}")'
    ).mappings().all()
    if (
        len(info) != 1
        or info[0]["name"] != "effect_id"
        or int(info[0]["cid"]) < 0
    ):
        raise RuntimeError(f"incompatible SQLite index {_EFFECT_INDEX}")
    key_columns = [
        row
        for row in connection.exec_driver_sql(
            f'PRAGMA index_xinfo("{_EFFECT_INDEX}")'
        ).mappings()
        if int(row["key"]) == 1
    ]
    if (
        len(key_columns) != 1
        or key_columns[0]["name"] != "effect_id"
        or int(key_columns[0]["cid"]) < 0
        or int(key_columns[0]["desc"]) != 0
        or str(key_columns[0]["coll"]).upper() != "BINARY"
    ):
        raise RuntimeError(f"incompatible SQLite index {_EFFECT_INDEX}")
    return True


def _validate_sqlite_trigger(
    connection: Connection,
    *,
    name: str,
    canonical_ddl: str,
) -> bool:
    trigger = _sqlite_named_object(connection, name)
    if trigger is None:
        return False
    if (
        trigger["type"] != "trigger"
        or trigger["tbl_name"] != "events"
        or not isinstance(trigger["sql"], str)
        or _normalized_sql(trigger["sql"]) != _normalized_sql(canonical_ddl)
    ):
        raise RuntimeError(f"incompatible SQLite trigger {name}")
    return True


def _pair_tokens(expression: str) -> list[str]:
    value = expression.strip()
    if value[:5].lower() == "check":
        value = value[5:].lstrip()
    tokens: list[str] = []
    position = 0
    while position < len(value):
        match = _PAIR_TOKEN.match(value, position)
        if match is None:
            if value[position:].strip():
                raise ValueError("unsupported PostgreSQL check expression")
            break
        tokens.append(match.group(1).lower())
        position = match.end()
    if not tokens:
        raise ValueError("empty PostgreSQL check expression")
    return tokens


def _parse_pair_expression(tokens: list[str]) -> tuple[object, ...]:
    position = 0

    def parse_or() -> tuple[object, ...]:
        nonlocal position
        node = parse_and()
        while position < len(tokens) and tokens[position] == "or":
            position += 1
            node = ("or", node, parse_and())
        return node

    def parse_and() -> tuple[object, ...]:
        nonlocal position
        node = parse_factor()
        while position < len(tokens) and tokens[position] == "and":
            position += 1
            node = ("and", node, parse_factor())
        return node

    def parse_factor() -> tuple[object, ...]:
        nonlocal position
        if position >= len(tokens):
            raise ValueError("incomplete PostgreSQL check expression")
        if tokens[position] == "(":
            position += 1
            node = parse_or()
            if position >= len(tokens) or tokens[position] != ")":
                raise ValueError("unbalanced PostgreSQL check expression")
            position += 1
            return node
        identifier = tokens[position]
        if identifier not in {"effect_id", "payload_hash"}:
            raise ValueError("unexpected PostgreSQL check identifier")
        position += 1
        if position >= len(tokens) or tokens[position] != "is":
            raise ValueError("PostgreSQL check atom must use IS NULL")
        position += 1
        is_not = position < len(tokens) and tokens[position] == "not"
        if is_not:
            position += 1
        if position >= len(tokens) or tokens[position] != "null":
            raise ValueError("PostgreSQL check atom must end with NULL")
        position += 1
        return ("atom", identifier, is_not)

    parsed = parse_or()
    if position != len(tokens):
        raise ValueError("unexpected PostgreSQL check suffix")
    return parsed


def _evaluate_pair_expression(
    node: tuple[object, ...], *, effect_is_null: bool, hash_is_null: bool
) -> bool:
    operator = node[0]
    if operator == "atom":
        value = effect_is_null if node[1] == "effect_id" else hash_is_null
        return not value if node[2] else value
    left = _evaluate_pair_expression(
        node[1], effect_is_null=effect_is_null, hash_is_null=hash_is_null
    )
    right = _evaluate_pair_expression(
        node[2], effect_is_null=effect_is_null, hash_is_null=hash_is_null
    )
    return left and right if operator == "and" else left or right


def _postgresql_pair_expression_is_exact(expression: str) -> bool:
    try:
        parsed = _parse_pair_expression(_pair_tokens(expression))
    except ValueError:
        return False
    for effect_is_null in (False, True):
        for hash_is_null in (False, True):
            actual = _evaluate_pair_expression(
                parsed,
                effect_is_null=effect_is_null,
                hash_is_null=hash_is_null,
            )
            if actual != (effect_is_null == hash_is_null):
                return False
    return True


def _validate_postgresql_effect_index(connection: Connection) -> bool:
    index = connection.execute(
        text("""
            SELECT
                index_meta.indisunique,
                index_meta.indisvalid,
                index_meta.indisready,
                index_meta.indpred IS NULL AS no_predicate,
                index_meta.indexprs IS NULL AS no_expressions,
                index_meta.indnkeyatts,
                index_meta.indnatts,
                attribute.attname AS column_name
            FROM pg_catalog.pg_class AS table_class
            JOIN pg_catalog.pg_index AS index_meta
              ON index_meta.indrelid = table_class.oid
            JOIN pg_catalog.pg_class AS index_class
              ON index_class.oid = index_meta.indexrelid
            LEFT JOIN pg_catalog.pg_attribute AS attribute
              ON attribute.attrelid = table_class.oid
             AND attribute.attnum = index_meta.indkey[0]
            WHERE table_class.oid = pg_catalog.to_regclass('events')
              AND index_class.relname = :name
        """),
        {"name": _EFFECT_INDEX},
    ).mappings().one_or_none()
    if index is None:
        return False
    if not (
        index["indisunique"]
        and index["indisvalid"]
        and index["indisready"]
        and index["no_predicate"]
        and index["no_expressions"]
        and int(index["indnkeyatts"]) == 1
        and int(index["indnatts"]) == 1
        and index["column_name"] == "effect_id"
    ):
        raise RuntimeError(f"incompatible PostgreSQL index {_EFFECT_INDEX}")
    return True


def _validate_postgresql_pair_constraint(connection: Connection) -> bool:
    constraint = connection.execute(
        text("""
            SELECT
                constraint_meta.contype,
                constraint_meta.convalidated,
                pg_catalog.pg_get_expr(
                    constraint_meta.conbin,
                    constraint_meta.conrelid,
                    false
                ) AS expression
            FROM pg_catalog.pg_constraint AS constraint_meta
            WHERE constraint_meta.conrelid = pg_catalog.to_regclass('events')
              AND constraint_meta.conname = :name
        """),
        {"name": _PAIR_CONSTRAINT},
    ).mappings().one_or_none()
    if constraint is None:
        return False
    expression = constraint["expression"]
    if (
        constraint["contype"] != "c"
        or not constraint["convalidated"]
        or not isinstance(expression, str)
        or not _postgresql_pair_expression_is_exact(expression)
    ):
        raise RuntimeError(
            f"incompatible PostgreSQL constraint {_PAIR_CONSTRAINT}"
        )
    return True


def _validate_rows(connection: Connection) -> None:
    mismatches = connection.execute(text(
        "SELECT COUNT(*) FROM events WHERE "
        "(effect_id IS NULL AND payload_hash IS NOT NULL) OR "
        "(effect_id IS NOT NULL AND payload_hash IS NULL)"
    )).scalar_one()
    if mismatches:
        raise RuntimeError("events contains incompatible effect identity pairs")
    duplicates = connection.execute(text(
        "SELECT effect_id FROM events WHERE effect_id IS NOT NULL "
        "GROUP BY effect_id HAVING COUNT(*) > 1"
    )).first()
    if duplicates is not None:
        raise RuntimeError("events contains duplicate effect identities")


def add_idempotent_memory_effect(engine: SqlAlchemyEngine) -> None:
    """Migrate an existing events table without rewriting historical rows."""
    with engine.engine.begin() as connection:
        dialect = connection.dialect.name
        if dialect not in {"sqlite", "postgresql"}:
            raise RuntimeError(f"unsupported idempotent memory backend: {dialect}")
        if "events" not in inspect(connection).get_table_names():
            raise RuntimeError("events table is required before the idempotency migration")

        columns = _columns(connection)
        has_effect_id = "effect_id" in columns
        has_payload_hash = "payload_hash" in columns
        if has_effect_id != has_payload_hash:
            raise RuntimeError("partial idempotent memory-effect migration detected")
        has_identity_columns = has_effect_id and has_payload_hash

        if dialect == "sqlite":
            index_exists = _validate_sqlite_effect_index(connection)
            insert_trigger_exists = _validate_sqlite_trigger(
                connection,
                name=_SQLITE_INSERT_TRIGGER,
                canonical_ddl=_SQLITE_INSERT_TRIGGER_DDL,
            )
            update_trigger_exists = _validate_sqlite_trigger(
                connection,
                name=_SQLITE_UPDATE_TRIGGER,
                canonical_ddl=_SQLITE_UPDATE_TRIGGER_DDL,
            )
            constraint_exists = False
            authorities_exist = (
                index_exists or insert_trigger_exists or update_trigger_exists
            )
        else:
            index_exists = _validate_postgresql_effect_index(connection)
            constraint_exists = _validate_postgresql_pair_constraint(connection)
            insert_trigger_exists = update_trigger_exists = False
            authorities_exist = index_exists or constraint_exists
        if authorities_exist and not has_identity_columns:
            raise RuntimeError("idempotent authorities exist before identity columns")

        if not has_identity_columns:
            connection.execute(text(
                "ALTER TABLE events ADD COLUMN effect_id VARCHAR(128) NULL"
            ))
            connection.execute(text(
                "ALTER TABLE events ADD COLUMN payload_hash VARCHAR(64) NULL"
            ))

        _validate_columns(connection)
        _validate_rows(connection)

        if not index_exists:
            connection.execute(text(_EFFECT_INDEX_DDL))
        if dialect == "sqlite":
            if not insert_trigger_exists:
                connection.execute(text(_SQLITE_INSERT_TRIGGER_DDL))
            if not update_trigger_exists:
                connection.execute(text(_SQLITE_UPDATE_TRIGGER_DDL))
            _validate_sqlite_effect_index(connection)
            _validate_sqlite_trigger(
                connection,
                name=_SQLITE_INSERT_TRIGGER,
                canonical_ddl=_SQLITE_INSERT_TRIGGER_DDL,
            )
            _validate_sqlite_trigger(
                connection,
                name=_SQLITE_UPDATE_TRIGGER,
                canonical_ddl=_SQLITE_UPDATE_TRIGGER_DDL,
            )
        else:
            if not constraint_exists:
                connection.execute(text(_POSTGRESQL_PAIR_CONSTRAINT_DDL))
            _validate_postgresql_effect_index(connection)
            _validate_postgresql_pair_constraint(connection)


__all__ = ["add_idempotent_memory_effect"]
