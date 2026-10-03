# EMA_PULLBACK_V2_REGIME_GATED — charte de recherche

Date de décision : 2026-10-03 UTC. Statut : `PRE_FORMALIZATION`.
`EMA_PULLBACK_V2_REGIME_GATED = PRE_FORMALIZATION`.

## Clôture de la voie V1

Décision du propriétaire : `EMA_PULLBACK_V1_PATH = TERMINATED`. V1 reste
`NO_GO_BASELINE`, V1A et V1B restent `NO_GO_VARIANT`. La réplication V1B sur le contrat
MNQ 03-26 reste `NO_GO_VARIANT` et son issue préengagée est
`STOP_INCREMENTAL_EMA_PULLBACK_V1_PATH`. Aucune V1C n'est créée. Les règles, seuils,
résultats et verdicts enregistrés ne changent pas.

| Pièce figée | SHA-256 |
| --- | --- |
| Résultat V1 MNQ 06-26 | `4351d82e2b965b75843b0e24545358c80e2dc544a0549d085ceb8e93f4ceb3f6` |
| Résultat V1A MNQ 06-26 | `29eef4a574fc46aab07a5ab60fc0c09fe111c3e72acc6d91ae3e5f04450582de` |
| Résultat V1B MNQ 06-26 | `d3b188c8efed50fc418dab25941b9237261bf39cb88a259c371d7e65e4a0e41b` |
| Réplication V1B MNQ 03-26 | `968f934c46969c3978575aa96b7e98f015958c731c6ed73a543ebe3a9b8372b6` |
| Module de stratégie V1 | `af9d9159262e6c027afada5d4faf1aa6374cf696c234ed1de554801d477dcac9` |
| Module de stratégie V1A | `9f8b88f5b5f476b9f00a7f096e5b74d4eda79771fbce03e166cea699d0305f59` |
| Module de stratégie V1B | `c61703033504539cda5067798c5b38832f406484e069228c9b6e3eb0533ee717` |

## Hypothèse et périmètre V2

`STRATEGY_FAMILY = EMA_PULLBACK_V2_REGIME_GATED`

> EMA pullbacks may have positive expectancy only when preceded by a measurable
> market-regime transition or directional impulse. The V1 instability may come
> from treating all EMA20 pullbacks as equivalent regardless of context.

V2 est un **nouveau programme de recherche**, sans signal de trading défini et sans
backtest autorisé à cette étape. Seuls les composants d'infrastructure validés
peuvent être réutilisés : replay déterministe, décisions causales à la clôture,
exécution au plus tôt sur la barre suivante, modèle de coûts et slippage, contrôles
de filiation, scellement OOS, reporting et gouvernance fail-closed. Les règles
d'entrée V1, les seuils V1 et les résultats V1 ne définissent aucun paramètre V2.
L'architecture de sortie et de risque V2 doit être décidée explicitement ; le Risk
Engine demeure une frontière obligatoire du projet.

La première mission est le contrat déterministe `REGIME_CONTEXT_V2`, composé des
familles de variables suivantes. La présence d'une famille dans la charte ne fixe
ni son prédicat ni son seuil :

1. `IMPULSE / REVERSAL EVENT` : étendue de bougie relative à l'étendue récente,
   relation mèche/corps et volume relatif ;
2. `MOMENTUM TRANSITION` : direction/croisement MACD et représentation éventuelle
   d'une divergence ;
3. `TREND ACCEPTANCE` : franchissement ou reprise d'EMA20, direction établie
   d'EMA20, puis pullback après qualification du contexte.

Avant toute nouvelle lecture de performance : figer prédicats exacts, warmup,
ordre des événements, invalidation, durée de validité du signal, politique à une
position, architecture de sortie et architecture de risque. Ensuite seulement,
qualifier un **nouveau dataset DEVELOPMENT** avec sa propre filiation. Les contrats
MNQ 06-26 et MNQ 03-26 déjà exploités pour V1 ne servent pas à choisir des
paramètres V2. L'OOS reste scellé.

## Composition des événements — décision du propriétaire

Le 2026-10-03, la gate `REGIME_CONTEXT_V2_EVENT_COMPOSITION_REQUIRED` a été
acquittée par la règle architecturale
`REGIME_CONTEXT_V2_EVENT_COMPOSITION = IMPULSE_OR_REVERSAL_DISTINCT`.

