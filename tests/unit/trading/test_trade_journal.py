"""Unit tests for offline trade journal intelligence."""
from __future__ import annotations

from datetime import date

from agicore.trading.trade_journal import (
    analyze_trade_journal,
    load_trade_journal,
    render_trade_journal_markdown,
    save_trade_journal,
)
from agicore.trading.trade_journal_models import (
    JournalEmotion,
    JournalMistakeType,
    JournalTag,
    SessionJournalEntry,
    TradeJournalEntry,
)


def _entry(
    trade_id: str,
    *,
    setup_name: str = "EMA20 pullback",
    emotion_before: JournalEmotion | None = JournalEmotion.CALM,
    emotion_during: JournalEmotion | None = JournalEmotion.FEAR,
    emotion_after: JournalEmotion | None = JournalEmotion.FRUSTRATION,
    mistake_types: tuple[JournalMistakeType, ...] = (),
    tags: tuple[JournalTag, ...] = (),
    screenshot_paths: tuple[str, ...] = ("screenshots/trade.png",),
    notes: str = "",
    followed_playbook: bool = True,
    followed_risk_rules: bool = True,
) -> TradeJournalEntry:
    return TradeJournalEntry(
        trade_id=trade_id,
        session_date=date(2026, 5, 18),
        instrument="NQ",
        direction="LONG",
        setup_name=setup_name,
        entry_reason="Pullback into EMA20 after trend confirmation",
        exit_reason="Target reached",
        emotion_before=emotion_before,
        emotion_during=emotion_during,
        emotion_after=emotion_after,
        mistake_types=mistake_types,
        tags=tags,
        screenshot_paths=screenshot_paths,
        notes=notes,
        followed_playbook=followed_playbook,
        followed_risk_rules=followed_risk_rules,
    )


def test_analyze_trade_journal_detects_counts_compliance_and_review_flags() -> None:
    trades = (
        _entry(
            "T1",
            mistake_types=(JournalMistakeType.FOMO,),
            tags=(JournalTag.PULLBACK, JournalTag.LOSS),
            screenshot_paths=(),
            notes="Fatigue puis tilt apres entree tardive.",
            followed_playbook=False,
        ),
        _entry(
            "T2",
            mistake_types=(JournalMistakeType.FOMO, JournalMistakeType.BROKE_RISK_RULES),
            tags=(JournalTag.PULLBACK, JournalTag.REVIEW),
            notes="Revenge possible apres la perte precedente.",
            followed_risk_rules=False,
        ),
        _entry(
            "T3",
            setup_name="Opening range breakout",
            emotion_before=JournalEmotion.CONFIDENT,
            emotion_during=JournalEmotion.EUPHORIA,
            emotion_after=JournalEmotion.CALM,
            tags=(JournalTag.BREAKOUT, JournalTag.WIN),
        ),
    )
    sessions = (
        SessionJournalEntry(
            session_date=date(2026, 5, 18),
            instrument="NQ",
            dominant_emotion=JournalEmotion.FATIGUE,
            tags=(JournalTag.REVIEW,),
            followed_risk_rules=False,
        ),
    )

    result = analyze_trade_journal(trades, sessions)

    assert result.total_trades == 3
    assert result.total_sessions == 1
    assert ("FOMO", 2) in result.recurring_mistakes
    assert ("EMA20 pullback", 2) in result.most_noted_setups
    assert ("PULLBACK", 2) in result.frequent_tags
    assert result.playbook_compliance_rate == 0.75
    assert result.risk_rules_compliance_rate == 0.5
    assert result.missing_screenshot_trade_ids == ("T1",)
    assert ("T1", "tilt") in result.keyword_flags
    assert ("T1", "fatigue") in result.keyword_flags
    assert ("T2", "revenge") in result.keyword_flags
    assert result.trades_to_review == ("T1", "T2")
    assert any("screenshot" in item for item in result.improvement_plan)


def test_render_trade_journal_markdown_contains_required_sections() -> None:
    result = analyze_trade_journal(
        (
            _entry(
                "T1",
                mistake_types=(JournalMistakeType.MOVED_STOP,),
                tags=(JournalTag.REVIEW,),
                screenshot_paths=(),
                notes="Peur de reperdre le gain latent.",
                followed_risk_rules=False,
            ),
        )
    )

    markdown = render_trade_journal_markdown(result)

    assert "# Trade Journal Intelligence" in markdown
    assert "## Resume journal" in markdown
    assert "## Emotions dominantes" in markdown
    assert "## Erreurs recurrentes" in markdown
    assert "## Respect playbook/risk" in markdown
    assert "## Tags frequents" in markdown
    assert "## Trades a revoir" in markdown
    assert "## Plan d'amelioration" in markdown
    assert "- MOVED_STOP: 1" in markdown
    assert "- T1: peur" in markdown
    assert "- Risk rules: 0.00%" in markdown


def test_trade_journal_json_round_trip(tmp_path) -> None:
    path = tmp_path / "journal.json"
    trades = (
        _entry(
            "T1",
            mistake_types=(JournalMistakeType.EARLY_EXIT,),
            tags=(JournalTag.WIN,),
            screenshot_paths=("screenshots/t1.png", "screenshots/t1-exit.png"),
            notes="Bonne entree, sortie trop rapide.",
        ),
    )
    sessions = (
        SessionJournalEntry(
            session_date=date(2026, 5, 18),
            instrument="NQ",
            dominant_emotion=JournalEmotion.CALM,
            tags=(JournalTag.HIGH_QUALITY,),
            screenshot_paths=("screenshots/session.png",),
            notes="Session propre.",
        ),
    )

    save_trade_journal(path, trades, sessions)
    loaded_trades, loaded_sessions = load_trade_journal(path)

    assert loaded_trades == trades
    assert loaded_sessions == sessions


def test_empty_journal_analysis_is_stable() -> None:
    result = analyze_trade_journal(())

    assert result.total_trades == 0
    assert result.total_sessions == 0
    assert result.playbook_compliance_rate == 1.0
    assert result.risk_rules_compliance_rate == 1.0
    assert result.dominant_emotions == ()
    assert result.trades_to_review == ()
    assert result.improvement_plan == ("Continue journaling every trade with notes and screenshots.",)
