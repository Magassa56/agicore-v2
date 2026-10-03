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
qualifié n'est pas encore un signal d'entrée. L'ordre désormais figé est :
événement complet, contexte actif, pullback qualifié et consommation unique,
puis confirmation prix/momentum sur une clôture ultérieure. L'exécution d'entrée
reste à définir séparément.

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

## Prochaine ambiguïté — exécution d'entrée V2

`BLOCKED_HUMAN_GATE — EMA_PULLBACK_V2_ENTRY_EXECUTION_REQUIRED`

Quand et comment une confirmation qualifiée à Close[q] devient-elle une entrée
exécutable ? Figer séparément son instant causal, son mode/prix d'exécution et
le traitement d'une prochaine barre indisponible. Aucune règle d'exécution
n'est choisie ici ; les sorties restent hors de cette prochaine gate. Aucun
replay ni ouverture OOS.
