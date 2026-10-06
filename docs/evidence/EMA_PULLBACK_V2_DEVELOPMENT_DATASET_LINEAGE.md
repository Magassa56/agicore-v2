# EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE — audit bloqué

Audit du 2026-10-06 UTC, effectué avant toute lecture de prix. Ce document
enregistre les preuves disponibles et les preuves manquantes. Il ne canonise
aucun dataset et ne donne aucune autorisation de replay.

| Sortie | Valeur |
| --- | --- |
| PHASE | `EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE` |
| STATUS | `BLOCKED_HUMAN_GATE` |
| CANDIDATE_CONTRACT | `MNQ 09-26` |
| DATASET_ROLE | `EXPOSED_DEVELOPMENT` |
| CANONICAL_DATASET_ID | `NONE` |
| SOURCE_RAW_SHA256 | `NONE` |
| DATASET_LINEAGE_MANIFEST_SHA256 | `ae8b9a6a0cc438ff2ee3eff4d139e47544146cf2dda223a416a5f3b4c6dda8d6` |
| REAL_STRATEGY_REPLAY | `NOT_EXECUTED` |
| NEXT | `EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED` |

Le digest ci-dessus identifie **ce rapport de blocage**, pas un dataset
approuvé. Le JSON contient `status = BLOCKED_HUMAN_GATE`,
`artifact_kind = BLOCKED_LINEAGE_AUDIT_NOT_APPROVED_DATASET`,
`dataset_id = null` et `raw_sha256 = null`. Ces octets ne peuvent pas
autoriser un runner DEVELOPMENT. Il faudra un nouveau manifest complet
et son nouveau hash après réception et vérification des preuves.

## Bindings vérifiés, inchangés

| Artefact | SHA-256 recalculé, conforme |
| --- | --- |
| Manifest `EMA_PULLBACK_V2_REGIME_GATED_BASELINE`, version 1 | `965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a` |
| Protocole DEVELOPMENT | `68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402` |

Base auditée : `547bdf60c5c71d67abbbe490b35c2f36d7d7354a`, arbre
`50f31d4ba6b390fcbde801b220dae05529f092fa`, issu de la PR #301 fusionnée.
Aucun seuil, module stratégique, manifest de stratégie ni protocole n'est
modifié. Toute divergence de ces bindings doit rester `FAIL_CLOSED`.

## Éligibilité : preuves partielles, attestation obligatoire

Les fichiers texte suivis et les diffs de tous les refs Git localement
disponibles ont été recherchés avant l'ajout de ce rapport. Le clone n'est
pas shallow ; 718 commits sont accessibles. Les recherches couvrent les
formes `MNQ 09-26`, `mnq-09-26`, `MNQU26` et les variantes de séparateurs,
année longue et nom du mois. Aucun contenu RAW, `data/`, archive, image ou
fichier de prix n'a été ouvert.

Les quatre références courantes sont procédurales : le checkpoint, le
protocole JSON, son Markdown et une assertion synthétique du contrat
candidat. Les deux commits de référence sont le protocole sans replay
`8342f5a4b4183aad6aae11fdc6db3abe789410c1` et son équivalent local
`79d1516adbf99147529befade84147e89f027458`. La recherche de chemins Git
historiques portant le nom du candidat ne trouve aucun fichier candidat.
Aucune référence d'évaluation, replay, screening de performance, sélection
de stratégie ou optimisation sur ce contrat n'a été trouvée dans ce scope.

Ce résultat ne prouve pas l'absence d'usage externe, de refs non récupérés,
de rapports Windows ou de données non suivies. Il ne remplace jamais les
deux attestations humaines. Le message de mission cite une phrase à fournir
si elle est vraie ; cette citation n'est pas une attestation personnelle.
`MNQ 06-26` et `MNQ 03-26` restent explicitement exclus. Aucune contamination
du candidat n'est prouvée, et aucun contrat de remplacement n'est choisi.

La phrase suivante doit être fournie explicitement et sincèrement par
l'humain ; auteur, date et référence de preuve devront être conservés :

> Je confirme que je n’ai pas utilisé MNQ 09-26 pour sélectionner, régler ou évaluer les performances de V2, et que je n’ai pas inspecté de résultat de performance V2 sur ce contrat avant la présente gate de filiation.

## Période contractuelle avant les prix

La règle demandée est conservée : première session après l'échéance du
précédent contrat trimestriel, jusqu'à la dernière session admissible du
contrat septembre, inclusivement. Aucun graphique ni résultat ne détermine
la période.

| Fait établi | Preuve primaire |
| --- | --- |
| Échéance précédente : **18 juin 2026**, jeudi | Calendrier CME U.S. Indexes 2026 ; Juneteenth tombe le lendemain |
| Échéance du candidat : **18 septembre 2026** | Calendrier CME ; contrat terminé au 6 octobre 2026 |
| Dernière session : trade date **18 septembre 2026** | Fin de négociation du contrat expirant à 08:30 Chicago |
| Fin contractuelle : **2026-09-18 08:30 CDT / 13:30 UTC** | Règles MNQ et fiche CME ; `America/Chicago`, offset d'été `-05:00` |
| Première session post-échéance, son OPEN exact et trade date | **Non résolus : preuve MNQ Juneteenth requise** |

Les horaires ordinaires CME commencent à 17:00 Chicago la veille de la
trade date. La note Juneteenth mentionne un pré-open le 18 juin et une
clôture le 19 juin, mais le texte public récupéré ne fournit pas les lignes
OPEN spécifiques à MNQ de cette session. Aucun horaire de fête n'est déduit
silencieusement d'un horaire ordinaire ou d'un calendrier de settlements.
`canonical_export_window` reste donc `null` ; ne pas exporter un
sous-intervalle choisi arbitrairement. Obtenir le calendrier produit MNQ
des 18–19 juin 2026, puis fixer l'intervalle complet avant lecture du RAW.

