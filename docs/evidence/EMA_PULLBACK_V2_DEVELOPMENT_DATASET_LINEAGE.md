# EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE

```text
PHASE : EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE
STATUS : PASS — révision 6, 2026-10-09T17:41:32.304085Z
CANONICAL_DEVELOPMENT_CONTRACT : MNQ 09-26
CANONICAL_DATASET_ID : mnq-09-26-minute-last-development-ee6eeed4-v1
DATASET_ROLE : EXPOSED_DEVELOPMENT
SOURCE_RAW_SHA256 : ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126
DATASET_LINEAGE_MANIFEST_SHA256 : d9a5d15a8746491391ba13417a099801ba6add44be1f275d2ca9e699adf56b89
REAL_STRATEGY_REPLAY : NOT_EXECUTED
NEXT : EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION_REQUIRED
```

## Portée et preuves conservées

Cette révision part de main après PR #308 (778dcf3d37b1e10b1726a06f3d22bf1566a4f9c0) et réconcilie uniquement
ses six blocages ouverts. L'attestation humaine du 9 octobre, explicitement liée au parent
6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5, établit les réglages du full-export du 8 octobre et leur continuité
jusqu'aux captures de vérification du 9 octobre. Les captures sont inspectées et hachées ;
elles ne sont pas présentées comme des captures contemporaines de l'export.
L'attestation est une preuve humaine rétrospective, pas un journal natif du fournisseur.

L'identité des deux RAW, l'exécution unique de PR #307, l'attestation de non-contamination,
la fenêtre canonique et l'intégrité structurelle sont reprises sans nouvelle lecture des RAW,
nouvelle transformation ou nouvelle recherche de contamination. La révision 5 bloquée
ff232f99b8da9e186c9b47b35f841ddca420c8851f7585682e14c371dbba12e6 reste disponible dans l'historique Git.

## Réconciliation de la provenance de l'export exact

| Exigence | Preuve et résultat |
| --- | --- |
| NinjaTrader | 8.0.28.0 64-bit ; version attestée pour le full-export, corroborée par About le 9 octobre. |
| Chaîne source | Rithmic / Rithmic for NinjaTrader → Historical Data > Download → stockage historique NinjaTrader → Export ; chaîne explicitement attestée, aucun import historique tiers, enregistrement live comme historique désactivé. |
| Merge | Global « Do not merge » + MNQ « Use global settings » ; réglages inchangés, politique effective DoNotMerge. |
| Instrument | MNQ 09-26 individuel trimestriel ; export Last / Minute, configuration MNQ Future, valeur du point 2 et tick 0.25. |
| Template | CME US Index Futures ETH, Central (US & Canada), sessions 17:00–16:00 CT et définitions de jours fériés 2026 visibles. |
| Horloge Windows | Romance Standard Time, base +01:00, DST pris en charge ; identifiant inchangé entre export et vérification, offset explicite +02:00. |
| Horloge RAW | UTC / NINJATRADER_END_OF_BAR, déjà établie ; aucun décalage ou remplacement de timestamp. |
| Moment d'export | LastWriteTime 2026-10-08T22:14:09+02:00 = 20:14:09Z ; approximation filesystem uniquement, pas un timestamp natif NinjaTrader. |

Le fichier source de stratégie, les seuils, le protocole DEVELOPMENT et la transformation
préengagée restent inchangés. Les captures ne prouvent pas à elles seules l'origine individuelle
de chaque ligne du cache ; aucun mécanisme fournisseur/cache précis n'est inventé.

## RAW canonique et transformation déjà exécutée

| Élément | Valeur vérifiée conservée |
| --- | --- |
| Parent | MNQ 09-26.Last.txt ; 5 416 523 octets ; 101 962 lignes. |
| Parent SHA-256 | 6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5 |
| Partition | 12 120 avant la fenêtre ; 89 841 retenues ; 1 après ; 0 ligne retenue modifiée. |
| Dérivé canonique | MNQ_09-26_DEVELOPMENT_CANONICAL_V1.Last.txt ; 4 785 270 octets ; 89 841 lignes. |
| Dérivé SHA-256 | ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126 |
| Bornes UTC End-of-Bar inclusives | 2026-06-18T22:01:00Z → 2026-09-18T13:30:00Z. |

