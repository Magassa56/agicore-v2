# EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE — audit bloqué

Audit initial du 2026-10-06 UTC, complété le 2026-10-08 sans lecture de prix. Ce document
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
| DATASET_LINEAGE_MANIFEST_SHA256 | `e4b3936d45c07f341370847f04fc577f2e55f8d2ae9cdfabb7196342ac443081` |
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
deux attestations humaines. Lors de l'audit initial, le message de mission
citait une phrase à fournir, sans déclaration personnelle. Le 6 octobre à
20:17:06 Europe/Paris (18:17:06 UTC), l'utilisateur de cette conversation a
fourni cette déclaration explicitement : les deux exigences d'attestation
sont désormais satisfaites.
`MNQ 06-26` et `MNQ 03-26` restent explicitement exclus. Aucune contamination
du candidat n'est prouvée, et aucun contrat de remplacement n'est choisi.

Déclaration reçue, conservée textuellement avec son auteur conversationnel,
sa date de soumission et une preuve JSON distincte :

> Je confirme que je n’ai pas utilisé MNQ 09-26 pour sélectionner, régler ou évaluer les performances de V2, et que je n’ai pas inspecté de résultat de performance V2 sur ce contrat avant la présente gate de filiation.

Preuve : `EMA_PULLBACK_V2_DEVELOPMENT_DATASET_HUMAN_ATTESTATION.json`,
SHA-256 `395b1f96429da11604248d0760fe6fc71e88acfa8c9b55aa7e9d078f0ba6a264`.
Les deux champs
`prior_performance_use` et `v2_performance_inspection` portent
`RECEIVED_EXPLICIT`. Ce document conserve la déclaration humaine ; il
ne constitue pas le reçu d’export. Le reçu réel reste à fournir.
Le rapport précédent reste traçable par son hash `ae8b9a6a0cc438ff2ee3eff4d139e47544146cf2dda223a416a5f3b4c6dda8d6`.

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

## Preuve Windows et horodatage filesystem du parent RAW

Preuve additionnelle reçue le 2026-10-06 à 21:55:55 Europe/Paris
(19:55:55 UTC), conservée dans
`EMA_PULLBACK_V2_DEVELOPMENT_DATASET_PARENT_RAW_TIMEZONE_EVIDENCE.json`.
SHA-256 de cette preuve : `37054e14f402a164b2205e9d25f2fe7e77858f3d945cc7c8e552dd98feaf2f46`.

| Champ déclaré | Valeur |
| --- | --- |
| Parent RAW SHA-256 | `fa41a98a56956a11ec3b2249eb579a699db7989378d06f971d22fa014cf277ad` |
| Parent RAW taille | `4 724 667` octets |
| Windows timezone | `Romance Standard Time` |
| Offset de base Windows | `+01:00` |
| SupportsDaylightSavingTime | `TRUE` |
| Horloge locale observée | `2026-10-06T21:47:58+02:00` |
| Offset effectivement observé | `+02:00` |
| Parent RAW LastWriteTime local | `2026-10-06T21:36:45+02:00` |
| Parent RAW LastWriteTime UTC | `2026-10-06T19:36:45Z` |

L'approximation du moment d'export est dérivée du `LastWriteTime` filesystem
sur la même machine Windows, avec l'offset `+02:00` explicitement observé
le même jour. La conversion exacte donne 19:36:45Z ; l'offset de base
Windows `+01:00` n'est pas utilisé dans cette conversion. Ce n'est **pas
un timestamp natif d'export NinjaTrader**. Aucun événement d'export natif
n'est inventé.

Le parent est déclaré immuable. Son SHA et sa taille sont conservés comme
identité attendue, `USER_DECLARED_NOT_LOCALLY_RECOMPUTED` : aucun octet RAW
n'est fourni, ouvert ou hashé ici. `raw_sha256` canonique et `dataset_id`
restent `null`. Lors de l'accès ultérieur autorisé, comparer les octets
reçus à ce SHA et cette taille avant l'audit ; aucun parent alternatif ne
peut être substitué silencieusement.

