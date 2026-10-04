# EMA_PULLBACK_V2_REGIME_GATED — charte de recherche

Date de décision : 2026-10-03 UTC. Statut : `PRE_FORMALIZATION`.
Dernière formalisation : 2026-10-04 UTC.
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
qualifié n'est pas encore un signal d'entrée. L'ordre désormais figé est :
événement complet, contexte actif, pullback qualifié et consommation unique,
puis confirmation prix/momentum sur une clôture ultérieure et base fill offline
à l'Open de la seule barre suivante. Le stop structurel et la politique à une
position sont figés ci-dessous ; Risk Engine/sizing et les autres décisions
de gestion/sortie restent des gates séparées.

Les seuils d'étendue, de volume et de géométrie des bougies sont désormais fixés
dans leurs sous-contrats ci-dessous ; aucun ATR ou magnitude MACD n'est fixé. Aucun
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
distinct, formalisé séparément ci-dessous.

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
avec des `Decimal` exacts. À cette étape historique, il ne combinait pas encore
le range avec la direction émergente et n'émettait ni événement ni signal d'entrée ; l'assemblage autorisé
est désormais décrit ci-dessous. ATR,
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
À cette étape historique, les trois sous-prédicats direction/range/volume
n'étaient pas encore assemblés en événement d'impulsion ou signal d'entrée.
Les tests sont uniquement synthétiques ; aucun replay, accès OOS ou ajustement sur MNQ 03-26/06-26.

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

## Assemblage de l'impulsion — décision du propriétaire

L'assemblage est autorisé explicitement par le propriétaire après fusion du
prédicat corps/mèches. PR #282 fusionnée après CI #246 verte, merge
`3997b75d6451b6e030c4f38cb428938da0211fb0`.

```text
directional_impulse_event_qualified =
    emerging_direction != NONE
    AND range_qualified
    AND volume_qualified
    AND body_wick_qualified
```

`evaluate_directional_impulse_event_v2` appelle exactement les quatre fonctions
figées. Aucune constante, règle d'entrée ou condition supplémentaire de marché
n'est introduite. Une même observation canonique `DirectionalImpulseBarV2`
fournit OHLC et volume Last/Minute à tous les calculs ; les vues internes ont
les mêmes index, timestamps et clôtures. Les métadonnées de volume gardent leurs
contrôles et ne remplacent pas la filiation du futur dataset.

Seules les observations présentes de `t-20 ... t-1` et `t` sont consultées.
Aucune barre plus ancienne ou future n'est lue. La direction est calculée par
la fonction existante sur `t-3 ... t-1` ; la candidate ne peut pas la modifier.
Warmup insuffisant, direction NONE ou tout composant non qualifié donne zéro
événement. Les statuts individuels sont conservés. Une candidate OHLC invalide
ou de range nul retourne le statut corps/mèches explicite, sans projeter cette
candidate dans le sous-prédicat de range ; range et volume restent alors non
évalués. Les incohérences structurelles ou temporelles restent des erreurs
fail-closed, jamais des événements. Aucune priorité stratégique nouvelle.

Si et seulement si les quatre composants qualifient, l'événement immutable
porte `event_type = DIRECTIONAL_IMPULSE_EVENT`, `event_direction` exclusivement
émergente, `event_bar_index = t`, `event_timestamp = timestamp_utc[t]` clôturée.
Il est compatible avec le compositeur distinct existant et ses règles de
collision inchangées. Il ne constitue pas une entrée ni une qualification
complète momentum/EMA20/pullback. Aucune durée de contexte ou invalidation
ultérieure n'est inventée ici. Aucun replay ni sélection de dataset.

## Direction préalable au retournement — décision du propriétaire

Le 2026-10-03, `REVERSAL_TRANSITION_EVENT_PRIOR_DIRECTION_REQUIRED` est acquittée.
La définition indépendante suivante est figée avant replay, non optimisée,
sans dérivation des résultats V1/V1A/V1B :

```text
PRIOR_DIRECTION_LOOKBACK = 5 closed bars
PRIOR_BARS = [t-5, t-4, t-3, t-2, t-1]
d1 = Close[t-4] - Close[t-5]
d2 = Close[t-3] - Close[t-4]
d3 = Close[t-2] - Close[t-3]
d4 = Close[t-1] - Close[t-2]
up_steps = count(di > 0)
down_steps = count(di < 0)
flat_steps = count(di == 0)
UP = Close[t-1] > Close[t-5] AND up_steps >= 3
DOWN = Close[t-1] < Close[t-5] AND down_steps >= 3
NONE = neither UP nor DOWN
UP => only SHORT reversal is eligible
DOWN => only LONG reversal is eligible
NONE => no reversal event
```

Les clôtures égales comptent uniquement comme flat. Les extrémités doivent
être strictement orientées ; Close[t-1] == Close[t-5] donne NONE, même avec
3 pas directionnels. Un seul pullback ou un seul flat est admis si les deux
conditions de direction sont satisfaites. Aucun seuil de magnitude ajouté.

La fonction `evaluate_reversal_prior_direction_v2` du module distinct
`src/agicore/trading/reversal_transition_v2.py` lit seulement les cinq index
antérieurs requis. `t` peut être absent et n'est jamais lue ;
ni les barres plus anciennes ni les futures ne sont consultées. La direction
est entièrement connue à Close[t-1] ; l'index et le timestamp de disponibilité
sont conservés sur une évaluation valide. Le calcul des quatre différences
est exact en Decimal, sans arrondi préalable, même sous faible précision ambiante.
Les entiers exacts sont acceptés ; floats et types non-prix ne sont pas convertis
silencieusement. Aucun prix ou indicateur autre que ces cinq Close n'est demandé.

| Condition | Statut | Direction préalable |
| --- | --- | --- |
| Moins de cinq bougies antérieures clôturées dans la fenêtre requise | `INSUFFICIENT_WARMUP` | `NONE` |
| Une Close requise absente, non finie ou de type invalide | `INVALID_PRIOR_DIRECTION_INPUT` | `NONE` |
| Cinq observations valides | `EVALUATED` | `UP`, `DOWN` ou `NONE` |

Une barre absente dans la fenêtre représente un historique insuffisant ;
une barre présente mais sans Close représente une entrée invalide. Un manque
de clôture est un warmup insuffisant. L'historique clôturé est vérifié avant les
prix ; les index ou timestamps incohérents sont refusés fail-closed. Sur les
statuts non évalués, aucune direction de retournement ou date de disponibilité
n'est revendiquée. `reversal_direction = None` représente l'absence de côté éligible.

IMPULSE garde sa direction émergente stricte sur trois bougies ; REVERSAL garde
la direction préalable établie sur cinq, avec au moins trois transitions sur
quatre et une extrémité alignée. Aucun héritage/import du détecteur d'impulsion.
Le type partagé LONG/SHORT est seulement celui de l'infrastructure de composition.
EMA20, MACD, RSI, stochastic, volume, range, wick, ATR et filtre de session
ne participent pas à ce sous-prédicat. Il ne qualifie pas encore un événement
REVERSAL_TRANSITION_EVENT ou une entrée. Aucun replay ni accès OOS.

## Bougie de rejet du retournement — décision du propriétaire

Le 2026-10-03, `REVERSAL_TRANSITION_EVENT_REJECTION_BAR_REQUIRED` est acquittée.
`REVERSAL_TRANSITION_EVENT_REJECTION_BAR` est figé comme baseline initiale
pré-replay, non optimisée, sans dérivation des résultats V1/V1A/V1B.
`MIN_REJECTION_WICK_RATIO = Decimal("0.40")` ne sera pas ajusté après
observation de résultats.

```text
PRIOR_BARS = [t-5, t-4, t-3, t-2, t-1]
REJECTION_CANDIDATE = t, closed
range_t = High[t] - Low[t]
upper_wick_t = High[t] - max(Open[t], Close[t])
lower_wick_t = min(Open[t], Close[t]) - Low[t]
prior_high = max(High[t-5], ..., High[t-1])
prior_low = min(Low[t-5], ..., Low[t-1])
SHORT = prior_direction == UP
        AND High[t] > prior_high
        AND Close[t] < prior_high
        AND upper_wick_t >= Decimal("0.40") * range_t
LONG = prior_direction == DOWN
       AND Low[t] < prior_low
       AND Close[t] > prior_low
       AND lower_wick_t >= Decimal("0.40") * range_t
```

La fonction `evaluate_reversal_rejection_bar_v2` réutilise la fonction figée de
direction préalable et exactement les mêmes cinq observations antérieures pour
les extrêmes. La candidate est exclue des deux références ; seule sa géométrie
est utilisée pour le rejet. Aucune bougie future ou antérieure à t-5 n'est lue.
Direction disponible à Close[t-1], rejet disponible uniquement à Close[t].
Les index et timestamps de disponibilité sont conservés séparément.

Validation préalable de la candidate : OHLC finis et exacts, High >= max(Open,
Close), Low <= min(Open, Close), High >= Low. Sinon `INVALID_OHLC`, qualification
fausse. Après validation, range <= 0 donne `INVALID_CANDIDATE_RANGE`,
qualification fausse. Le balayage et le retour sont stricts : égalité du High
ou du Low à l'extrême, ou de Close à l'extrême concerné, échoue. La mèche est
inclusive : exactement 40% passe, toute valeur inférieure échoue. Calculs exacts
Decimal, sans division de ratios ni arrondi avant comparaison, même sous
précision ambiante réduite ; les entiers exacts sont admis, les floats refusés.

