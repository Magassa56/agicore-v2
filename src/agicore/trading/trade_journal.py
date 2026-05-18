"""Offline trade journal intelligence for AGIcore Trading."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, is_dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from .trade_journal_models import (
    JournalAnalysisResult,
    JournalEmotion,
    JournalMistakeType,
    JournalTag,
    SessionJournalEntry,
    TradeJournalEntry,
)

_JOURNAL_KEYWORDS = {
    "tilt": ("tilt",),
    "fatigue": ("fatigue", "fatiguee", "fatigued"),
    "revenge": ("revenge", "vengeance"),
    "peur": ("peur", "fear"),
    "euphorie": ("euphorie", "euphoria"),
}


def analyze_trade_journal(
    trade_entries: Iterable[TradeJournalEntry],
    session_entries: Iterable[SessionJournalEntry] = (),
) -> JournalAnalysisResult:
    """Analyze a manual trade journal using deterministic offline heuristics."""
    trades = tuple(trade_entries)
    sessions = tuple(session_entries)

    emotion_counts: Counter[str] = Counter()
    mistake_counts: Counter[str] = Counter()
    setup_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()
    missing_screenshots: list[str] = []
    keyword_flags: list[tuple[str, str]] = []
    review_ids: set[str] = set()

    for trade in trades:
        for emotion in (trade.emotion_before, trade.emotion_during, trade.emotion_after):
            if emotion is not None:
                emotion_counts[_enum_value(emotion)] += 1
        for mistake in trade.mistake_types:
            mistake_counts[_enum_value(mistake)] += 1
            review_ids.add(trade.trade_id)
        if trade.setup_name.strip():
            setup_counts[trade.setup_name.strip()] += 1
        for tag in trade.tags:
            tag_counts[_enum_value(tag)] += 1
        if not trade.screenshot_paths:
            missing_screenshots.append(trade.trade_id)
            review_ids.add(trade.trade_id)
        if not trade.followed_playbook or not trade.followed_risk_rules:
            review_ids.add(trade.trade_id)
        for keyword in _detect_note_keywords(trade.notes):
            keyword_flags.append((trade.trade_id, keyword))
            review_ids.add(trade.trade_id)

    for session in sessions:
        if session.dominant_emotion is not None:
            emotion_counts[_enum_value(session.dominant_emotion)] += 1
        for tag in session.tags:
            tag_counts[_enum_value(tag)] += 1

    playbook_rate = _compliance_rate(
        [trade.followed_playbook for trade in trades]
        + [session.followed_playbook for session in sessions]
    )
    risk_rate = _compliance_rate(
        [trade.followed_risk_rules for trade in trades]
        + [session.followed_risk_rules for session in sessions]
    )

    result = JournalAnalysisResult(
        total_trades=len(trades),
        total_sessions=len(sessions),
        dominant_emotions=_ranked(emotion_counts),
        recurring_mistakes=_ranked(mistake_counts),
        most_noted_setups=_ranked(setup_counts),
        frequent_tags=_ranked(tag_counts),
        playbook_compliance_rate=playbook_rate,
        risk_rules_compliance_rate=risk_rate,
        missing_screenshot_trade_ids=tuple(missing_screenshots),
        keyword_flags=tuple(keyword_flags),
        trades_to_review=tuple(sorted(review_ids)),
        improvement_plan=_build_improvement_plan(
            mistake_counts=mistake_counts,
            keyword_flags=keyword_flags,
            playbook_rate=playbook_rate,
            risk_rate=risk_rate,
            missing_screenshots=missing_screenshots,
        ),
    )
    return result


def render_trade_journal_markdown(result: JournalAnalysisResult) -> str:
    """Render a Markdown report from a journal analysis result."""
    lines = [
        "# Trade Journal Intelligence",
        "",
        "## Resume journal",
        "",
        f"- Trades journalises: {result.total_trades}",
        f"- Sessions journalisees: {result.total_sessions}",
        f"- Trades a revoir: {len(result.trades_to_review)}",
        "",
        "## Emotions dominantes",
        "",
        *_counter_lines(result.dominant_emotions),
        "",
        "## Erreurs recurrentes",
        "",
        *_counter_lines(result.recurring_mistakes),
        "",
        "## Respect playbook/risk",
        "",
        f"- Playbook: {result.playbook_compliance_rate:.2%}",
        f"- Risk rules: {result.risk_rules_compliance_rate:.2%}",
        "",
        "## Tags frequents",
        "",
        *_counter_lines(result.frequent_tags),
        "",
        "## Trades a revoir",
        "",
        *_bullet_lines(result.trades_to_review),
        "",
        "## Captures manquantes",
        "",
        *_bullet_lines(result.missing_screenshot_trade_ids),
        "",
        "## Mots-cles detectes",
        "",
        *_keyword_lines(result.keyword_flags),
        "",
        "## Plan d'amelioration",
        "",
        *_bullet_lines(result.improvement_plan),
        "",
    ]
    return "\n".join(lines)


def save_trade_journal(
    path: str | Path,
    trade_entries: Iterable[TradeJournalEntry],
    session_entries: Iterable[SessionJournalEntry] = (),
) -> None:
    """Save journal entries as simple JSON without external services."""
    payload = {
        "trade_entries": [_to_jsonable(entry) for entry in trade_entries],
        "session_entries": [_to_jsonable(entry) for entry in session_entries],
    }
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_trade_journal(path: str | Path) -> tuple[tuple[TradeJournalEntry, ...], tuple[SessionJournalEntry, ...]]:
    """Load journal entries previously saved with save_trade_journal."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    trades = tuple(_trade_from_dict(item) for item in payload.get("trade_entries", ()))
    sessions = tuple(_session_from_dict(item) for item in payload.get("session_entries", ()))
    return trades, sessions