Cette preuve complète le volet Windows/filesystem et ne définit ni le
fuseau des barres RAW, ni leur timestamp de début/fin, ni le fuseau/DST du
template de session. Le reçu complet reste à fournir. Aucun champ ne sera
présenté comme un horodatage natif NinjaTrader à partir de cette preuve ;
le modèle vide de reçu reste inchangé. La preuve ne lève aucun des cinq
blocages restants.

Historique des rapports de blocage : révision 1
`ae8b9a6a0cc438ff2ee3eff4d139e47544146cf2dda223a416a5f3b4c6dda8d6`,
révision 2 `99333bd31fbfe1d5c936fa5bd528bd0784da888cb2b6f04e02e705f707d9b079` ; les bindings
stratégie/protocole et la preuve d'attestation sont inchangés.

## Nouveau parent complet déclaré le 8 octobre — octets absents

Preuve reçue à `2026-10-08T22:20:37+02:00` / `20:20:37Z`, conservée dans
`EMA_PULLBACK_V2_DEVELOPMENT_DATASET_FULL_PARENT_RAW_EXPORT_EVIDENCE.json`.
SHA-256 de la preuve : `a8b2189505c327882d6a4596c38d8d0e9ae80305f6d1b816c68345f4bbd37a64`.

| Champ déclaré pour ce nouvel export | Valeur |
| --- | --- |
| Instrument UI | `MNQ 09-26` |
| Dates demandées | `2026-06-01` à `2026-09-18` |
| Intervalle UI / type | `Minute` / `Last` ; valeur numérique de l'intervalle non fournie |
| Succès UI | `TRUE`, déclaré par l'utilisateur |
| Nom du parent complet | `MNQ 09-26.Last.txt` |
| Taille déclarée | `5 416 523` octets |
| SHA-256 déclaré | `6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5` |
| CreationTime filesystem | `2026-10-08T22:14:07+02:00` / `20:14:07Z` dérivé |
| LastWriteTime filesystem | `2026-10-08T22:14:09+02:00` / `20:14:09Z` dérivé |
| Rôle | `FULL_PARENT_RAW_PENDING_BYTE_VERIFICATION` |

Ces heures sont **des preuves filesystem uniquement**, pas des timestamps
natifs d'export NinjaTrader. La conversion UTC utilise l'offset explicite
`+02:00` ; aucun fuseau de barre, template de session ou paramètre manquant
n'est déduit des heures Windows ou de l'export précédent.

Le nouveau SHA/taille définit une identité déclarée distincte du parent du
6 octobre `fa41a98a...277ad` / 4 724 667 octets. Sa preuve immuable est
conservée intégralement : aucun lien de transformation, aucune identité
binaire et aucune substitution entre les deux exports n'est présumé.
Le nouvel export ne devient pas le RAW canonique.

La recherche du nom exact et des variantes ainsi que l'inventaire des
uploads texte récents ne trouvent **aucun fichier de 5 416 523 octets**.
Le candidat accessible le plus récent, `MNQ 09-26.Last(5).txt`, fait
691 856 octets ; le fichier portant le nom exact fait 367 982 octets et
remonte au 6 septembre. Ils ne sont ni téléchargés, ni ouverts, ni hashés
comme substituts. Cette conclusion porte uniquement sur les fichiers
accessibles au moment du contrôle, pas sur les octets du fichier Windows.

Les contrôles demandés restent `NOT_EVALUATED` : SHA exact, lignes et
bornes, ordre strict, doublons, lignes malformées, OHLC finis/valides,
volume entier non négatif, grille exacte 0.25, structure minute et
inventaire explicite des gaps, couverture jusqu'à la terminaison et
présence de barres post-terminaison. Zéro octet RAW a été lu ; aucun
résultat d'intégrité ne peut être annoncé.