Aucune condition de couleur du corps : une bougie encore haussière peut
qualifier SHORT après UP, et une bougie encore baissière peut qualifier LONG
après DOWN. Un doji n'est pas exclu si les trois conditions sont satisfaites.
Le retour compare Close au seul extrême balayé ; aucune borne supplémentaire
sur l'autre extrême n'est ajoutée. Une direction préalable NONE ne qualifie rien.

Les statuts warmup/donnée Close invalide du sous-prédicat préalable sont
propagés. Candidate absente/non clôturée ou métadonnées incohérentes : erreur
fail-closed. High/Low antérieurs manquants, non finis ou inversés :
`INVALID_PRIOR_EXTREMA`, qualification fausse. Ces contrôles d'entrée ne sont
pas des conditions de marché supplémentaires. L'Open historique n'est pas
requis. `EVALUATED` distingue une évaluation valide de son booléen de qualification.

Aucun MACD, EMA20, volume, ATR, RSI, stochastic, sens du corps ou confirmation
t+1 n'est ajouté. Le rejet reste un sous-prédicat : il n'émet aucun événement
REVERSAL_TRANSITION_EVENT ni signal d'entrée. La transition opposée après le
rejet sera formalisée séparément. Aucun replay, accès OOS ou ajustement sur
MNQ 03-26/06-26.

## Transition opposée sur une seule bougie — décision du propriétaire

Le 2026-10-03, `REVERSAL_TRANSITION_EVENT_OPPOSITE_TRANSITION_REQUIRED` est
acquittée. `REVERSAL_TRANSITION_EVENT_OPPOSITE_TRANSITION` est une baseline
pré-replay non optimisée, sans dérivation V1/V1A/V1B ni ajustement après résultats.

```text
REJECTION_BAR = t
CONFIRMATION_BAR = t+1
CONFIRMATION_WINDOW = exactly 1 closed bar
rejection_body_low = min(Open[t], Close[t])
rejection_body_high = max(Open[t], Close[t])
SHORT = prior_direction == UP AND rejection_direction == SHORT
        AND Close[t+1] < Open[t+1]
        AND Close[t+1] < rejection_body_low
LONG = prior_direction == DOWN AND rejection_direction == LONG
       AND Close[t+1] > Open[t+1]
       AND Close[t+1] > rejection_body_high
```

La fonction `evaluate_reversal_opposite_transition_v2` réutilise le prédicat de
rejet figé. À Close[t], rejet qualifié mais transition non confirmée :
`AWAITING_OPPOSITE_TRANSITION`. Elle reçoit une horloge `closed_bar_index` ;
à t, aucune présence ni valeur de t+1 n'est consultée, même si l'historique
fourni contient déjà des bougies futures. `end_of_data=True` est un signal
de disponibilité de données, pas un filtre stratégique : une fin à t sans
confirmation clôturée donne `INCOMPLETE_CONFIRMATION`. À partir de t+1,
seule cette bougie de confirmation est consultée ; une absence ou non-clôture
donne aussi `INCOMPLETE_CONFIRMATION`, transition fausse.

Comparaisons strictes, en Decimal exact sans arrondi : Close égal à la borne
concernée ou à Open échoue. Confirmation valide : `CONFIRMED`. Bougie t+1
clôturée et prédicat faux : `EXPIRED_NO_TRANSITION`. Une bougie t+2 ou ultérieure
ne peut jamais confirmer rétroactivement t. Une évaluation ultérieure utilise
t+1 seulement et conserve son index/timestamp de disponibilité ; elle ne
déplace pas la confirmation à la barre courante.

Seuls Open/Close finis et exacts de t+1 sont requis ; High/Low ne participent
pas à cette gate. Open/Close absents, non finis ou de type inexact :
`INVALID_CONFIRMATION_INPUT`, transition fausse. Un rejet non qualifié donne
`REJECTION_NOT_QUALIFIED`, conserve ses statuts imbriqués et ne lit pas t+1.
Index/timestamps incohérents et horloge précédant t : erreur fail-closed.
Les évaluations de transition valides, positives ou expirées, sont connues
uniquement à Close[t+1] ; les états d'attente/incomplétude n'ont pas de timestamp
de confirmation. Le rejet conserve sa disponibilité séparée à Close[t].

Aucune cassure du Low[t] SHORT ou du High[t] LONG, magnitude de corps, seuil
de range/volume sur t+1, EMA20, MACD, RSI, stochastic, ATR ou session. Symétrie
LONG/SHORT stricte. Aucune lecture t+2/future, replay, OOS ou calibration MNQ.
Ce sous-prédicat ne crée pas encore d'événement complet.

## Assemblage du retournement — décision du propriétaire

La confirmation a été fusionnée par PR #286 après CI #254 verte, merge
`39130e82152002c3c11c7c316f65d8fbcc7fc9d5`.
L'assemblage explicitement autorisé par le propriétaire appelle exactement
les trois fonctions figées sur les mêmes observations :

```text
REVERSAL_TRANSITION_EVENT =
    prior_direction_qualified
    AND rejection_bar_qualified
    AND opposite_transition_confirmed
UP => SHORT event
DOWN => LONG event
```

`evaluate_reversal_transition_event_v2` conserve les résultats individuels et
leurs statuts. À Close[t] : aucun événement, transition en attente. Échec,
warmup incomplet, entrée invalide, confirmation absente ou non clôturée : aucun
événement. Un t+1 échoué reste expiré même si t+2 satisfait la géométrie.
Aucun seuil, filtre, priorité de marché ou nouveau composant n'est introduit.

L'événement source immutable `ReversalTransitionEventV2` porte exactement :

```text
event_type = REVERSAL_TRANSITION
event_direction = LONG | SHORT
prior_direction = UP | DOWN
rejection_bar_index = t
event_bar_index = t+1
rejection_timestamp = timestamp_utc[t]
event_timestamp = timestamp_utc[t+1]
```

La direction vient exclusivement du côté opposé à la direction préalable.
Index et timestamps sont cohérents, UTC et ordonnés. Les seules observations
consultées sont t-5..t, puis t+1 derrière l'horloge clôturée. Une réévaluation
ultérieure ne retimestamp pas l'événement ; t+2/future ne sont jamais lus.

`as_regime_event()` adapte explicitement l'étiquette source
`REVERSAL_TRANSITION` à la famille de composition déjà figée
`RegimeEventType.REVERSAL_TRANSITION_EVENT`, en gardant direction, index et
timestamp t+1. Le record source conserve les métadonnées de rejet. Le
compositeur existant reste inchangé : seul/sens commun qualifié, directions
opposées ambiguës, aucune priorité entre impulsion et retournement. Sa règle
de barre courante refuse de réutiliser l'événement t+1 comme événement t+2.

L'assemblage seul ne maintient pas le contexte sur des barres suivantes ; la
durée de vie distincte est formalisée ci-dessous. Il ne définit pas de
momentum/acceptation EMA20/pullback et n'émet aucune entrée.
Baselines inchangées, pré-replay non optimisées, sans dérivation V1/V1A/V1B.
Aucun replay, accès OOS, dataset réel ou ajustement MNQ 03-26/06-26.

## Durée de vie du contexte — décision du propriétaire

Le 2026-10-03, `REGIME_CONTEXT_V2_EVENT_LIFETIME_REQUIRED` est acquittée.
Les deux bornes sont des baselines initiales pré-replay, non optimisées et
choisies avant toute performance V2. Aucun ajustement à partir de MNQ 03-26,
MNQ 06-26 ou des résultats V1/V1A/V1B :

```text
MAX_CONTEXT_AGE_CLOSED_BARS = 8
MAX_CONTEXT_ELAPSED_TIME = 8 minutes
CONTEXT_REUSE = ONE_SHOT
SAME_DIRECTION_REFRESH = DISABLED
source_event_bar_index = e
first_eligible_pullback_bar = e+1
last_eligible_pullback_bar = e+8
timestamp[k] - source_event_timestamp <= 8 minutes
```

Le contexte est créé après Close[e] par la composition qualifiée d'une
impulsion, d'un retournement complet ou des deux dans le même sens. Les
étiquettes de famille du compositeur sont conservées, ainsi que direction,
index et timestamp source. Pour REVERSAL, e est la confirmation t+1, jamais
la bougie de rejet t. La bougie e est toujours inéligible au pullback.

États exacts : `INACTIVE`, `ACTIVE`, `CONSUMED`, `EXPIRED_MAX_AGE`,
`EXPIRED_ELAPSED_TIME`, `INVALIDATED_OPPOSITE_EVENT`,
`INVALIDATED_AMBIGUOUS_EVENT`, `EXPIRED_END_OF_DATA`.

`advance_regime_context_v2` suit cet ordre sur chaque nouvelle bougie clôturée :

1. expiration du contexte ACTIVE si temps écoulé >8 minutes, puis âge >8
   bougies ; si les deux sont dépassés, le statut temporel prévaut ;
2. appel du compositeur figé sur les événements complets de la seule bougie k ;
3. AMBIGUOUS invalide l'ancien contexte sans remplacement ; un événement
   opposé invalide l'ancien et crée un nouveau contexte à k, inéligible sur k ;
4. même direction ACTIVE : source, étiquettes et âge conservés, aucune pile
   ni prolongation ; notice `SAME_DIRECTION_EVENT_IGNORED_NO_REFRESH` ;
5. seulement ensuite, évaluation de `EMA20_PULLBACK_QUALIFIED` sur un
   contexte ACTIVE existant et éligible ; true le consomme définitivement.