Les rolls usuels CME du 15 juin et du 14 septembre ne remplacent pas les
bornes d'expiration prescrites par cette mission. Il n'y a aucun merge ni
substitution de contrat. Les bornes contractuelles ne fixent pas par
elles-mêmes le fuseau ou la sémantique des timestamps exportés.

Sources consultées le 2026-10-06, métadonnées exclusivement :

- [CME — Equity Index Roll Dates](https://www.cmegroup.com/trading/equity-index/rolldates.html).
- [CME — MNQ rulebook, chapitre 361](https://www.cmegroup.com/rulebook/CME/IV/350/361.pdf).
- [CME — Micro E-mini Futures, spécifications](https://www.cmegroup.com/trading/equity-index/files/cme-micro-e-mini-futures-fact-card.pdf).
- [CME — Globex Trading Hours and Holiday Schedules 2026](https://www.cmegroup.com/trading-hours.html).
- [CME — Juneteenth settlement notice 2026](https://www.cmegroup.com/tools-information/holiday-calendar/files/2026/juneteenth-day-settlement-times-2026.pdf).

Le PDF `2026-juneteenth-clearing-advisory.pdf` est écarté comme preuve
d'horaire produit 2026 : son sujet récupéré porte l'année 2025 malgré son
nom. Aucun écart de source n'est corrigé ou masqué.

## Source et reçu à fournir

Un seul fichier est attendu : **`MNQ 09-26.Last.txt`**. Paramètres requis :
MNQ, contrat trimestriel individuel, `1 Minute`, `Last`, `DoNotMerge`,
`CME US Index Futures ETH`. Aucun fichier Bid/Ask n'est demandé. Une série
continue, merged ou back-adjusted ne peut pas être admissible.

`EMA_PULLBACK_V2_DEVELOPMENT_DATASET_EXPORT_RECEIPT_TEMPLATE.json` est un
**modèle vide, pas un reçu contemporain**. Les valeurs prescrites sont
séparées des valeurs observées, toutes `null`. Il ne contient ni hash RAW,
ni date d'export, ni fournisseur, ni version NinjaTrader inventés.

Le reçu réel devra enregistrer paramètres observés et preuves, chaîne
fournisseur, version NinjaTrader, nom/SHA-256/taille/lignes du RAW, premiers
et derniers timestamps, heure locale et UTC de l'export, fuseau Windows et
offset réel à l'export, sens des timestamps, fuseau de session et DST,
preuve d'échéance, fenêtre complète et attestations. Ne pas antidater un
reçu ; aucune sémantique UTC/Paris/Chicago n'est supposée pour le RAW.

## Contrôles RAW non exécutés

Aucun RAW n'est fourni pour cette gate et l'éligibilité humaine reste
bloquée. Aucun fichier candidat n'a été acquis, ouvert ou hashé. Les contrôles
de lisibilité, lignes et bornes, ordre strict, doublons, lignes malformées,
OHLC finis et valides, volume fini non négatif, grille exacte 0.25,
structure minute/gaps, DST/fuseaux, identité et absence de merge portent
tous `NOT_EVALUATED`, jamais `PASS`.

Après levée des blocages préalables, calculer immédiatement le SHA-256
complet des octets RAW et le conserver, puis effectuer seulement l'audit
d'intégrité. Chaque gap réel doit être enregistré, classé et préservé ;
une minute absente n'est pas automatiquement invalide. Aucun dedup,
forward fill, interpolation, bougie synthétique, correction OHLC/timestamp
ou remplacement de volume. Si une transformation est nécessaire :
`BLOCKED_HUMAN_GATE`, puis
`EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_REQUIRED` avant toute
transformation explicite, déterministe et hashée avec filiation parent.

## Reprise de la gate

Les blocages précis sont les deux attestations manquantes, l'OPEN de la
première session post-échéance non résolu, le RAW et son hash immédiat non
fournis, le reçu contemporain absent, les sémantiques de timestamps/session
non prouvées et l'intégrité RAW non évaluée. La réponse à une attestation
ne vaut pas validation des autres points.

Une fois toutes les preuves suffisantes, seulement alors fixer MNQ 09-26
comme canonique et construire l'identifiant depuis les huit premiers
caractères du **vrai** SHA-256 RAW. Remplacer le rapport de blocage par le
manifest complet et publier son nouveau digest. Après `PASS`, ouvrir
`EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION_REQUIRED`, sur données
synthétiques et bindings exacts ; l'exécution DEVELOPMENT unique reste
une gate distincte ultérieure.

Le JSON canonique est UTF-8 compact, clés triées récursivement, sans
NaN/Infinity JSON, avec un LF final. Son hash SHA-256 porte sur les octets
exacts et reste hors du payload pour éviter une auto-référence circulaire.
Le modèle de reçu utilise la même sérialisation déterministe.

Vérifications locales : 17 tests existants du contrat de filiation sur
métadonnées synthétiques PASS en 0.31s ; sérialisation canonique rejouée
deux fois, hashes recalculés, champs bloqués/null et modèle vide contrôlés,
conversion de l'heure contractuelle Chicago/UTC exacte, périmètre limité
aux quatre documents vérifié et `git diff --check` PASS. Aucun nouveau
module Python de checklist ni calcul stratégique n'a été ajouté.

Aucun appel à un module de signal V2, EMA20, MACD, risque, exécution,
stop, sortie ou PnL ; aucun comptage de trades, graphique V2, donnée OOS,
ordre broker, optimisation ni replay stratégique réel. Reaction Engine
reste rouge ; aucun verdict de performance V2 n'existe dans cette gate.
