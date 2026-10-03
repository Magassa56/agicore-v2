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

Les seuils d'étendue et de volume sont désormais fixés dans leurs sous-contrats
ci-dessous ; aucun ratio de mèche, ATR ou magnitude MACD n'est fixé. Aucun
replay ni choix de paramètre à partir des contrats MNQ 03-26 ou MNQ 06-26 n'est
autorisé.

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

## Range de la bougie candidate — décision du propriétaire

Le 2026-10-03, `DIRECTIONAL_IMPULSE_EVENT_RANGE_PREDICATE_REQUIRED` a été
acquittée. Ce sous-contrat indépendant de LONG/SHORT est figé **avant tout
replay**, sans optimisation ni recours aux résultats V1/V1A/V1B :

```text
RANGE_MEASURE = HIGH_LOW
RANGE_REFERENCE = MEDIAN_PRIOR_20_CLOSED_BARS
RANGE_MULTIPLIER = Decimal("1.50")
range_t = High[t] - Low[t]
prior_ranges = [High[i] - Low[i] for i in t-20 ... t-1]
reference_range = exact_median(prior_ranges)
range_qualified = range_t >= Decimal("1.50") * reference_range
```

La médiane des 20 étendues triées est la moyenne exacte des valeurs centrales
10 et 11. L'égalité avec le seuil qualifie le range ; une valeur strictement
inférieure échoue, sans arrondi préalable. `t` doit être clôturée. Moins de 20
bougies antérieures clôturées donne `INSUFFICIENT_WARMUP` et
`range_qualified = false`. Une médiane nulle ou négative donne
`INVALID_REFERENCE_RANGE` et `range_qualified = false`. Une source incohérente
est refusée. Aucune barre future n'est consultée et `t` ne participe pas à la
référence. Seules `t` et les 20 bougies précédentes sont nécessaires.

Le module `src/agicore/trading/directional_impulse_v2.py` calcule ce sous-prédicat
avec des `Decimal` exacts. Il ne combine pas encore le range avec la direction
émergente et n'émet ni `DIRECTIONAL_IMPULSE_EVENT` ni signal d'entrée. ATR,
True Range, corps/mèche, direction de bougie, volume, EMA20, MACD et filtre de
session ne participent pas au prédicat de range.

## Volume de la bougie candidate — décision du propriétaire

Le 2026-10-03, `DIRECTIONAL_IMPULSE_EVENT_VOLUME_PREDICATE_REQUIRED` a été
acquittée. La baseline est choisie avant tout replay, non optimisée et non
dérivée des résultats V1/V1A/V1B :

```text
VOLUME_MEASURE = BAR_TRADE_VOLUME
VOLUME_REFERENCE = MEDIAN_PRIOR_20_CLOSED_BARS
VOLUME_MULTIPLIER = Decimal("1.50")
volume_t = Volume[t]
prior_volumes = [Volume[i] for i in t-20 ... t-1]
reference_volume = exact_median(prior_volumes)
volume_qualified = volume_t >= Decimal("1.50") * reference_volume
```

La médiane des 20 volumes triés est la moyenne arithmétique exacte des valeurs
centrales 10 et 11. L'égalité qualifie ; toute valeur strictement inférieure
échoue. Les entiers et `Decimal` finis sont conservés exactement, sans conversion
float ni arrondi avant comparaison, même si la précision Decimal ambiante est
réduite. Le volume est le volume de transactions agrégé d'une barre **Last d'une
minute**. `TradeVolumeBarV2` exige explicitement cette mesure, l'intervalle et
le type Last ; aucun volume Bid/Ask, delta, tick count ou déséquilibre de carnet
ne peut être substitué. Ces métadonnées d'entrée ne prouvent pas la filiation
d'un dataset, qui reste un contrôle séparé.

| Condition | Statut | Qualification |
| --- | --- | --- |
| Moins de 20 bougies antérieures clôturées | `INSUFFICIENT_WARMUP` | `false` |
| Volume de `t` absent ou invalide | `INVALID_CANDIDATE_VOLUME` | `false` |
| Volume d'une référence absent ou invalide | `INVALID_REFERENCE_VOLUME` | `false` |
| Un volume sélectionné est négatif | `INVALID_VOLUME` | `false` |
| Médiane de référence <= 0 | `INVALID_REFERENCE_VOLUME` | `false` |
| Volumes valides et médiane positive | `EVALUATED` | Comparaison inclusive |