Les dates demandées du parent large ne remplacent pas la fenêtre
canonique post-échéance déjà préengagée. La première session reste non
résolue. La terminaison contractuelle de référence reste le 18 septembre
à 08:30 Chicago / 13:30 UTC ; aucune comparaison avec le RAW ne sera faite
sans ses octets et la preuve du fuseau et du sens des timestamps de barre.
Le nombre de barres post-terminaison reste inconnu, et non zéro.
Les métadonnées CME suivantes ont été reconsultées le 8 octobre, sans prix :
[CME — dates d'expiration](https://www.cmegroup.com/trading/equity-index/rolldates.html)
et [CME — chapitre MNQ 361](https://www.cmegroup.com/rulebook/CME/IV/350/361.pdf).

Le reçu complet manque encore : chaîne fournisseur, version NinjaTrader,
valeur `1` de l'intervalle Minute, `DoNotMerge`, template `CME US Index
Futures ETH`, sémantique/fuseau des barres et fuseau/DST de session. Les
champs observés du modèle vide restent null ; seules les déclarations
explicitement reçues sont conservées dans cette nouvelle preuve séparée.
La gate reste `BLOCKED_HUMAN_GATE`, aucun dataset ID ni RAW canonique.

Pour poursuivre les contrôles autorisés, fournir le fichier complet
inchangé de **5 416 523 octets**, puis comparer immédiatement son SHA au
`6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5`. Un autre nom d'upload peut être tracé, mais jamais considéré
équivalent sans vérification des octets. Aucune correction ni transformation
n'est effectuée ; les éventuelles corrections restent une gate séparée.

## Contrôles RAW non exécutés

Aucun upload correspondant au nouveau parent complet n’est accessible ;
la période exacte et les preuves d’export restent bloquées. Aucun fichier candidat n'a été acquis, ouvert ou
hashé. Les deux attestations humaines sont reçues. Les contrôles
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

Les deux blocages d'attestation sont levés. Les cinq blocages restants
sont l'OPEN de la première session post-échéance non résolu, les octets RAW
et leur hash/taille non vérifiés localement, le reçu complet absent, les
sémantiques de timestamps/session non prouvées et l'intégrité RAW non évaluée.
Le SHA/taille du parent du 6 octobre et la preuve Windows/filesystem sont
conservés ; le nouvel export complet du 8 octobre est également déclaré,
mais ses octets ne sont pas accessibles. Aucune canonisation. Le statut
global reste `BLOCKED_HUMAN_GATE`.

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
métadonnées synthétiques PASS en 0.15s ; sérialisation canonique rejouée
deux fois, hashes recalculés, champs bloqués/null et modèle vide contrôlés,
conversion de l'heure contractuelle Chicago/UTC exacte, périmètre limité
aux quatre documents vérifié et `git diff --check` PASS. Aucun nouveau
module Python de checklist ni calcul stratégique n'a été ajouté.

Mise à jour d'attestation : déclaration exacte et horodatage local/UTC
vérifiés, preuve JSON hashée, deux blocages retirés et cinq conservés.
Le modèle de reçu vide et les champs RAW restent inchangés.

Mise à jour Windows/filesystem : conversion du même jour par `+02:00`
vérifiée, offset de base `+01:00` exclu du calcul, approximation explicitée,
preuve hashée liée au parent déclaré, cinq blocages préservés. Aucun octet
RAW ni indicateur n'est lu pour ces vérifications.

Aucun appel à un module de signal V2, EMA20, MACD, risque, exécution,
stop, sortie ou PnL ; aucun comptage de trades, graphique V2, donnée OOS,
ordre broker, optimisation ni replay stratégique réel. Reaction Engine
reste rouge ; aucun verdict de performance V2 n'existe dans cette gate.

Mise à jour export complet : preuve UI/filesystem déclarée et hashée,
conversion UTC exacte, ancien parent inchangé, inventaire des fichiers
accessibles sans lecture des octets. Tous les contrôles du nouveau RAW
restent NOT_EVALUATED et les cinq blocages de filiation sont conservés.

Vérification de cette mise à jour du 8 octobre : 17 tests de filiation
PASS en 0.14s ; assertions documentaires et conversions locales/UTC PASS,
sérialisations déterministes identiques, hashes stratégie/protocole
conformes, ancien parent/attestation/modèle inchangés, quatre documents
uniquement, diff-check PASS. Aucun audit des octets RAW n’est annoncé.