À e+8 et exactement huit minutes, le contexte reste éligible. Si le pullback
n'est pas qualifié, `EXPIRED_MAX_AGE` intervient après cette dernière
opportunité. À e+9, l'âge interdit l'évaluation. Un dépassement temporel, même
de la plus petite précision du timestamp, expire avant l'évaluation, y compris
sur la première bougie disponible après un trou de données/session.
L'expiration initiale précède les nouveaux événements : un événement après
expiration peut créer une nouvelle source, même de même direction, sans
rafraîchir l'ancienne. Une invalidation opposée/ambiguë sur k gagne sur le
pullback potentiel de l'ancien contexte ; aucun appel de son évaluateur.

La consommation retient dans un record immutable `source_event_types`,
`source_event_direction`, `source_event_bar_index`, `source_event_timestamp`,
`pullback_bar_index`, `pullback_timestamp`. Un contexte consommé reste CONSUMED
malgré un échec ultérieur de confirmation/entrée. Il faut un nouvel événement
pour une nouvelle source et une nouvelle opportunité. Les records retirés
sur la bougie sont rendus au caller pour audit, sans modifier les snapshots
précédents ni empiler plusieurs contextes actifs.

Cette gate définissait une interface d'évaluateur formel causal, appelé
avec le contexte, k et son timestamp après les contrôles ci-dessus. Aucun
évaluateur fourni ou résultat false : aucune consommation. Un résultat autre
que bool est refusé. Une touche/proximité EMA brute n'est pas une qualification
formelle. La règle OHLC/EMA20 est désormais formalisée ci-dessous.

Fin des données : `end_of_data=True` expire tout contexte restant ACTIVE après
la dernière évaluation autorisée. `finish_regime_context_v2` termine aussi la
série au dernier index/timestamp déjà connus, sans inventer une nouvelle
bougie. Un record CONSUMED ou déjà terminal reste dans son état. Une série
terminée refuse toute continuation/transport de contexte ; la suivante part
sans contexte. Aucun pullback, entrée ou report synthétique.

Métadonnées UTC, source clôturée et horloge index/timestamp strictement
croissante obligatoires ; événements futurs, double traitement d'une bougie,
provenance future ou entrées incohérentes refusés fail-closed. L'API reçoit
seulement les événements de la bougie courante, sans collection future.
Le compositeur et les détecteurs figés restent inchangés.

Aucune invalidation par prix/High/Low, franchissement EMA20, MACD, ATR, volume,
filtre de session, limite quotidienne, stop, take profit ou exécution d'entrée.
Aucun replay, accès OOS ou lecture de dataset réel.

## Pullback EMA20 V2 — décision du propriétaire

Le 2026-10-03, `EMA20_PULLBACK_V2_REQUIRED` est acquittée. Définition initiale
pré-replay non optimisée, indépendante des résultats V1/V1A/V1B. Aucun seuil
en ticks/points ni paramètre de proximité n'est choisi. Aucun ajustement à
partir de MNQ 03-26 ou MNQ 06-26.

```text
EMA_PERIOD = 20
ALPHA = 2/21
EMA_RESET_AT_SESSION = FALSE
EMA20[19] = sum(Close[0] ... Close[19]) / 20
EMA20[i] = (2 * Close[i] + 19 * EMA20[i-1]) / 21, i >= 20
ema_reference = EMA20[k-1]
first possible pullback candidate = 20
```

`evaluate_ema20_v2` convertit exactement chaque Decimal fini en Fraction et
effectue la moyenne d'initialisation et chaque récurrence en rationnels exacts.
Entiers et Fraction exacts sont aussi admis ; les floats binaires sont refusés.
Aucune division Decimal arrondie, conversion float ou approximation de seuil
n'influence les comparaisons, même sous faible précision Decimal ambiante.

Les indices énumèrent les observations réelles depuis zéro. Aucun reset
quotidien/session, remplissage de gap, bougie synthétique ou seed ultérieur.
Un gap d'horloge entre deux observations n'interrompt pas la récurrence ; seules
les clôtures valides et terminées sont utilisées. L'API consulte explicitement
0..k-1, jamais k ni les clés futures pour calculer la référence. Un Close
nécessaire absent/non fini, une observation requise absente ou non clôturée
donne `INVALID_EMA_INPUT` sans substitution ni saut de cette observation.
Avant l'index 19, la première EMA n'existe pas : `INSUFFICIENT_EMA_WARMUP`.
Le pullback exige au moins vingt clôtures antérieures et commence à k=20.

Pour la candidate k clôturée, la référence est fixée par EMA20[k-1], entièrement
connue avant k. Close[k] peut changer la géométrie qualifiée, mais jamais cette
référence ; EMA20[k] n'est pas utilisée pour juger le contact.

```text
LONG = Close[k-1] > ema_reference
       AND Open[k] >= ema_reference
       AND Low[k] <= ema_reference
       AND Close[k] > ema_reference

SHORT = Close[k-1] < ema_reference
        AND Open[k] <= ema_reference
        AND High[k] >= ema_reference
        AND Close[k] < ema_reference
```

| Frontière | LONG | SHORT |
| --- | --- | --- |
| Open égal à la référence | Autorisé | Autorisé |
| Extrême égal à la référence | Low égal : contact accepté | High égal : contact accepté |
| Extrême au-delà de la référence | Low inférieur autorisé | High supérieur autorisé |
| Aucun contact | Low supérieur : FAIL | High inférieur : FAIL |
| Close[k] égal à la référence | FAIL | FAIL |
| Close[k-1] égal à la référence | FAIL | FAIL |

Aucune couleur de bougie n'est exigée : LONG rouge, SHORT vert ou doji peuvent
qualifier si toute la géométrie EMA est satisfaite. Aucun seuil de range, pente,
magnitude ou ratio corps/mèche n'est ajouté au pullback.

OHLC de k finis et cohérents requis : High >= max(Open, Close),
Low <= min(Open, Close), High >= Low. Sinon `INVALID_OHLC` et false. Un Close[k]
absent/non fini donne `INVALID_EMA_INPUT` et false. Les OHLC historiques ne sont
pas employés pour l'EMA ; seules leurs clôtures et métadonnées causales le sont.
Index, fermeture et timestamp UTC cohérents sont exigés ; les timestamps
historiques doivent être strictement croissants et antérieurs à celui de k.

`evaluate_ema20_pullback_v2` est la décision pure sur un contexte déjà ACTIVE,
k dans e+1..e+8 et temps écoulé <=8 minutes. Un contexte absent, terminal,
sur sa propre bougie source ou hors fenêtre est `INELIGIBLE_CONTEXT` et false.
Ce prédicat ne crée ni ne prolonge le contexte. `advance_ema20_pullback_v2`
le raccorde au cycle de vie figé : expiration, composition/invalidation,
conservation sans refresh, puis seulement évaluation formelle. Invalidation
opposée/ambiguë gagne toujours sur un pullback de l'ancien contexte sur k.

True consomme à Close[k] et conserve context_source_event_types,
context_direction, context_event_bar_index, context_event_timestamp,
pullback_bar_index=k, pullback_timestamp et ema_reference=EMA20[k-1] dans la
décision qualifiée. Le record CONSUMED du cycle de vie conserve aussi cette
Fraction exacte avec sa source et son pullback ; elle reste disponible après
des barres ultérieures ou le retrait de l'ancien record. Aucun second pullback
ni réactivation après échec de future confirmation/entrée. Les règles de
durée de vie et les détecteurs antérieurs sont inchangés.

Aucun MACD, EMA slope/proximity, ATR, volume, couleur de bougie, SMA14/SMA21,
filtre de session, stop, target ou exécution d'entrée. Aucune règle V1 héritée.
Aucun replay, accès OOS ou lecture de dataset réel.

## Confirmation prix/momentum d'entrée V2 — décision du propriétaire

Le 2026-10-03, `EMA_PULLBACK_V2_ENTRY_CONFIRMATION_MOMENTUM_REQUIRED` est
acquittée. Baseline initiale pré-replay non optimisée, indépendante des
résultats V1/V1A/V1B. Aucun ajustement sur MNQ 03-26 ou MNQ 06-26.

```text
PULLBACK_BAR = k
FIRST_CONFIRMATION_BAR = k+1
LAST_CONFIRMATION_BAR = k+2
MAX_CONFIRMATION_AGE_CLOSED_BARS = 2
MAX_CONFIRMATION_ELAPSED_TIME = 2 minutes
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
MACD_WARMUP_CLOSED_BARS = 26 + 9 = 35
MACD_SESSION_RESET = FALSE
NO_MACD_CROSS_REQUIRED
NO_MACD_MAGNITUDE_THRESHOLD
```

À Close[k], le pullback formel est qualifié, le contexte reste CONSUMED et
l'opportunité distincte devient AWAITING_CONFIRMATION. Elle conserve exactement
le corps de k : pullback_body_low=min(Open[k], Close[k]) et
pullback_body_high=max(Open[k], Close[k]). k ne peut jamais se confirmer.
Seules k+1 et k+2, clôturées, sont candidates ; le premier PASS gagne.

| Direction du pullback consommé | Prix de confirmation sur q | Momentum sur q |
| --- | --- | --- |
| LONG | Close[q] > Open[q] et Close[q] > pullback_body_high | MACD[q] > SIGNAL[q], HIST[q] > 0, HIST[q] > HIST[q-1], MACD[q] > MACD[q-1] |
| SHORT | Close[q] < Open[q] et Close[q] < pullback_body_low | MACD[q] < SIGNAL[q], HIST[q] < 0, HIST[q] < HIST[q-1], MACD[q] < MACD[q-1] |