def _build_improvement_plan(
    *,
    mistake_counts: Counter[str],
    keyword_flags: list[tuple[str, str]],
    playbook_rate: float,
    risk_rate: float,
    missing_screenshots: list[str],
) -> tuple[str, ...]:
    actions: list[str] = []
    if playbook_rate < 1.0:
        actions.append("Review entry checklist before each trade and mark playbook compliance.")
    if risk_rate < 1.0:
        actions.append("Block new entries after any risk rule breach until post-trade review is done.")
    if mistake_counts:
        mistake = mistake_counts.most_common(1)[0][0]
        actions.append(f"Focus next session review on the recurring mistake: {mistake}.")
    if keyword_flags:
        actions.append("Add a mandatory pause when notes mention tilt, fatigue, revenge, peur or euphorie.")
    if missing_screenshots:
        actions.append("Attach a screenshot reference to every reviewed trade.")
    return tuple(dict.fromkeys(actions or ["Continue journaling every trade with notes and screenshots."]))


def _detect_note_keywords(notes: str) -> tuple[str, ...]:
    normalized = notes.casefold()
    detected = [
        label
        for label, variants in _JOURNAL_KEYWORDS.items()
        if any(variant in normalized for variant in variants)
    ]
    return tuple(detected)


def _compliance_rate(values: list[bool]) -> float:
    if not values:
        return 1.0
    return sum(1 for value in values if value) / len(values)


def _ranked(counter: Counter[str]) -> tuple[tuple[str, int], ...]:
    return tuple(counter.most_common())


def _counter_lines(values: tuple[tuple[str, int], ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {name}: {count}" for name, count in values]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _keyword_lines(values: tuple[tuple[str, str], ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {trade_id}: {keyword}" for trade_id, keyword in values]


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _to_jsonable(entry: Any) -> dict[str, Any]:
    if not is_dataclass(entry):
        raise TypeError(f"Unsupported journal entry: {type(entry)!r}")
    payload = asdict(entry)
    for key, value in tuple(payload.items()):
        if isinstance(value, date):
            payload[key] = value.isoformat()
        elif isinstance(value, tuple):
            payload[key] = [_json_scalar(item) for item in value]
        else:
            payload[key] = _json_scalar(value)
    return payload


def _json_scalar(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    return value


def _trade_from_dict(payload: dict[str, Any]) -> TradeJournalEntry:
    return TradeJournalEntry(
        trade_id=str(payload["trade_id"]),
        session_date=date.fromisoformat(payload["session_date"]),
        instrument=str(payload["instrument"]),
        direction=str(payload["direction"]),
        setup_name=str(payload["setup_name"]),
        entry_reason=str(payload["entry_reason"]),
        exit_reason=str(payload["exit_reason"]),
        emotion_before=_optional_enum(JournalEmotion, payload.get("emotion_before")),
        emotion_during=_optional_enum(JournalEmotion, payload.get("emotion_during")),
        emotion_after=_optional_enum(JournalEmotion, payload.get("emotion_after")),
        mistake_types=tuple(JournalMistakeType(item) for item in payload.get("mistake_types", ())),
        tags=tuple(JournalTag(item) for item in payload.get("tags", ())),
        screenshot_paths=tuple(str(item) for item in payload.get("screenshot_paths", ())),
        notes=str(payload.get("notes", "")),
        followed_playbook=bool(payload.get("followed_playbook", True)),
        followed_risk_rules=bool(payload.get("followed_risk_rules", True)),
    )


def _session_from_dict(payload: dict[str, Any]) -> SessionJournalEntry:
    return SessionJournalEntry(
        session_date=date.fromisoformat(payload["session_date"]),
        instrument=str(payload.get("instrument", "")),
        dominant_emotion=_optional_enum(JournalEmotion, payload.get("dominant_emotion")),
        tags=tuple(JournalTag(item) for item in payload.get("tags", ())),
        screenshot_paths=tuple(str(item) for item in payload.get("screenshot_paths", ())),
        notes=str(payload.get("notes", "")),
        followed_playbook=bool(payload.get("followed_playbook", True)),
        followed_risk_rules=bool(payload.get("followed_risk_rules", True)),
    )


def _optional_enum(enum_type: type[JournalEmotion], value: str | None) -> JournalEmotion | None:
    if value is None:
        return None
    return enum_type(value)


__all__ = [
    "analyze_trade_journal",
    "load_trade_journal",
    "render_trade_journal_markdown",
    "save_trade_journal",
]