Toutes les lignes retenues sont identiques octet pour octet à leur parent, fins de ligne incluses.
L'audit indépendant PR #307 conserve des compteurs nuls pour les lignes malformées, timestamps
invalides/dupliqués/non chronologiques, OHLC invalides, valeurs non finies, volumes négatifs/non
entiers et prix hors grille MNQ 0.25. Aucun audit d'octets supplémentaire n'est exécuté ici.

## Gaps et donnée hors session

Les 71 gaps et leurs endpoints restent inchangés : 51 maintenances, 11 week-ends, 3 fermetures
jour férié/week-end, 1 fermeture anticipée et 5 UNEXPECTED_DATA_GAP_PRESERVED.
Ces cinq gaps représentent 70 minutes inexpliquées pendant des sessions publiées ; ils ne sont
pas reclassés comme fermetures prévues. Le protocole figé exige des gaps explicites et préservés,
sans exiger une couverture minute complète.

La ligne parent 26821 / dérivée 14701 à 2026-07-04T14:40:00Z (09:40 CT, samedi fermé)
reste inchangée et est documentée comme **UNRESOLVED_OFF_SESSION_STORED_DATA_PRESERVED**.
Ce n'est pas une barre de session régulière CME valide. L'utilisateur atteste ne pas l'avoir
modifiée manuellement et documente la chaîne de constitution du parent ; l'origine exacte de
cette ligne et son mécanisme fournisseur/cache restent **non prouvés**.
L'instruction humaine demande cette classification honnête, sans inventer une explication.
Le protocole n'impose ni suppression de cette ligne ni filtre de session : cette anomalie
documentée ne reste donc pas une preuve manquante bloquante de filiation.

Le constat et le code de l'audit initial restent conservés avec leur date d'origine. La revue
de provenance est ajoutée séparément ; aucune absence n'est remplie, aucun prix, volume,
timestamp ou filtre stratégique n'est modifié.

## Bindings et sérialisation

| Document | SHA-256 |
| --- | --- |
| Manifest stratégie | 965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a |
| Protocole DEVELOPMENT | 68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402 |
| Protocole transformation | bb47e6a9b867dd6e35516f5c43e56b9259aa00c526deb4978b050783a1e47f62 |
| Source transformation | 3ec9aadf9e4852d1ad4ef10ad6fd3f958d716a9de5df792a744c6926cf26d44c |
| Reçu exécution PR #307 | 2b4c6b86da5749545a55b6173916a26be88644b252afb9afcaf6f86deb7ccbf1 |
| Attestation de provenance | 0ee487a4217c6aeabdf64f8108aca1e0cc1a3a0d209afec9140fefd52bbd4f50 |
| Reçu d'export réconcilié | 24dcb1f1d068b1dea0432e14c351d6bcc4d0d3b2fd21b64de73fb1d5753b41c5 |
| Audit gaps et revue de provenance | 490aef8b06499dc6ac3ed8b5b85026fd72b899bfff38dc2d146190d8039305cf |
| Manifest filiation révision 6 | d9a5d15a8746491391ba13417a099801ba6add44be1f275d2ca9e699adf56b89 |

Les JSON utilisent UTF-8, clés triées, séparateurs compacts, valeurs non finies interdites et LF
final. Le SHA-256 porte sur les octets exacts ; le hash du manifest n'est pas injecté dans son
propre payload. Les 22 champs exigés par le protocole sont renseignés avec une preuve explicite.

## Suite autorisée

Vérification locale : 139 tests ciblés synthétiques et metadata PASS. Deux lectures
neuves des documents donnent des résultats canoniques identiques ; les 22 exigences
de filiation, les liens SHA-256, les preuves figées et les 71 gaps conservés passent.
Le contrôle documentaire ne lit aucun RAW et ne lance aucun calcul stratégique.

La prochaine gate est uniquement la construction et le test synthétique du runner, lié aux
hashes stratégie, protocole et filiation. Le replay réel requiert ensuite une autorisation
d'exécution distincte. Aucun signal V2 réel, comptage de trades, PnL, screening, replay,
optimisation, OOS, paper trading ou accès broker n'est exécuté par cette réconciliation.
