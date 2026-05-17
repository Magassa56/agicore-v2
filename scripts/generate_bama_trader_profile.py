"""Generate the BAMA trader profile report from a local NinjaTrader CSV export."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import date
from pathlib import Path

from agicore.trading import RiskGuardConfig, analyze_trades, evaluate_risk, import_nt8_csv
from agicore.trading.import_nt8_csv import NormalizedTrade


DATA_PATH = Path("data/NT8_all_trades_2021_2026_APEX.csv")
REPORT_PATH = Path("reports/bama_trader_profile_v1.md")


def main() -> None:
    trades = import_nt8_csv(DATA_PATH)
    stats = analyze_trades(trades)
    profile = _build_profile(trades)

    daily_limit = _suggest_daily_loss_limit(profile["losing_days"])
    max_trades = _suggest_max_trades_per_day(profile["pnl_by_trade_count"])
    risk = evaluate_risk(
        stats,
        RiskGuardConfig(
            destructive_day_loss=-(daily_limit * 2),
            daily_loss_limit=-daily_limit,
            max_trades_per_day=max_trades,
            dangerous_hour_loss=-max(150.0, daily_limit / 2),
            max_consecutive_losses=3,
        ),
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        _render_report(trades, stats, risk, profile, daily_limit, max_trades),
        encoding="utf-8",
    )
    print(f"Report generated: {REPORT_PATH}")


def _build_profile(trades: Sequence[NormalizedTrade]) -> dict[str, object]:
    ordered = sorted(trades, key=lambda trade: trade.exit_time)
    by_day: defaultdict[date, list[NormalizedTrade]] = defaultdict(list)
    by_hour: defaultdict[int, list[NormalizedTrade]] = defaultdict(list)
    for trade in ordered:
        by_day[trade.exit_time.date()].append(trade)
        by_hour[trade.exit_time.hour].append(trade)

    winning = [trade for trade in ordered if trade.pnl > 0]
    losing = [trade for trade in ordered if trade.pnl <= 0]
    loss_streaks = _loss_streaks(ordered)
    day_summaries = {
        day: _trade_group_summary(day_trades) for day, day_trades in sorted(by_day.items())
    }
    losing_days = [summary["pnl"] for summary in day_summaries.values() if summary["pnl"] < 0]
    pnl_by_trade_count: defaultdict[int, list[float]] = defaultdict(list)
    for summary in day_summaries.values():
        pnl_by_trade_count[int(summary["count"])].append(float(summary["pnl"]))

    return {
        "by_day": by_day,
        "by_hour": by_hour,
        "winning": winning,
        "losing": losing,
        "winning_summary": _trade_group_summary(winning),
        "losing_summary": _trade_group_summary(losing),
        "loss_streaks": loss_streaks,
        "day_summaries": day_summaries,
        "losing_days": losing_days,
        "pnl_by_trade_count": pnl_by_trade_count,
    }


def _render_report(
    trades: Sequence[NormalizedTrade],
    stats,
    risk,
    profile: dict[str, object],
    daily_limit: float,
    max_trades: int,
) -> str:
    by_hour = profile["by_hour"]
    by_day = profile["day_summaries"]
    evening = [
        trade
        for trade in trades
        if 18 <= trade.exit_time.hour <= 23
    ]
    destructive_trades = sorted(trades, key=lambda trade: trade.pnl)[:5]
    overtrading_days = [
        (day, summary)
        for day, summary in by_day.items()
        if int(summary["count"]) > max_trades
    ]
    best_trade_counts = _best_trade_counts(profile["pnl_by_trade_count"])

    lines = [
        "# BAMA Trader Profile v1",
        "",
        "Source: `data/NT8_all_trades_2021_2026_APEX.csv`",
        "",
        "## 1. Resume global",
        "",
        f"- PnL total: {_money(stats.total_pnl)}",
        f"- Nombre total de trades: {stats.total_trades}",
        f"- Win rate: {stats.win_rate:.2%}",
        f"- Trade moyen: {_money(stats.average_trade)}",
        f"- Plus gros gain: {_money(stats.largest_gain)}",
        f"- Plus grosse perte: {_money(stats.largest_loss)}",
        f"- MAE moyen: {_optional_money(stats.average_mae)}",
        f"- MFE moyen: {_optional_money(stats.average_mfe)}",
        "",
        "## 2. Analyse temporelle",
        "",
        "### Meilleures heures",
        *_format_hour_groups(by_hour, reverse=True),
        "",
        "### Pires heures",
        *_format_hour_groups(by_hour, reverse=False),
        "",
        "### Meilleures journees",
        *_format_day_groups(by_day, reverse=True),
        "",
        "### Pires journees",
        *_format_day_groups(by_day, reverse=False),
        "",
        "### Heures du soir (18:00-23:59)",
        *_format_group_detail(evening),
        "",
        "## 3. Analyse comportementale",
        "",
        f"- Serie maximale de pertes: {stats.max_consecutive_losses} trades consecutifs",
        f"- Nombre de series de pertes de 3 trades ou plus: {_count_long_loss_streaks(profile['loss_streaks'])}",
        f"- Jours en surtrading (>{max_trades} trades): {len(overtrading_days)}",
        f"- Trades destructeurs identifies: {len([trade for trade in trades if trade.pnl <= stats.largest_loss])} plus bas extreme, avec top 5 ci-dessous",
        "",
        "### Top 5 trades destructeurs",
        *_format_trade_rows(destructive_trades),
        "",
        "### Gagnants vs perdants",
        *_format_winners_losers(profile["winning_summary"], profile["losing_summary"]),
        "",
        "## 4. Analyse Apex",
        "",
        f"- Limite journaliere proposee: stop a -{daily_limit:.0f} $ realise.",
        f"- Nombre optimal de trades: {max_trades} trades maximum par jour.",
        f"- Configurations de taille a surveiller: pertes concentrees sur les trades multi-contrats quand le MAE depasse le MFE.",
        "- Horaires a eviter: " + _format_avoid_hours(risk.worst_hours),
        "- Protection recommandee: arret immediat apres 3 pertes consecutives ou apres une perte unitaire superieure a 50% de la limite journaliere.",
        "- Protection recommandee: pause obligatoire apres un trade perdant dont le MAE est superieur au MFE.",
        "- Protection recommandee: ne pas augmenter la taille pendant une sequence perdante.",
        "",
        "### Lecture par nombre de trades",
        *best_trade_counts,
        "",
        "## 5. Conclusion finale",
        "",
        *_format_conclusion(stats, profile, evening, max_trades),
        "",
    ]
    return "\n".join(lines)


def _trade_group_summary(trades: Sequence[NormalizedTrade]) -> dict[str, float]:
    count = len(trades)
    pnl = sum(trade.pnl for trade in trades)
    wins = sum(1 for trade in trades if trade.pnl > 0)
    durations = [
        (trade.exit_time - trade.entry_time).total_seconds() / 60
        for trade in trades
        if trade.exit_time >= trade.entry_time
    ]
    mae_values = [trade.mae for trade in trades if trade.mae is not None]
    mfe_values = [trade.mfe for trade in trades if trade.mfe is not None]
    return {
        "count": float(count),
        "pnl": pnl,
        "win_rate": (wins / count) if count else 0.0,
        "average": (pnl / count) if count else 0.0,
        "duration": _average(durations),
        "mae": _average(mae_values),
        "mfe": _average(mfe_values),
    }


def _loss_streaks(trades: Sequence[NormalizedTrade]) -> list[int]:
    streaks: list[int] = []
    current = 0
    for trade in trades:
        if trade.pnl <= 0:
            current += 1
            continue
        if current:
            streaks.append(current)
            current = 0
    if current:
        streaks.append(current)
    return streaks


def _suggest_daily_loss_limit(losing_days: Sequence[float]) -> float:
    if not losing_days:
        return 300.0
    average_losing_day = abs(sum(losing_days) / len(losing_days))
    return max(300.0, round(average_losing_day / 100) * 100)


def _suggest_max_trades_per_day(pnl_by_trade_count: dict[int, list[float]]) -> int:
    profitable_counts = [
        count
        for count, pnls in pnl_by_trade_count.items()
        if pnls and sum(pnls) / len(pnls) > 0
    ]
    if profitable_counts:
        return max(3, min(max(profitable_counts), 10))
    return 5


def _best_trade_counts(pnl_by_trade_count: dict[int, list[float]]) -> list[str]:
    rows = []
    for count, pnls in sorted(pnl_by_trade_count.items()):
        rows.append((count, len(pnls), sum(pnls), sum(pnls) / len(pnls)))
    rows = sorted(rows, key=lambda row: row[3], reverse=True)[:5]
    if not rows:
        return ["- Donnees insuffisantes."]
    return [
        f"- {count} trades/jour: {days} jour(s), PnL total {_money(total)}, moyenne/jour {_money(avg)}"
        for count, days, total, avg in rows
    ]


def _format_hour_groups(by_hour: dict[int, list[NormalizedTrade]], *, reverse: bool) -> list[str]:
    rows = []
    for hour, trades in by_hour.items():
        summary = _trade_group_summary(trades)
        rows.append((hour, summary))
    rows = sorted(rows, key=lambda row: row[1]["pnl"], reverse=reverse)[:5]
    return [
        f"- {hour:02d}:00: PnL {_money(summary['pnl'])}, trades {summary['count']:.0f}, win rate {summary['win_rate']:.2%}, moyenne {_money(summary['average'])}"
        for hour, summary in rows
    ] or ["- Aucune donnee."]


def _format_day_groups(by_day: dict[date, dict[str, float]], *, reverse: bool) -> list[str]:
    rows = sorted(by_day.items(), key=lambda row: row[1]["pnl"], reverse=reverse)[:5]
    return [
        f"- {day.isoformat()}: PnL {_money(summary['pnl'])}, trades {summary['count']:.0f}, win rate {summary['win_rate']:.2%}, moyenne {_money(summary['average'])}"
        for day, summary in rows
    ] or ["- Aucune donnee."]


def _format_group_detail(trades: Sequence[NormalizedTrade]) -> list[str]:
    summary = _trade_group_summary(trades)
    return [
        f"- Trades: {summary['count']:.0f}",
        f"- PnL: {_money(summary['pnl'])}",
        f"- Win rate: {summary['win_rate']:.2%}",
        f"- Trade moyen: {_money(summary['average'])}",
        f"- Duree moyenne: {_minutes(summary['duration'])}",
    ]


def _format_trade_rows(trades: Sequence[NormalizedTrade]) -> list[str]:
    return [
        f"- {trade.exit_time:%Y-%m-%d %H:%M:%S}: {_money(trade.pnl)}, qty {_optional_number(trade.quantity)}, MAE {_optional_money(trade.mae)}, MFE {_optional_money(trade.mfe)}"
        for trade in trades
    ] or ["- Aucune donnee."]


def _format_winners_losers(winning: dict[str, float], losing: dict[str, float]) -> list[str]:
    return [
        f"- Trades gagnants: {winning['count']:.0f}, moyenne {_money(winning['average'])}, duree moyenne {_minutes(winning['duration'])}, MAE {_optional_money(winning['mae'])}, MFE {_optional_money(winning['mfe'])}",
        f"- Trades perdants: {losing['count']:.0f}, moyenne {_money(losing['average'])}, duree moyenne {_minutes(losing['duration'])}, MAE {_optional_money(losing['mae'])}, MFE {_optional_money(losing['mfe'])}",
    ]


def _format_conclusion(
    stats,
    profile: dict[str, object],
    evening: Sequence[NormalizedTrade],
    max_trades: int,
) -> list[str]:
    losing = profile["losing_summary"]
    winning = profile["winning_summary"]
    evening_summary = _trade_group_summary(evening)
    style = "scalping tres court terme" if max(winning["duration"], losing["duration"]) < 5 else "intraday court terme"
    risk_bias = "negatif" if stats.total_pnl < 0 else "positif"
    return [
        f"- Profil trader: win rate eleve ({stats.win_rate:.2%}) mais expectancy {risk_bias} avec un trade moyen de {_money(stats.average_trade)}.",
        f"- Style detecte: {style}, avec duree moyenne gagnants {_minutes(winning['duration'])} et perdants {_minutes(losing['duration'])}.",
        f"- Principaux risques: pertes unitaires lourdes, sequences de pertes jusqu'a {stats.max_consecutive_losses}, et degradation possible lors des sessions du soir (PnL soir {_money(evening_summary['pnl'])}).",
        "- Points forts: capacite a generer plus de trades gagnants que perdants et presence de gains unitaires significatifs.",
        f"- Priorite operationnelle: reduire la taille ou arreter la session avant le trade {max_trades + 1}, puis verrouiller le stop journalier propose.",
    ]


def _format_avoid_hours(hours: Sequence[int]) -> str:
    if not hours:
        return "aucune heure bloquee automatiquement; surveiller les pires heures listees plus haut."
    return ", ".join(f"{hour:02d}:00" for hour in hours)


def _count_long_loss_streaks(streaks: Iterable[int]) -> int:
    return sum(1 for streak in streaks if streak >= 3)


def _average(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _money(value: float) -> str:
    return f"{value:.2f} $"


def _optional_money(value: float | None) -> str:
    return "n/a" if value is None else _money(value)


def _optional_number(value: float | None) -> str:
    return "n/a" if value is None else f"{value:g}"


def _minutes(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f} min"


if __name__ == "__main__":
    main()
