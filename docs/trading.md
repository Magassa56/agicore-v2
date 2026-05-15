# Trading — domaine d'exécution AGIcore-v2

> Couche concernée : L5 (Action) avec dépendances vers L3 (décision) et L4 (orchestration).

---

## 1. Plateforme et marchés

| Élément | Détail |
|---|---|
| Plateforme d'exécution | NinjaTrader 8 |
| Marchés | Futures, Forex, Crypto |
| Connector | `ninjatrader_connector.py` (L5) |

---

## 2. Stratégies

| Stratégie | Module | Statut |
|---|---|---|
| EMA crossover | `strategy_ema_rsi.py` | prioritaire |
| RSI divergence | `strategy_ema_rsi.py` | prioritaire |
| Momentum | à créer | backlog |

Toute nouvelle stratégie doit :
- exposer une interface `Strategy` commune (méthodes `on_bar`, `signal`, `params`)
- être backtestable via `backtesting_engine.py`
- être testée par pytest avec au minimum 3 jeux de données de référence

---

## 3. Gestion du risque (`risk_manager.py`)

Les limites suivantes sont des **règles dures**, non négociables sans validation J'ai :

| Paramètre | Valeur |
|---|---|
| Max drawdown par trade | 2 % |
| Max drawdown journalier | 6 % |
| Sizing | Kelly fractionnel si pertinent, sinon fixe |
| Stop loss | obligatoire sur chaque ordre |
| Position concurrente max | défini par stratégie, plafonné par risk_manager |

Le `risk_manager` est un **gatekeeper** : aucun ordre ne part en L5 sans son OK.

---

## 4. Données

| Format | Granularité | Source |
|---|---|---|
| OHLCV | 1m, 5m, 1h | NinjaTrader / data feed |
| Tick data | si disponible | NinjaTrader |

Les données historiques utilisées pour backtest doivent être versionnées (hash + date d'extraction) pour assurer la reproductibilité.

---

## 5. Backtesting

`backtesting_engine.py` doit supporter :

- **Walk-forward** : entraînement sur fenêtre glissante, test sur fenêtre suivante
- **Out-of-sample validation** : split temporel strict (jamais de leak)
- **Métriques minimales** : Sharpe, Sortino, max drawdown, win rate, profit factor, expectancy
- **Slippage et frais** : modélisés explicitement (ne jamais backtest "pur")

Aucune stratégie ne passe en production sans validation walk-forward + out-of-sample.

---

## 6. Logging et reporting

| Module | Rôle |
|---|---|
| `trade_logger.py` | journalisation de chaque ordre (entrée, sortie, PnL, contexte) |
| `performance_reporter.py` | agrégation périodique (jour, semaine, mois) |

Chaque trade enregistré porte : `trade_id`, `agent_id`, `strategy_id`, `signal_origin`, `risk_check_passed`, `timestamp_utc`.

---

## 7. Librairies recommandées

- `pandas` — data manipulation
- `numpy` — calculs vectorisés
- `ta-lib` ou `pandas-ta` — indicateurs techniques
- `backtrader` (optionnel) ou moteur custom dans `backtesting_engine.py`

Préférer un moteur custom léger plutôt qu'une grosse dépendance, sauf raison forte.

---

## 8. Workflow d'ajout d'une stratégie

1. Créer branche `feature/strategy-<nom>`
2. Implémenter dans `src/agicore/l5_action/strategy_<nom>.py`
3. Ajouter tests pytest dans `tests/unit/test_strategy_<nom>.py`
4. Backtester walk-forward + out-of-sample
5. Documenter résultats dans `docs/strategies/<nom>.md`
6. PR vers `main` avec validation J'ai