`DIRECTIONAL_IMPULSE_EVENT` signifie accélération et acceptation fortes dans une
direction déjà émergente. `REVERSAL_TRANSITION_EVENT` signifie rejet ou épuisement
suivi d'une transition vers la direction opposée. Les deux prédicats restent
indépendants : aucun score générique ne les fusionne. Chaque événement qualifié
porte `event_type`, `event_direction = LONG | SHORT`, `event_bar_index` et
`event_timestamp` (UTC). La composition porte sur la même barre clôturée et
refuse toute métadonnée incohérente ou provenant d'une barre ultérieure.

| Événements sur la barre clôturée | Contexte | Direction | Étiquettes conservées |
| --- | --- | --- | --- |
| Aucun | `UNQUALIFIED` | Aucune | Aucune |
| Impulsion seule ou retournement seul | `QUALIFIED` | Celle de l'événement | Une |
| Les deux, même direction | `QUALIFIED` | Direction commune | Les deux |
| Les deux, directions opposées | `AMBIGUOUS` | Aucune | Les deux ; aucune entrée |

La qualification du contexte est l'OR des événements indépendants, sous réserve
de la collision opposée. Aucun événement n'a priorité sur l'autre. Un contexte
qualifié n'est pas encore un signal d'entrée. L'ordre prévu est : contexte,
transition momentum, acceptation EMA20, pullback, puis entrée ; les prédicats
intermédiaires restent à définir.

Aucun seuil numérique de volume, d'étendue de bougie, de ratio de mèche, d'ATR
ou de magnitude MACD n'est fixé. Aucun replay ni choix de paramètre à partir des
contrats MNQ 03-26 ou MNQ 06-26 n'est autorisé.

## Direction émergente avant l'impulsion — décision du propriétaire

Le 2026-10-03, `DIRECTIONAL_IMPULSE_EVENT_EMERGING_DIRECTION_REQUIRED` a été
acquittée. Le prérequis structurel non optimisé porte exclusivement sur trois
bougies **clôturées** : `t-3`, `t-2` et `t-1`. La direction est connue dès
`Close[t-1]` ; la bougie candidate `t` ne contribue jamais à ce calcul et un
événement d'impulsion éventuel ne pourra être évalué qu'à `Close[t]`.

| Direction | Clôtures des trois bougies | Extrêmes des trois bougies |
| --- | --- | --- |
| `LONG` | `Close[t-3] < Close[t-2] < Close[t-1]` | `Low[t-3] <= Low[t-2] <= Low[t-1]` |
| `SHORT` | `Close[t-3] > Close[t-2] > Close[t-1]` | `High[t-3] >= High[t-2] >= High[t-1]` |

Une égalité entre clôtures ou la rupture de l'ordre des extrêmes donne
`emerging_direction = NONE` après évaluation. L'égalité entre lows LONG ou entre
highs SHORT est autorisée. Si l'une des trois bougies requises manque ou que
`t < 3`, le statut est `INSUFFICIENT_WARMUP` et la direction est `NONE`. Des
barres préalables non clôturées ou dont les métadonnées sont incohérentes sont
refusées. Le calcul est pur et ne lit ni la bougie `t` ni les suivantes.

Le sous-contrat est dans `src/agicore/trading/directional_impulse_v2.py` ; il ne
produit aucun `DIRECTIONAL_IMPULSE_EVENT`, signal d'entrée ou décision d'ordre.
EMA20, MACD, ATR, volume, seuil d'étendue ou de mèche et filtre de session ne
participent pas à cette direction émergente. Aucun résultat de V1/V1A/V1B n'a
servi à choisir ce prédicat. L'événement de retournement garde son prédicat
distinct, encore à définir.

## Prochaine ambiguïté — événement d'impulsion

`BLOCKED_HUMAN_GATE — DIRECTIONAL_IMPULSE_EVENT_RANGE_PREDICATE_REQUIRED`

L'accélération ou l'acceptation forte sur la bougie candidate `t` n'a pas encore
de prédicat d'étendue défini. **Décision humaine unique demandée :** quelle
règle causale exacte de range (mesure de `t`, référence sur bougies antérieures,
fenêtre et seuil de comparaison) doit qualifier la composante d'amplitude de
`DIRECTIONAL_IMPULSE_EVENT` ? Le volume et les mèches feront l'objet de gates
distinctes. Aucun replay ni OOS avant la formalisation complète.