La barre candidate doit exister et être clôturée. Index, types de source ou
timestamps incohérents sont refusés. Une barre absente dans l'historique constitue
un warmup insuffisant ; une barre présente mais sans volume constitue une
référence invalide. En cas de défauts simultanés, le prérequis d'historique clôturé
est contrôlé d'abord ; sur une fenêtre complète, tout volume négatif prime, puis
le défaut candidat, puis le défaut de référence. Tous ces cas restent non qualifiés.

Seules `t` et `t-20 ... t-1` sont lues. La référence exclut `t` ; les observations
plus anciennes ou futures n'affectent pas le résultat. Le prédicat ne contient
aucune direction LONG/SHORT : celle-ci vient exclusivement de
`DIRECTIONAL_IMPULSE_EMERGING_DIRECTION`. Aucun volume moyen mobile, z-score,
normalisation horaire, cumul, delta, footprint, order flow, ratio corps/mèche,
EMA20, MACD ou filtre de session n'est ajouté.

Le sous-prédicat pur est dans `src/agicore/trading/directional_impulse_v2.py`.
Les trois sous-prédicats direction/range/volume ne sont pas encore assemblés
en événement d'impulsion ou signal d'entrée. Les tests sont uniquement
synthétiques ; aucun replay, accès OOS ou ajustement sur MNQ 03-26/06-26.

## Corps et mèches de la candidate — décision du propriétaire

Le 2026-10-03, `DIRECTIONAL_IMPULSE_EVENT_BODY_WICK_PREDICATE_REQUIRED` est
acquittée. `MIN_BODY_TO_RANGE_RATIO = Decimal("0.60")` et
`MAX_TERMINAL_WICK_TO_RANGE_RATIO = Decimal("0.20")` sont des baselines
pré-replay, non optimisées, sans dérivation des résultats V1/V1A/V1B.
Aucun seuil ne sera ajusté après observation de performance.

```text
range_t = High[t] - Low[t]
body_t = abs(Close[t] - Open[t])
upper_wick_t = High[t] - max(Open[t], Close[t])
lower_wick_t = min(Open[t], Close[t])
LONG = emerging_direction == LONG AND Close[t] > Open[t]
       AND body_t >= Decimal("0.60") * range_t
       AND upper_wick_t <= Decimal("0.20") * range_t
SHORT = emerging_direction == SHORT AND Close[t] < Open[t]
        AND body_t >= Decimal("0.60") * range_t
        AND lower_wick_t <= Decimal("0.20") * range_t
```

La candidate `t` doit être clôturée ; elle seule est consultée par ce
sous-prédicat. OHLC finis Decimal et cohérents requis : High >= max(Open, Close),
Low <= min(Open, Close), High >= Low. Sinon `INVALID_OHLC`, qualification fausse.
Après cette validation, range <= 0 donne `INVALID_CANDIDATE_RANGE`, qualification
fausse. Aucune direction émergente donne une qualification fausse ; le corps
n'infère jamais une direction. Les métadonnées incohérentes sont refusées.

L'égalité 60% du corps et 20% de mèche terminale est admise ; une différence
même infinitésimale du mauvais côté échoue. Doji refusé. Calcul exact Decimal,
sans division de ratios ni arrondi préalable, même sous précision ambiante réduite.
La mèche terminale est upper LONG / lower SHORT, dans le sens final de
l'impulsion. Aucune limite séparée sur lower LONG / upper SHORT : la contrainte
sur le corps borne déjà indirectement la somme des mèches.

Aucun engulfing, breakout du high précédent, ATR, EMA20, MACD, filtre de session
ou optimisation corps/mèche n'est ajouté. Les anciens composants restent figés.

## Suite autorisée — assemblage de l'impulsion

Après fusion du sous-prédicat corps/mèches et CI verte, assembler uniquement :
`emerging_direction AND range_qualified AND volume_qualified AND body_wick_qualified`.
Émettre le type DIRECTIONAL_IMPULSE_EVENT, sa direction émergente, l'index et
le timestamp de `t` clôturée. Aucun replay, OOS ou signal d'entrée n'est autorisé.
Le prédicat REVERSAL_TRANSITION_EVENT reste distinct et à formaliser.