Les deux colonnes sont exigées simultanément. Toutes leurs comparaisons sont
strictes : égalité au bord du corps, doji, MACD==SIGNAL, HIST==0, histogramme
inchangé ou ligne MACD inchangée donnent FAIL. La cassure de High[k] pour LONG
ou Low[k] pour SHORT n'est pas exigée. Les High/Low de q ne participent pas à
cette gate ; seuls ses Open/Close et sa disponibilité causale sont requis.
La couleur du pullback k reste celle admise par le prédicat EMA20 figé.

```text
EMA12[0] = Close[0]
EMA26[0] = Close[0]
MACD[0] = EMA12[0] - EMA26[0] = 0
SIGNAL[0] = MACD[0]
HIST[0] = MACD[0] - SIGNAL[0] = 0

EMA12[i] = EMA12[i-1] + (2/13) * (Close[i] - EMA12[i-1])
EMA26[i] = EMA26[i-1] + (2/27) * (Close[i] - EMA26[i-1])
MACD[i] = EMA12[i] - EMA26[i]
SIGNAL[i] = SIGNAL[i-1] + (2/10) * (MACD[i] - SIGNAL[i-1])
HIST[i] = MACD[i] - SIGNAL[i]
```

Chaque prix Decimal fini est converti exactement en Fraction ; toutes les
récurrences et comparaisons restent rationnelles exactes. Entiers/Fraction
admis, floats binaires refusés. Aucun arrondi préalable, seuil arrondi, reset
journalier/session ou remplissage des gaps. L'indicateur avance uniquement
sur les clôtures valides des observations réelles, sans bougie synthétique.
Les indices commencent à zéro. Le warmup inclut q : premier candidat MACD
éligible à q=34, lorsque 35 bougies clôturées existent. Avant cela :
INSUFFICIENT_MACD_WARMUP et confirmation false. Les valeurs initiales sont
exposées pour vérifier l'arithmétique mais n'autorisent aucune confirmation.
35 est dérivé mécaniquement de 26+9, sans observation de performance.

Le MACD peut être déjà au-dessus du signal avant q pour LONG, ou au-dessous
pour SHORT. Aucun crossover exact sur q ni seuil de magnitude. Il faut à la
fois le bon côté, le bon signe d'histogramme, son renforcement strict et le
déplacement strict de la ligne MACD dans la direction du trade.

`begin_entry_confirmation_momentum_v2` accepte la transition formelle de
consommation EMA20, vérifie sa provenance et capture le corps de k une fois.
`advance_entry_confirmation_momentum_v2` traite chaque clôture candidate dans
l'ordre, sans saut de k+1 en faveur de k+2. Index, fermeture et timestamps UTC
cohérents sont requis. Le préfixe MACD consulté est explicitement 0..q, sans
énumération des clés ou de la longueur d'une collection contenant le futur.
Les timestamps requis sont strictement croissants et connus à Close[q].

| Situation | Transition de l'opportunité |
| --- | --- |
| Close[k] | AWAITING_CONFIRMATION, aucune évaluation |
| Temps depuis k >2 minutes | EXPIRED_CONFIRMATION_ELAPSED_TIME avant toute lecture prix/MACD de q |
| k+1 FAIL | Reste AWAITING_CONFIRMATION |
| Premier PASS sur k+1 ou k+2 | CONFIRMED à Close[q], record qualifié conservé |
| k+2 FAIL | EXPIRED_NO_ENTRY_CONFIRMATION après évaluation |
| q au-delà de k+2 | Aucune évaluation, aucune résurrection |
| État terminal | Conservé sans lecture des bougies ultérieures |

Exactement deux minutes est inclusif. Si temps et âge sont dépassés,
l'expiration temporelle est appliquée avant toute évaluation. Si k+1 passe,
k+2 n'est jamais lue pour cette opportunité. Si les données disponibles
s'arrêtent avant une prochaine clôture, aucune confirmation/entrée synthétique
n'est produite ; seule la décision connue est conservée. Le contexte source
reste définitivement CONSUMED, y compris après warmup insuffisant, expiration,
échec de confirmation ou future entrée.

Un Close requis absent/non fini, une observation requise absente ou non
clôturée donne INVALID_MACD_INPUT sans substitution, saut ni reset. Open[q]
invalide ou candidate indisponible donne INVALID_CONFIRMATION_INPUT. Ces
statuts techniques donnent false, sans prolonger la fenêtre. Les métadonnées
incohérentes/non causales sont refusées par EntryConfirmationV2Error.

Sur PASS, conserver source_regime_event_types/direction/bar_index/timestamp,
pullback_bar_index=k, pullback_timestamp, ema_reference exacte,
confirmation_bar_index=q, confirmation_timestamp, macd, signal, histogram,
previous_macd et previous_histogram. La décision n'existe qu'à Close[q].
Le record et le contexte source sont immuables ; la confirmation n'est pas
une exécution d'entrée.

Aucun fill, ordre, stop, take profit, breakeven, trailing, sizing, objectif
quotidien, limite de trades/jour, filtre de session, SMA14/SMA21, RSI,
stochastic, volume supplémentaire ou seuil de magnitude MACD. Aucune règle
d'entrée V1 héritée, aucun replay ni ouverture OOS.

## Exécution d'entrée offline V2 — décision du propriétaire

Le 2026-10-04, `EMA_PULLBACK_V2_ENTRY_EXECUTION_REQUIRED` est acquittée.
Baseline initiale pré-replay non optimisée, choisie indépendamment de V1/V1A/V1B.
Aucun ajustement sur MNQ 03-26 ou MNQ 06-26, aucun replay ni ouverture OOS.

```text
CONFIRMATION_BAR = q
ENTRY_DECISION_MOMENT = Close[q]
EXECUTION_BAR = q+1
EXECUTION_POINT = Open[q+1]
ORDER_SEMANTICS = MARKET
MAX_EXECUTION_AGE_CLOSED_BARS = 1
MAX_EXECUTION_ELAPSED_TIME = 1 minute
NO_FILL_ON_q
NO_MAX_ENTRY_GAP_FILTER
```

La confirmation clôturée qualifiée crée PENDING_NEXT_BAR_OPEN à Close[q],
sans fill ni lecture de prix d'exécution. q ne peut jamais porter sa propre
exécution. Seule q+1 peut exécuter : LONG porte la sémantique BUY MARKET,
SHORT SELL_SHORT MARKET. Ce sont des étiquettes offline, aucun ordre soumis.
Le prix de base exact est execution_price_before_costs=Open[q+1].

| Champs de q+1 | Accès au moment du fill |
| --- | --- |
| bar_index | Autorisé, pour exiger q+1 |
| timestamp_utc | Autorisé, pour valider l'horloge |
| Open | Autorisé seulement après index/horloge valides |
| High, Low, Close, Volume | Interdits |
| is_closed | Non lu : la décision se fait à l'ouverture |

Le protocole d'observation ne déclare que ces trois champs autorisés.
L'évaluateur lit uniquement ces attributs, même si le caller détient déjà
l'OHLCV complet de q+1. Aucune validation OHLC ni condition sur les prix
ultérieurs de cette barre. Des observations minimales et des bougies complètes
gardées par un test d'accès donnent exactement le même résultat.

Exiger index=q+1 et 0 < timestamp[q+1]-timestamp[q] <=1 minute. Exactement
une minute est inclusif. Une coupure supérieure à une minute expire avant
toute lecture de l'Open. Un timestamp non croissant, absent, non UTC/cohérent
ou un index antérieur incohérent refuse le fill : INVALID_EXECUTION_CLOCK.
L'état technique terminal FAILED_INVALID_EXECUTION_CLOCK conserve ce refus,
sans réactivation. Répéter la propre barre q avec son timestamp connu conserve
PENDING, sans lire son Open ni produire de fill.

| Situation | État d'exécution | Statut particulier | Fill |
| --- | --- | --- | --- |
| Confirmation qualifiée à Close[q] | PENDING_NEXT_BAR_OPEN | NOT_EVALUATED | Aucun |
| q+1 valide, Open fini et positif | FILLED | EVALUATED | Exactement Open[q+1] |
| q+1 absent / fin des données | EXPIRED_NO_EXECUTION | EVALUATED | Aucun |
| Une barre ultérieure arrive après q+1 manquant | EXPIRED_NO_EXECUTION | EVALUATED | Aucun |
| q+1 avec temps écoulé >1 minute | EXPIRED_EXECUTION_GAP | EVALUATED | Aucun |
| Horloge non causale/invalide | FAILED_INVALID_EXECUTION_CLOCK | INVALID_EXECUTION_CLOCK | Aucun |
| Open absent, non fini ou <=0 | FAILED_INVALID_EXECUTION_INPUT | INVALID_EXECUTION_INPUT | Aucun |

Une barre ultérieure est rejetée par son seul index, sans consultation de
son timestamp ou de ses prix. Aucun report q+2/q+3, bougie ou fill synthétique.
Open absent/non fini/non positif n'est jamais remplacé par Close[q], Close[q+1],
midpoint, EMA20 ou un prix antérieur. Decimal fini converti exactement en
Fraction ; entiers/Fraction exacts admis, float binaire/chaîne/bool refusés
selon les conventions V2. Aucun arrondi préalable. Un gap de prix valide,
même très grand, remplit à l'Open valide, sans seuil de distance ni annulation.

