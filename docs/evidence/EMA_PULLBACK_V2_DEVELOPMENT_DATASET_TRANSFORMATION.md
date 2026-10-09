# EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION — préengagement

`STATUS = PASS_PRECOMMITTED`. Une seule transformation est préengagée :
filtrer les lignes par timestamp UTC End-of-Bar, sans modifier leurs octets.
L'exécution réelle est **interdite dans cette PR**. La fusion ne l'autorise pas.
`NEXT = EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION_REQUIRED`.

| Binding | SHA-256 exact |
| --- | --- |
| Stratégie V2 version 1 | `965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a` |
| Protocole DEVELOPMENT | `68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402` |
| FULL_PARENT_RAW | `6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5` |
| Source `tools/ema_pullback_v2_dataset_transformation.py` | `3ec9aadf9e4852d1ad4ef10ad6fd3f958d716a9de5df792a744c6926cf26d44c` |
| TRANSFORMATION_PROTOCOL_SHA256 | `bb47e6a9b867dd6e35516f5c43e56b9259aa00c526deb4978b050783a1e47f62` |

Le JSON canonique de ce protocole est
`EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION.json`. UTF-8, clés triées,
JSON compact sans NaN, LF final. Son SHA-256 porte sur les octets exacts et
reste hors du payload pour éviter une auto-référence. Toute modification du
code exige un nouveau préengagement et un nouveau hash ; aucune variante locale.

## Parent immuable vérifié en lecture seule

Pièce jointe `MNQ 09-26.Last.txt` : identité recomputée depuis les octets,
**5 416 523 octets**, **101 962 lignes de données**, première ligne
`2026-06-07T22:01:00Z`, dernière ligne `2026-09-18T13:31:00Z`.
SHA recalculé conforme avant et après l'audit ; aucun octet du parent modifié.

Les compteurs sont à zéro : lignes malformées, timestamps invalides,
doublons, ordre non chronologique, OHLC invalides, valeurs non finies,
volume négatif/non entier, prix hors grille exacte MNQ 0.25 et timestamps
hors structure minute. **326 intervalles** entre observations dépassent
une minute : ils sont constatés sans les combler, interpoler ni reconstruire.
Ils ne deviennent pas un critère de sélection des lignes.

La mission reçue le 2026-10-09 à 12:27:28+02:00 fournit explicitement
`NINJATRADER_END_OF_BAR`, `UTC`, le début de session canonique et la terminaison.
Ces métadonnées ne sont pas inférées des heures filesystem, des prix ou
d'une performance. La partition a été auditée en lecture seule, sans
construction d'une liste de lignes retenues ni création de RAW dérivé.
Les résultats figurent dans le JSON avec leur SHA d'audit. Le rapport de
filiation de la PR #305 reste un **snapshot historique de blocage**, pas
la preuve courante de l'identité des octets maintenant reçus.

## Prédicat unique, inclusif

```text
Keep row iff
    timestamp >= 2026-06-18T22:01:00Z
    AND
    timestamp <= 2026-09-18T13:30:00Z
```

Le début de session est `2026-06-18T22:00:00Z`. Avec le timestamp de fin de
bougie minute, la première borne admissible est 22:01:00Z. La dernière
borne est exactement la terminaison contractuelle du 18 septembre à
13:30:00Z. Les deux égalités passent. Aucun autre prédicat n'est permis.

| Invariant audit préalable | Valeur |
| --- | ---: |
| Lignes parent | 101 962 |
| Retirées avant la borne | 12 120 |
| Retirées après la borne | 1 |
| Retenues attendues | 89 841 |

`101962 = 12120 + 89841 + 1`. Ces nombres sont des invariants de données,
pas des résultats de performance. Le prix et le volume ne participent
jamais au choix des lignes. Une ligne invalide, même hors fenêtre,
**fait échouer toute l'opération** ; elle n'est pas filtrée silencieusement.

## Conservation et fail-closed

L'implémentation valide tout le parent avant de construire un sous-ensemble.
Le SHA, la taille, le nombre de lignes, les bornes du parent et les trois
compteurs de partition doivent correspondre exactement. UTC/End-of-Bar
est obligatoire. Tous les contrôles de structure doivent rester PASS.
La grille MNQ est validée en Fraction exacte à partir du texte décimal.

Les lignes admissibles gardent leur payload OHLCV, leur timestamp textuel,
leur ordre, leurs fins de ligne CRLF/LF et l'absence éventuelle de LF final.
Aucun tri, dedup, arrondi, normalisation, correction, ajout de ligne, forward
fill, interpolation, filtre prix/volume/signal ou reconstruction de session.
Le parent n'est jamais réécrit. Une sortie existante est refusée.

## Approbation et exécution séparées

L'outil vérifie uniquement les documents par défaut. La commande suivante
ne lit aucun parent RAW et n'écrit aucune donnée transformée :

```bash
python -m tools.ema_pullback_v2_dataset_transformation \
  --protocol-sha256 bb47e6a9b867dd6e35516f5c43e56b9259aa00c526deb4978b050783a1e47f62
```

Le JSON contient le template exact de la commande future avec `--execute`,
le nom de gate, le chemin d'entrée immuable et un **nouveau** chemin de sortie.
Le flag de gate constate l'intention du caller ; il ne donne pas une
autorisation à lui seul. Cette commande reste interdite pendant ce préengagement.
Aucune option n'autorise des bornes ou des prédicats alternatifs.

La prochaine gate autorisée devra enregistrer l'exacte commande, les
paramètres, les hashes parent/code/protocole, les comptes avant/après, le
SHA/taille du dérivé et la preuve que les lignes retenues sont inchangées.
La sortie CLI expose ces hashes et les invariants dans un reçu JSON.
Le hash et la taille du dérivé restent **NONE** jusqu'à l'exécution réelle.

## Tests et état de filiation

Les tests utilisent exclusivement des OHLCV inventés. Ils couvrent les
bornes inclusives, les minutes juste dehors, la conservation des fins de
ligne/lexèmes, les gaps préservés, l'absence de filtre prix/volume, chaque
classe d'entrée invalide, les incohérences d'identité/comptage/sémantique,
les hashes de source/protocole/stratégie, l'immutabilité, le défaut sans
exécution et les protections de fichier. Deux exécutions synthétiques
neuves donnent les mêmes bytes, hash et audit.

`REAL_PARENT_TRANSFORMATION = NOT_EXECUTED`.
`REAL_STRATEGY_REPLAY = NOT_EXECUTED`.
`EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE = BLOCKED_HUMAN_GATE`.
Aucun dataset canonique, signal V2, comptage de trades, PnL, optimisation,
OOS ou broker. Le préengagement n'établit pas les autres preuves fournisseur,
version NinjaTrader, merge/template/session ou la filiation du futur dérivé.
Après l'exécution séparément autorisée, reprendre la gate de filiation ;
aucun replay n'est automatiquement permis.

Validation locale de ce préengagement : 139 tests ciblés synthétiques/metadata
PASS en 0.61s (51 nouveaux cas, filiation et protocole DEVELOPMENT inclus),
Ruff check/format PASS, vérification CLI des documents sans RAW PASS,
sérialisation et hashes conformes, périmètre de cinq fichiers et diff-check
PASS. Aucune transformation réelle exécutée. La CI complète est requise
avant fusion du préengagement.
