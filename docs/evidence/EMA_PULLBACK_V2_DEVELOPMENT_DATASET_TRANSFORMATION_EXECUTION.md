# EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION

```text
PHASE: EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION
STATUS: PASS
REAL_PARENT_TRANSFORMATION: EXECUTED_ONCE
REAL_STRATEGY_REPLAY: NOT_EXECUTED
NEXT: EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED
```

L’autorisation explicite AGIcoreManager a été reçue le 2026-10-09 à
10:57:20Z. La transformation préengagée par [PR #306](https://github.com/Magassa56/agicore-v2/pull/306)
a été invoquée exactement une fois, sans modification du code ni des paramètres,
depuis le merge `7e46769f3b12ba8cf71e20cdf99b057bef4c5310`.
Le processus a commencé à `2026-10-09T11:01:36.680914Z` et s’est
terminé à `2026-10-09T11:01:38.754119Z`, code 0, stderr vide.
Ces horloges sont celles du processus local, jamais un timestamp d’export NinjaTrader.

## Chaîne de hashes immuable

| Objet | SHA-256 |
| --- | --- |
| Manifest stratégie | `965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a` |
| Protocole DEVELOPMENT | `68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402` |
| Protocole transformation | `bb47e6a9b867dd6e35516f5c43e56b9259aa00c526deb4978b050783a1e47f62` |
| Source transformation | `3ec9aadf9e4852d1ad4ef10ad6fd3f958d716a9de5df792a744c6926cf26d44c` |
| Parent RAW | `6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5` |
| Dérivé RAW | `ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126` |
| Stdout original | `947b176f39d51cf12a65e729df176a66de6e282dfff600768a4d96c383b7b363` |
| Source de l’audit indépendant, incluse dans le JSON | `5d53cb9abe45c510ef2533f0b068d14b012bc0a9cb2c2d0cd74bd41dda3f44f5` |
| Résultat de l’audit indépendant, inclus dans le JSON | `2bb3a6169639336f48a34bb145daeb35627ae800b70989a7fb1a58d198852340` |
| Reçu JSON canonique | `2b4c6b86da5749545a55b6173916a26be88644b252afb9afcaf6f86deb7ccbf1` |

Le reçu JSON est sérialisé en UTF-8, clés triées, séparateurs compacts,
`allow_nan=false`, suivi d’un LF. Son digest est externe au payload.
Les quatre fichiers figés ont les mêmes hashes avant et après l’exécution.

## Commande réellement exécutée

```bash
python -m tools.ema_pullback_v2_dataset_transformation --protocol docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION.json --protocol-sha256 bb47e6a9b867dd6e35516f5c43e56b9259aa00c526deb4978b050783a1e47f62 --execute --execution-gate EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION --input '/workspace/scratch/889b77c10552/upload/MNQ 09-26.Last.txt' --output /workspace/scratch/889b77c10552/transformation-execution/MNQ_09-26_DEVELOPMENT_CANONICAL_V1.Last.txt
```

Les paramètres sont exactement ceux autorisés. Seuls les chemins d’entrée et
de nouvelle sortie remplacent les placeholders. Les deux RAW sont hors du
dossier `data/` du dépôt et ne sont pas versionnés. Un marqueur exclusif a
réservé l’invocation n°1 avant lancement ; aucun deuxième lancement n’a été effectué.
Le stdout exact est conservé sous forme canonique dans le reçu JSON et lié à son hash.

## Identité et partition

| Contrôle | Résultat |
| --- | --- |
| Parent | `MNQ 09-26.Last.txt` |
| SHA parent avant/après | Identique |
| Taille parent | 5 416 523 octets |
| Lignes parent | 101 962 |
| Retirées avant la fenêtre | 12 120 |
| Retenues | 89 841 |
| Retirées après la fenêtre | 1 |
| Lignes retenues modifiées | 0 |
| Nouveau fichier | `MNQ_09-26_DEVELOPMENT_CANONICAL_V1.Last.txt` |
| Taille dérivé | 4 785 270 octets |
| Lignes dérivé | 89 841 |
| Premier timestamp UTC End-of-Bar | `2026-06-18T22:01:00Z` |
| Dernier timestamp UTC End-of-Bar | `2026-09-18T13:30:00Z` |

La seule sélection est `timestamp >= 2026-06-18T22:01:00Z` ET
`timestamp <= 2026-09-18T13:30:00Z`, bornes inclusives. L’ordre original,
les valeurs et les fins de ligne ont été préservés. Chaque ligne du dérivé
a été comparée directement à sa ligne parent correspondante, de la ligne
parent 12 121 à la ligne 101 961 inclusivement. Le hash incrémental de ces
lignes parent est identique au hash du dérivé.

## Deuxième audit indépendant

Un parseur en bibliothèque standard, sans import du transformateur ou de V2,
a relu séparément le parent et le dérivé. Il ne construit ni n’écrit de RAW dérivé.
Sa source complète et son résultat sont inclus dans le JSON canonique.
Les bytes du parent et du dérivé ont encore été vérifiés inchangés pendant l’audit.

| Compteur sur le dérivé | Valeur |
| --- | --- |
| malformed_rows | 0 |
| invalid_timestamps | 0 |
| duplicate_timestamps | 0 |
| non_chronological_rows | 0 |
| invalid_ohlc | 0 |
| nonfinite_values | 0 |
| negative_volume | 0 |
| noninteger_volume | 0 |
| off_mnq_0_25_tick_grid | 0 |
| non_minute_timestamps | 0 |

Les mêmes compteurs sont nuls pour le parent. Les contrôles numériques utilisent
Decimal vers Fraction exacte, jamais un arrondi. Le fuseau UTC et la sémantique
NinjaTrader End-of-Bar reposent sur l’attestation explicite liée au préengagement ;
le texte des lignes seul ne prouve pas un fuseau.

Le parent possède 326 intervalles de plus d’une minute ; le dérivé en conserve 71
à l’intérieur de la fenêtre. Leurs bornes et durées sont inventoriées dans le
JSON. Aucun gap n’a été comblé. Leur classification finale reste une obligation
de filiation ; cet audit ne reconstruit pas de session.

## Portée et suite

Aucun signal V2, comptage de trades, PnL, replay, screening, optimisation,
accès OOS ou broker. La transformation ne calcule aucune performance.
La source de transformation, le manifest stratégie et les protocoles restent inchangés.

`CANONICAL_DATASET_ID = NONE`. Le nom recommandé du dérivé contient « CANONICAL »,
mais il ne lui accorde pas ce statut. `DATASET_LINEAGE = BLOCKED_HUMAN_GATE`
jusqu’à sa gate séparée et ses preuves restantes. L’ancien manifeste de filiation
référencé dans le JSON est un snapshot historique BLOCKED, pas le présent audit.

La prochaine gate est exclusivement
`EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED`, avec ce reçu et le dérivé
immuable. Aucune exécution stratégique n’est autorisée par ce PASS.