`register_entry_execution_v2` valide la provenance de la décision CONFIRMED
et l'enregistre à Close[q] dans EntryExecutionBookV2. Ce registre immuable
appartient à une seule série offline et doit être transmis aux appels suivants.
Réenregistrer la même confirmation, y compris une copie équivalente, retourne
le même registre sans remettre son état à PENDING. Modifier une provenance
déjà enregistrée sous la même identité causale est refusé explicitement.
Des confirmations distinctes gardent des états indépendants ; aucune politique
de position ou limite de trades n'est ajoutée ici.

`execute_entry_open_v2` traite uniquement une confirmation déjà enregistrée.
opening_bar=None signifie absence définitive de q+1, dont fin de données,
pas une interrogation avant disponibilité de l'Open. Tous les états terminaux
retournent le même registre, le même état et le même record sans aucun accès
marché. FILLED reste FILLED ; aucun deuxième fill. Les expirations et échecs
restent terminaux, même si une barre future aurait permis un fill.

Le record immuable conserve source_regime_event_types/bar_index/timestamp/
direction, pullback_bar_index/timestamp/ema_reference, confirmation_bar_index=q
et son timestamp, execution_bar_index=q+1, execution_bar_timestamp,
execution_side=LONG|SHORT, execution_price_before_costs exact et les étiquettes
MARKET/BUY|SELL_SHORT. Il conserve aussi le EntryConfirmationRecordV2 complet,
avec son MACD exact. Le lien événement -> pullback consommé -> confirmation
-> exécution n'est jamais remplacé ni muté.

Cette gate ne définit que le base fill déterministe. Aucun slippage, commission,
spread, quantité, stop, take profit, breakeven ou trailing. Aucun broker,
Apex/Rithmic ou ordre NinjaTrader live connecté. Risk Engine, sizing, politique
de position et toutes les sorties restent requis avant une stratégie V2
complète, et avant toute considération pour le paper trading. Aucune règle V1
ni architecture de risque n'est héritée implicitement.

## Stop structurel initial V2 — décision du propriétaire

Le 2026-10-04, `EMA_PULLBACK_V2_INITIAL_STOP_REQUIRED` est acquittée.
`EMA_PULLBACK_V2_INITIAL_STOP` est une baseline initiale pré-replay non optimisée,
indépendante de V1/V1A/V1B. Aucun ajustement sur MNQ 03-26 ou MNQ 06-26.

```text
PULLBACK_BAR = k
CONFIRMATION_BAR = q, q in {k+1, k+2}
ENTRY_BAR = q+1
STRUCTURAL_STOP_WINDOW = [k ... q] inclusive
TICK_SIZE = Fraction(1, 4)
STOP_BUFFER_TICKS = 1
STOP_BUFFER = 0.25 point
known_at = Close[q]
INITIAL_STOP_RECALCULATION = FORBIDDEN
```

Toute la structure clôturée k..q participe : deux bougies pour q=k+1,
trois pour q=k+2. Une extension sur k+1 ou sur la confirmation q compte
autant que l'extrême du pullback k.

| Direction | Extrême structurel | Stop initial exact |
| --- | --- | --- |
| LONG | min(Low[i] pour i=k..q) | structural_low - Fraction(1, 4) |
| SHORT | max(High[i] pour i=k..q) | structural_high + Fraction(1, 4) |

Exemple LONG : Low[k]=20000, Low[k+1]=19998, Low[k+2]=19999,
confirmation q=k+2 : structural_low=19998, initial_stop=19997.75.
Le niveau est entièrement connu à Close[q], avant l'entrée, puis immuable.
Aucun Open, High, Low, Close ou Volume de q+1 n'entre dans son calcul.
Aucune barre avant k ou après q n'est lue pour cette gate.

L'interface structurelle ne lit que bar_index, timestamp_utc, is_closed,
High et Low des indices requis. Chaque barre doit exister, être clôturée
et porter des métadonnées cohérentes avec k..q et la confirmation qualifiée.
Les métadonnées non causales/incohérentes sont refusées explicitement par
InitialStopV2Error ; aucune horloge future ni longueur totale de série lue.

| Données de la fenêtre | Statut | initial_stop |
| --- | --- | --- |
| Un indice requis absent, dont k+1 intermédiaire | INCOMPLETE_STRUCTURAL_STOP_WINDOW | NONE |
| High/Low absent, non fini, inexact ou High < Low ; barre non clôturée | INVALID_STRUCTURAL_STOP_INPUT | NONE |
| Tous les indices contigus k..q valides | EVALUATED | Extrême et buffer exacts |

High et Low doivent tous deux être présents et finis sur chaque barre,
y compris le côté qui ne détermine pas l'extrême directionnel. High=Low
est admis ici : aucun seuil de range ajouté. Decimal fini est converti
exactement en Fraction ; entiers/Fraction admis, float binaire/chaîne/bool
refusés selon les conventions V2. Aucun arrondi préalable ni ajustement
sur la grille de ticks. Aucune validation du corps Open/Close supplémentaire.

`evaluate_initial_stop_v2` produit le snapshot de Close[q].
`register_initial_stop_v2` le conserve dans InitialStopBookV2, registre immuable
d'une seule série offline à transmettre aux appels suivants. Réenregistrer la
même confirmation ou une copie équivalente retourne le même registre avant
toute lecture de la structure. Un snapshot invalide/incomplet ne se répare pas
rétroactivement. Une provenance modifiée sous la même identité causale est
refusée. Des confirmations distinctes conservent des stops indépendants.

Après le fill déjà défini par la PR #291, vérifier séparément la relation
avec entry_price=execution_price_before_costs=Open[q+1] :

| Direction | ARMED | BREACHED_AT_ENTRY_OPEN |
| --- | --- | --- |
| LONG | initial_stop < entry_price | entry_price <= initial_stop |
| SHORT | initial_stop > entry_price | entry_price >= initial_stop |

L'égalité donne BREACHED_AT_ENTRY_OPEN. `bind_initial_stop_to_entry_v2`
utilise uniquement le record FILLED déjà conservé dans EntryExecutionBookV2,
sans interface de bougie ni accès marché. Aucun stop armé avant un fill réel
du modèle offline ; une exécution pending/expirée/invalide laisse le snapshot
inchangé. Un stop indisponible reste NONE, sans remplacement ni nouvelle
politique d'annulation d'entrée.

Un Open valide au-delà du niveau ne déplace pas le stop, ne le recalcule pas,
n'élargit pas le risque et n'annule pas rétroactivement le fill. FILLED reste
FILLED. La fermeture exacte d'une position BREACHED_AT_ENTRY_OPEN sera
définie par la prochaine gate de trigger/fill. Lier plusieurs fois le même
fill conserve le même registre ; un autre fill ne peut remplacer le lien.
Un ancien snapshot PENDING ne désarme pas un stop déjà lié à son fill.

Le record de stop conserve source_regime_event_types/bar_index/timestamp,
source_regime_event_direction, pullback_bar_index=k/timestamp/ema_reference,
confirmation_bar_index=q/timestamp, structural_window_first_bar=k,
structural_window_last_bar=q, structural_extreme, stop_buffer_ticks=1,
tick_size exact, initial_stop_price, stop_known_at_bar_index=q et
stop_known_at_timestamp=timestamp[q], ainsi que le EntryConfirmationRecordV2
complet. Après fill, le lien immuable ajoute entry_bar_index=q+1,
entry_bar_timestamp, entry_price, stop_state et le record d'exécution complet.
La chaîne événement -> pullback consommé -> confirmation -> stop/fill reste
conservée sans mutation des snapshots précédents.

Aucune distance minimale/maximale en ticks, aucun stop ATR, pourcentage ou
montant fixe. Un stop très large reste valide structurellement. Refuser un
trade pour son risque appartient aux futures gates Risk Engine et sizing.
Aucun trailing, breakeven, mouvement EMA20, nouveau swing, mise à jour ATR,
élargissement ou resserrement. Aucun trigger, prix de sortie, take profit,
quantité, coût ou ordre broker ajouté dans cette gate.

## Déclenchement et fill du stop structurel V2 — décision du propriétaire

Le 2026-10-04, `EMA_PULLBACK_V2_STRUCTURAL_STOP_TRIGGER_FILL_REQUIRED`
est acquittée. Baseline initiale pré-replay non optimisée, indépendante
des performances V1/V1A/V1B. Aucun ajustement MNQ 03-26 ou MNQ 06-26.

```text
STOP_ORDER_SEMANTICS = STOP_MARKET
INITIAL_STOP_RECALCULATION = FORBIDDEN
STOP_TOUCH_IS_TRIGGER = TRUE
ENTRY_BAR = e = q+1
monitoring_first_bar = e
```

Le niveau S provient exclusivement du record EMA_PULLBACK_V2_INITIAL_STOP
de la PR #292, connu à Close[q]. Il reste immuable. LONG porte protective_action
SELL ; SHORT BUY_TO_COVER. Étiquettes offline uniquement, aucun ordre broker.

| Situation | LONG | SHORT | Phase | Prix de fill de base |
| --- | --- | --- | --- | --- |
| BREACHED_AT_ENTRY_OPEN | Entry <= S | Entry >= S | ENTRY_OPEN | Entry = Open[e] |
| Gap ultérieur r>e | Open[r] <= S | Open[r] >= S | BAR_OPEN_GAP | Open[r] |
| Contact intrabar, gap exclu | Low[r] <= S | High[r] >= S | INTRABAR | S |
| Aucun contact | Low[r] > S | High[r] < S | Aucun trigger | Aucun fill |

Un stop franchi à l'entrée se déclenche immédiatement après le fill PR #291,
sur e, sans lire High[e], Low[e], Close[e] ou Volume[e]. L'entrée reste FILLED,
sans transformation rétroactive en CANCELLED/REJECTED/NO_TRADE.
Exemple LONG : S=20000, Open[e]=19998.50 : entrée et stop exit à 19998.50,
jamais au niveau favorable périmé 20000. Le prix déjà conservé par l'entrée
suffit ; aucun nouvel accès à Open[e] nécessaire.

ARMED protège immédiatement la barre e après son Open. Pour r=e, la relation
Open[e]>S en LONG / Open[e]<S en SHORT est déjà établie par PR #292 : aucun
second test de gap. Low[e]<=S en LONG / High[e]>=S en SHORT remplit à S.
L'Open de référence pour valider cet extrême est le fill exact retenu de e.

Pour r>e, valider l'Open fini puis tester le gap en premier. Si le gap passe,
remplir à Open[r] et retourner avant toute lecture/validation de Low ou High.
Cela reste vrai avec une OHLCV complète en mémoire ou un extrême ultérieur
absent/invalide. Sinon seulement, consulter l'extrême adverse et tester le
contact inclusif. Toutes les égalités Open/Low/High au niveau S déclenchent.

| Phase d'accès | Champs utilisés |
| --- | --- |
| ENTRY_OPEN breach | Record d'entrée/stop immuable ; aucun input marché |
| Barre e ARMED | bar_index, timestamp_utc, Low (LONG) ou High (SHORT) ; Open[e] retenu |
| Barre ultérieure, gap | bar_index, timestamp_utc, Open ; aucun extrême |
| Barre ultérieure, sans gap | bar_index, timestamp_utc, Open, Low (LONG) ou High (SHORT) |

Aucune lecture de Close, Volume, extrême opposé, is_closed, EMA20, MACD ou ATR.
Hors gap déjà déclenché, LONG exige Open et Low finis avec Low<=Open ; SHORT
Open et High finis avec High>=Open. Extrême absent/non fini/malformé ou Open
ultérieur absent/non fini : FAILED_INVALID_STOP_OBSERVATION, aucun fill.
Les conversions exactes Decimal fini/int/Fraction suivent les conventions V2,
sans float binaire/chaîne/bool ni arrondi. Aucun seuil positif ou distance
supplémentaire ajouté aux observations ultérieures.

`register_structural_stop_execution_v2` exige le stop lié à son fill PR #292
et capture cette provenance dans StructuralStopExecutionBookV2, registre
immuable d'une seule série offline à transmettre aux appels suivants.
BREACHED_AT_ENTRY_OPEN crée directement FILLED_STOP ; ARMED attend sa première
observation e. Réenregistrer une source équivalente conserve son état sans
reset. Un niveau, fill ou provenance modifié sous la même identité est refusé.

`observe_structural_stop_v2` traite une seule observation réelle à la fois,
sans mapping/prefixe futur. Après e, les indices doivent être exactement
r+1, r+2, etc. Un saut d'indice, dont e omise, donne
FAILED_INCOMPLETE_STOP_OBSERVATION avant toute lecture de prix ou d'horloge,
sans présumer un stop intact et sans fill synthétique. Index/horloge invalide,
timestamp non causal ou relecture d'une observation active déjà traitée donne
FAILED_INVALID_STOP_OBSERVATION. Les timestamps doivent être cohérents UTC,
strictement croissants entre observations ; e conserve le timestamp d'entrée.

Aucune durée maximale et aucun reset/expiry à la frontière de session.
Un écart de temps de plusieurs heures/jours entre deux observations consécutives
est valide. Le stop demeure actif puis un Open franchissant S remplit à cet Open.
Les gaps ne créent pas de barres synthétiques. Si aucun gap ne déclenche,
l'observation de l'extrême adverse complet doit être disponible avant son
évaluation OHLC ; le caller ne transmet pas un range futur à l'ouverture.

ENTRY_OPEN est entièrement connu à Open[e], BAR_OPEN_GAP à Open[r]. Un contact
OHLC INTRABAR est survenu pendant r et connu au plus tard à Close[r].
trigger_known_at=NO_LATER_THAN_CLOSE[r] ; exact_intrabar_timestamp=UNKNOWN,
représenté par None. Le timestamp de barre est conservé comme métadonnée,
sans inventer une heure précise de contact.

Après fill : stop_execution_state=FILLED_STOP, terminal. Les échecs
FAILED_INCOMPLETE_STOP_OBSERVATION/FAILED_INVALID_STOP_OBSERVATION sont aussi
terminaux. Les appels ultérieurs rendent le même registre/record avant toute
lecture marché, sans deuxième fill ni réparation rétroactive. Les snapshots
antérieurs et le stop_state_at_entry restent inchangés.

Le record conserve source_regime_event_types/index/timestamp/direction,
pullback index/timestamp/ema_reference, confirmation index/timestamp,
entry index/timestamp/price, initial_stop_price, structural_extreme,
tick_size, stop_buffer_ticks, stop_state_at_entry, trigger_bar_index,
trigger_bar_timestamp, trigger_phase, trigger_known_at, base_stop_fill_price,
protective_action et STOP_MARKET. Le InitialStopAtEntryV2 complet conserve
aussi les records imbriqués de stop initial, confirmation et exécution.
Toutes ces données sont immuables ; aucune mutation du niveau structurel.

Si les observations se terminent avec ARMED, aucun stop fill synthétique.
observation=None retourne le même registre ARMED, sans expiration, clôture
forcée ou résultat de performance inventé. La politique de fin de données
reste à formaliser séparément.

Aucun coût, commission, spread, slippage ou adverse-fill ticks : seulement
base_stop_fill_price. Aucun take profit, sortie EMA20, breakeven, trailing,
time stop, session close exit, Risk Engine ou sizing. La priorité intrabar
avec une autre sortie sera une gate distincte lorsqu'une telle sortie existera.
Aucun replay ou accès OOS ; aucune autorisation broker/paper trading.

## Une position par série et admission des nouveaux signaux — décision du propriétaire

Le 2026-10-04, `EMA_PULLBACK_V2_OPEN_POSITION_SIGNAL_POLICY_REQUIRED` est
acquittée par `EMA_PULLBACK_V2_OPEN_POSITION_SIGNAL_POLICY`. Baseline initiale
pré-replay non optimisée, indépendante des résultats V1/V1A/V1B et non ajustée
sur MNQ 03-26 ou MNQ 06-26.

```text
MAX_SIMULTANEOUS_POSITIONS_PER_SERIES = 1
PYRAMIDING = DISABLED
HEDGING = DISABLED
FLIP_ON_OPPOSITE_SIGNAL = DISABLED
SCALE_IN = DISABLED
SIGNAL_QUEUE_WHILE_OPEN = DISABLED
```

Le scope est une instance de stratégie et un instrument/une série. Aucun
plafond global de portefeuille, agrégation de compte ou exposition croisée.
`OpenPositionSignalPolicyBookV2` porte explicitement strategy_instance_id et
series_id ; le caller conserve le registre immuable de ce seul scope.

| État / observation | Résultat |
| --- | --- |
| FLAT + nouveau régime complet LONG ou SHORT | Admission dans le lifetime/pullback V2 déjà figé |
| EntryExecution FILLED LONG | OPEN_LONG |
| EntryExecution FILLED SHORT | OPEN_SHORT |
| OPEN_LONG ou OPEN_SHORT + nouvelle opportunité de l'un ou l'autre sens | SUPPRESSED_POSITION_OPEN ; aucun contexte exécutable |
| StructuralStop FILLED_STOP de cette position | FLAT |
| Stop ARMED ou échec de monitoring sans fill | Position conservée ouverte |

Un événement, contexte, pullback consommé, confirmation ou exécution PENDING
n'ouvre aucune position. Seul le fill d'entrée canonique PR #291 ouvre la
position ; seul un fill terminal d'une sortie formelle la ferme. À cette gate,
la seule sortie formalisée est FILLED_STOP PR #293. Les futures sorties devront
respecter cette même machine d'état.

Le blocage intervient avant `advance_ema20_pullback_v2` et toute création de
RegimeEventContextV2. Pendant OPEN, la composition des événements bruts reste
disponible en télémétrie, mais le lifetime/pullback n'est pas invoqué et aucun
mapping OHLC historique/futur n'est consulté pour une nouvelle opportunité.
Les EMA20, MACD, impulsions et retournements bruts peuvent continuer à être
calculés séparément pour l'audit. Même une composition AMBIGUOUS reste
non actionnable ; elle ne ferme ni ne retourne la position.

Tout nouveau signal LONG/SHORT pendant OPEN est définitivement perdu pour
l'entrée : aucun empilement, couverture, retournement, scale-in, augmentation
de quantité, recalcul de prix moyen, ordre inverse pending, queue, report ou
réactivation ultérieure. À l'entrée, le lifetime exécutable est retiré ; ses
snapshots et la consommation antérieure restent immuables en audit. Après la
sortie, aucun ancien événement/contexte/pullback/confirmation/pending né pendant
OPEN n'est restauré. Une nouvelle chaîne doit commencer par un régime complet
admis après le retour d'éligibilité.

Ordre causal strict pour une nouvelle barre clôturée r :

1. Résoudre le stop de la position existante, à son Open ou pendant r.
2. Mettre à jour l'état de position à partir du fill terminal éventuel.
3. Composer/admettre les événements de Close[r] selon cet état.
4. Seulement si FLAT, appliquer le lifetime/pullback V2 déjà figé.

Une sortie à Open[r] ou INTRABAR sur r permet donc un nouveau régime formé
à Close[r]. Si la position reste ouverte, ce régime est supprimé. Le nouveau
contexte admis à Close[r] ne peut jamais être consommé sur sa propre barre r.

BREACHED_AT_ENTRY_OPEN conserve l'entrée FILLED à Open[e], puis son véritable
stop FILLED_STOP au même Open[e] : OPEN_LONG/OPEN_SHORT puis FLAT, avec les deux
records liés et leur prix de base exact. Aucune annulation rétroactive ni
assimilation à NO_TRADE. La résolution à ENTRY_OPEN n'utilise aucun OHLCV de e ;
le nouveau régime de Close[e] est ensuite admissible.

`apply_position_entry_fill_v2` exige le fill canonique et son pullback réellement
admis/consommé dans le registre, après sa confirmation clôturée. Cela refuse
une chaîne externe issue d'un signal supprimé ou une ancienne source restaurée.
Le stop lié doit être dans son état connu à l'Open d'entrée : aucun résultat
intrabar ou futur déjà précalculé ne peut y être injecté.
`resolve_position_stop_v2` réutilise exclusivement la gate PR #293 et ses champs
autorisés, sans modifier le niveau ou le prix du fill. Monitoring invalide ou
absent ne fabrique pas une sortie/FLAT. Les gaps temporels ne font pas expirer
une position ni son stop ; les observations restent séquentielles.

`advance_open_position_signal_policy_v2` assure l'ordre sortie/état/admission,
puis conserve la décision de Close[r]. Répéter un fill canonique ou une même
clôture rend le même registre, sans deuxième position ni deuxième transition
FLAT. Rejouer un fill d'une position déjà clôturée ne la rouvre pas. Modifier
une provenance ou les événements sous une identité déjà traitée est refusé.
Les clocks et indices ne peuvent reculer et aucune observation future de stop
n'est acceptée pour une décision courante.

Suppression conservée : signal_bar_index, signal_timestamp, signal_direction,
source_event_types, position_state, suppression_reason=POSITION_ALREADY_OPEN,
active_position_entry_bar_index et active_position_direction. Les records
d'entrée/stop/sortie conservent immuablement l'événement source, le pullback et
son EMA exacte, la confirmation et le fill d'entrée. Aucun record supprimé ne
sert à construire une chaîne d'entrée complète.

Aucun replay, ouverture OOS, calibration MNQ, broker ou ordre réel. Aucun Risk
Engine, sizing, quantité, coût, take profit, breakeven ou trailing ajouté dans
cette gate. V2 reste PRE_FORMALIZATION, sans performance évaluée.

## Risk Engine et quantité MNQ à la confirmation — décision du propriétaire

Le 2026-10-04, `EMA_PULLBACK_V2_RISK_ENGINE_POSITION_SIZING_REQUIRED` est
acquittée par `EMA_PULLBACK_V2_RISK_ENGINE_POSITION_SIZING`. Baseline initiale
pré-replay non optimisée, indépendante de V1/V1A/V1B et sans ajustement à partir
des résultats MNQ 03-26 ou MNQ 06-26 déjà utilisés.

```text
INSTRUMENT = MNQ
TICK_SIZE = Fraction(1, 4)
POINT_VALUE_USD = Fraction(2, 1)
TICK_VALUE_USD = Fraction(1, 2)
PLANNED_RISK_BUDGET_USD = Fraction(100, 1)
RISK_BUDGET_KIND = PLANNED_STRUCTURAL_PRICE_RISK_BUDGET
MIN_CONTRACTS = 1
MAX_CONTRACTS = 2
NO_RESIZING_AFTER_CONFIRMATION = TRUE
```

La décision est entièrement connue à Close[q], avec confirmation formellement
qualifiée, direction, stop initial EVALUATED connu à cette clôture et position
FLAT. q reste k+1 ou k+2. La seule référence de prix est Close[q]. La gate ne
consulte aucun Open/High/Low/Close/Volume de q+1 ni aucune autre barre future.
Le stop initial doit conserver la provenance exacte de cette confirmation,
la fenêtre k...q, son tick/buffer figé et aucun état d'armement futur injecté.

| Direction | Distance structurelle prévue | Relation strictement exigée |
| --- | --- | --- |
| LONG | Close[q] - initial_stop_price | Close[q] > initial_stop_price |
| SHORT | initial_stop_price - Close[q] | Close[q] < initial_stop_price |

Égalité, mauvaise relation ou distance non positive : REJECT avec
INVALID_STRUCTURAL_RISK_DISTANCE. Close[q] et initial_stop_price sont convertis
exactement en Fraction ; leurs quotients par Fraction(1,4) doivent être des
entiers exacts. Sinon INVALID_MNQ_TICK_GRID, sans arrondi au tick voisin.
Les conversions suivent les conventions V2 Decimal fini/int/Fraction ; aucun
float binaire, chaîne, bool ni arrondi intermédiaire. Un contexte EMA rationnel
peut avoir une référence hors grille : ce n'est pas le prix brut du sizing.

```text
risk_per_contract_usd = stop_distance_points * Fraction(2, 1)
raw_quantity = floor(Fraction(100, 1) / risk_per_contract_usd)
quantity = min(2, raw_quantity)
quantity < 1 => REJECT, RISK_PER_CONTRACT_EXCEEDS_BUDGET
otherwise => APPROVE
planned_total_risk_usd = quantity * risk_per_contract_usd <= Fraction(100, 1)
```

Le floor est exact, sans round-to-nearest. Sur APPROVE, quantity est un entier
de 1 à 2 et planned_total_risk_usd est strictement positif, au plus 100 USD.

| Risque prévu par contrat | Quantité / décision |
| --- | --- |
| 0 < risque <= 50 USD | 2 contrats |
| 50 < risque <= 100 USD | 1 contrat |
| risque > 100 USD | REJECT ; quantité approuvée 0 |

50 USD exactement donne 2 contrats ; 100 USD exactement donne 1. Une distance
de 15 points donne 30 USD/contrat, raw_quantity=3, quantité plafonnée à 2 et
risque total 60 USD. 35 points donne 70 USD/contrat et 1 contrat. 55 points
donne 110 USD/contrat, raw_quantity=0 et REJECT. Close[q]=20010 et stop LONG
19990 donnent exactement 20 points, 40 USD/contrat et 2 contrats pour 80 USD.
SHORT est le miroir exact de LONG.

Le budget de 100 USD couvre seulement la distance entre la référence de
confirmation et le stop structurel. Il ne garantit jamais une perte réalisée
maximale de 100 USD : gap, STOP_MARKET, futurs coûts et slippage peuvent la
dépasser. Aucun coût n'est incorporé dans ce budget initial.

Rejet fail-closed aussi pour instrument différent de MNQ, confirmation absente
ou non qualifiée, stop absent/non EVALUATED, provenance de stop incohérente,
Close[q] ou stop absent/non fini, observation q non clôturée/incohérente,
position non FLAT ou état de position invalide. Aucun fallback fixe de 1/2
contrats ni stop arbitraire. Les arguments de clock exigent une clôture UTC
réelle ; une invocation non causale est refusée avant lecture marché.

`register_risk_position_sizing_v2` conserve RiskPositionSizingBookV2 immuable
pour une instance de stratégie et une série. Il vérifie le même scope, le
pullback réellement admis/consommé par la politique PR #294 et la décision de
position à Close[q]. Une chaîne supprimée ou une politique absente/stale ne
peut autoriser une nouvelle entrée. Une position déjà ouverte est rejetée
avant toute lecture du prix de sizing.

Seul APPROVE appelle `register_entry_execution_v2` de PR #291 et crée PENDING
pour Open[q+1], avec quantité déjà figée. Les règles d'exécution, clocks,
validation d'Open et états terminaux PR #291 restent inchangés. REJECT ne crée
aucun record d'exécution et rend l'opportunité REJECTED_BY_RISK_ENGINE,
terminale pour tout le pullback consommé : aucun retry à q+1, q+2 ou plus tard.
Les appels répétés retournent la décision enregistrée avant toute relecture de
prix/stop, sans adaptation aux résultats ni reconsidération d'une source rejetée.

`execute_risk_approved_entry_open_v2` délègue seulement l'Open autorisé à PR #291.
RiskSizedEntryRecordV2 lie le fill réel à sa décision canonique et expose sa
quantité figée. Aucun redimensionnement après confirmation, que l'Open élargisse,
réduise ou franchisse la distance au stop. BREACHED_AT_ENTRY_OPEN conserve
l'entrée FILLED puis la sortie au même Open selon PR #292/#293, sans annulation
rétroactive ni déplacement du stop. Les diagnostics actual_entry_price et
actual_entry_to_stop_distance_points sont dérivés après fill et ne modifient
jamais la décision ou la quantité. La distance diagnostique est signée :
zéro/négative si l'entrée ouvre au niveau/au-delà du stop.

Le record de décision conserve instrument, direction, familles/index/timestamp
du régime source, pullback index/timestamp/ema_reference, confirmation
index/timestamp, known_at=q/timestamp[q], sizing_reference_price=Close[q],
initial_stop_price, stop_distance_points, point_value_usd, risk_per_contract_usd,
risk_budget_usd/kind, raw_quantity, approved_quantity, planned_total_risk_usd,
decision/rejection_reason et état de position à la décision. Les snapshots
complets de source consommée, confirmation et stop sont conservés. Un rejet
conserve les champs déjà validés et aucune quantité autorisée/risque total.
Le registre possède les seules exécutions autorisées et leurs quantités ; une
provenance altérée ou une exécution sans APPROVE est refusée. Chaque fill garde
exactement une quantité, sans duplicate ou résurrection après expiry.

Aucun pourcentage d'equity, PnL courant/passé, série gagnante/perdante,
martingale/anti-martingale, volatilité, Kelly, score ou famille de régime dans
le calcul : même risque structurel, même quantité. Aucun changement de stop,
coût, commission, spread, slippage, take profit, breakeven ou trailing ajouté.
Aucun replay, accès OOS, broker, ordre réel ou autorisation paper trading.
V2 reste PRE_FORMALIZATION, sans performance évaluée.

## Frais et slippage MNQ des fills offline — décision du propriétaire

Le 2026-10-04, `EMA_PULLBACK_V2_FEES_AND_SLIPPAGE_MODEL_REQUIRED` est acquittée
par `EMA_PULLBACK_V2_FEES_AND_SLIPPAGE_MODEL`. Baseline initiale pré-replay
non optimisée, exclusivement comptable/exécution offline. Les signaux, le
stop structurel, les fills déterministes de base et la quantité approuvée
par le Risk Engine demeurent inchangés.

La convention de coûts V1 est volontairement reprise pour comparer les futurs
résultats à convention identique : 0.51 USD/contrat/fill et un tick adverse à
chaque fill, sans débit séparé de spread. Ce choix explicite ne constitue
aucune calibration de performance V2 ; aucun résultat MNQ ne sert à l'ajuster.
Le runtime V1 et ses résultats figés ne sont pas modifiés ni invoqués pour
comptabiliser V2. Aucun tarif broker réel n'est recherché.

```text
TICK_SIZE = Fraction(1, 4)
POINT_VALUE_USD = Fraction(2, 1)
TICK_VALUE_USD = Fraction(1, 2)
FEE_PER_CONTRACT_PER_FILL_USD = Fraction(51, 100)
ADVERSE_SLIPPAGE_TICKS_PER_FILL = 1
ADVERSE_SLIPPAGE_POINTS_PER_FILL = Fraction(1, 4)
SPREAD_MODEL = ABSORBED_IN_SLIPPAGE
EXTRA_SPREAD_CHARGE = Fraction(0)
SLIPPAGE_ACCOUNTED_EXACTLY_ONCE = TRUE
NO_POST_CONFIRMATION_RESIZING = TRUE
ROUND_TO_CENTS = ROUND_HALF_UP
```

Ne jamais écraser execution_price_before_costs ou base_stop_fill_price.
FillCostRecordV2 conserve séparément base_fill_price et
effective_fill_price_after_slippage, avec action, quantity, slippage_ticks,
fee_usd et slippage_cost_usd diagnostique. Le tick est appliqué exactement
une fois au prix de base de chaque fill effectivement exécuté.

| Action offline | Cas | Prix effectif |
| --- | --- | --- |
| BUY | Entrée LONG | base + Fraction(1,4) |
| SELL_SHORT | Entrée SHORT | base - Fraction(1,4) |
| SELL | Stop LONG | base - Fraction(1,4) |
| BUY_TO_COVER | Stop SHORT | base + Fraction(1,4) |

Pour chaque fill : fee_usd=quantity*Fraction(51,100) et coût économique du
slippage=quantity*Fraction(1,2). L'aller-retour explicite est 1.02 USD pour
1 contrat et 2.04 USD pour 2 contrats ; le slippage économique de deux fills
est respectivement 1.00 et 2.00 USD, déjà incorporé aux prix effectifs.
Aucun coût de spread ou seconde soustraction du slippage dans le PnL.

Entrée LONG de base 20000 donne 20000.25 effectif ; entrée SHORT donne
19999.75. Stop LONG de base 19990 donne 19989.75 effectif ; stop SHORT
de base 20010 donne 20010.25. Gap LONG : stop structurel 20000, prochain
Open 19995 => base_stop_fill_price=19995 selon PR #293, puis prix effectif
19994.75. Ne jamais remplacer cette base par l'ancien niveau 20000.

BREACHED_AT_ENTRY_OPEN conserve les deux véritables fills au même Open de
base, entrée puis stop immédiat. Pour 1 MNQ LONG à Open=20000, prix effectifs
20000.25/19999.75 => perte de prix de 1.00 USD et frais de 1.02 USD, donc
net_realized_pnl_usd=-Fraction(202,100). Pour 2 MNQ : -Fraction(404,100).
SHORT est le miroir exact. Aucun trade annulé ou PnL nul artificiel.

```text
LONG gross_price_pnl_usd =
    (effective_exit - effective_entry) * Fraction(2,1) * approved_quantity
SHORT gross_price_pnl_usd =
    (effective_entry - effective_exit) * Fraction(2,1) * approved_quantity
total_fees_usd = entry_fee + exit_fee
net_realized_pnl_usd = gross_price_pnl_usd - total_fees_usd
```

diagnostic_total_slippage_cost_usd est conservé pour l'audit uniquement.
Il ne doit pas être soustrait du gross_price_pnl_usd calculé avec les prix
effectifs. Les records calculent le PnL exact à partir de ces prix et des
frais seuls, sans cumul dépendant du nombre d'appels.

FeesAndSlippageBookV2 conserve un registre immuable pour une instance de
stratégie et une série, de même scope que RiskPositionSizingBookV2.
`account_entry_fill_v2` exige une source canonique du registre de risque et
son véritable RiskSizedEntryRecordV2. Une confirmation APPROVE encore PENDING,
un REJECT, une expiry ou un input d'exécution invalide sans fill ne paie rien
et ne crée aucun record comptable. Seul un fill réel ajoute une entrée comptable.
La quantité provient exclusivement de approved_quantity, sans redimensionnement,
réduction/augmentation ou rejet rétroactif par les coûts.

Enregistrement immédiat à l'entrée : prix de base/effectif, frais, tick de
slippage et coût diagnostique. Tant qu'aucune sortie formelle n'est remplie,
exit_type, stop_fill, exit, gross_price_pnl_usd et net_realized_pnl_usd sont
None. Les frais d'entrée existent déjà, mais aucun PnL de trade réalisé ou
prix de sortie n'est synthétisé, notamment en fin de données.

`account_structural_stop_fill_v2` réutilise exclusivement un FILLED_STOP
canonique de PR #293 ; c'est la seule sortie actuellement formalisée.
ARMED, monitoring invalide/incomplet ou absence de fill ne produit aucun coût
d'exit ni PnL réalisé. Les liens entrée/stop et leurs métadonnées doivent
correspondre aux sources originales ; aucune lecture de barres/prix futurs,
bid/ask ou mark price. Ce modèle ne déclenche aucun stop et ne change pas
sa règle de trigger/fill, son niveau ou son moment causal.

TradeCostRecordV2 conserve le RiskSizedEntryRecordV2 complet (régime, pullback,
EMA, confirmation, décision de risque et entrée), les coûts d'entrée et,
lorsqu'il existe, le StructuralStopFillRecordV2 complet et ses coûts d'exit.
Il expose quantity, exit_type=STRUCTURAL_STOP, total_fees_usd,
diagnostic_total_slippage_cost_usd, gross_price_pnl_usd et net_realized_pnl_usd.
Les snapshots et prix de base restent immuables. Recompter la même entrée ou
sortie rend le même registre, sans deuxième débit ; une provenance modifiée
sous la même identité est refusée. Un ancien snapshot de stop non rempli
ne peut effacer un exit déjà comptabilisé.

Le budget prévu de PR #295 reste 100 USD de risque de prix structurel
pré-trade, distinct des coûts. Les frais/slippage ne recalculent jamais la
quantité ou le budget. Risque prévu versus perte nette réalisée restent
auditables séparément ; à exactement 100 USD de risque prévu sur 2 contrats,
un stop sans gap à la distance prévue donne -104.04 USD nets. Gaps, slippage
et frais peuvent dépasser davantage 100 USD, sans masquage de cette perte.

Prix, valeurs point/tick, slippage, frais et PnL restent Fraction exacts,
sans float ni arrondi intermédiaire. `report_usd_cents_v2` convertit seulement
la sortie monétaire en Decimal à deux décimales avec HALF_UP ; la valeur
Fraction interne demeure disponible et inchangée. L'arrondi se fait par
arithmétique entière exacte, indépendante de la précision du contexte Decimal,
y compris aux demi-centimes positifs/négatifs et pour les rationnels périodiques.
La comptabilité n'ajoute aucune réparation de grille ou condition de prix
post-fill aux règles déjà figées de PR #291/#293.

Aucun take profit, breakeven, trailing, sortie EMA/session, daily profit lock,
max daily trades, equity, frais broker live, bid/ask replay ou slippage dynamique.
Aucun replay, accès OOS, ajustement de performance MNQ, broker ou ordre réel.
V2 reste PRE_FORMALIZATION ; la rentabilité n'est pas évaluée.

## Prochaine ambiguïté — politique de sortie V2

`BLOCKED_HUMAN_GATE — EMA_PULLBACK_V2_EXIT_POLICY_REQUIRED`

Décider séparément l'architecture de sortie V2 en conservant le stop structurel,
son fill et les conventions de coûts déjà figés. Aucun take profit, breakeven,
trailing, sortie EMA/session ou arbitrage intrabar n'est ajouté automatiquement.
La politique de fin de données doit aussi être décidée explicitement avant une
stratégie V2 complète. Sans replay ni ouverture OOS.
