# DEVELOPMENT V2 — filiation réconciliée après PR #307

```text
PHASE = EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE
STATUS = BLOCKED_HUMAN_GATE
CANONICAL_DATASET_ID = NONE
SOURCE_RAW_SHA256 = NONE
DATASET_LINEAGE_MANIFEST_SHA256 = ff232f99b8da9e186c9b47b35f841ddca420c8851f7585682e14c371dbba12e6
REAL_STRATEGY_REPLAY = NOT_EXECUTED
NEXT = EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED
```

Révision 5, établie le 2026-10-09T13:12:06.124799Z, sur `main` après PR #307, commit
`fbf4ccda9d3b55c4db2098a3a433d22d88cea168`, arbre `be2b61591cf9a405db628e6fbaf963ab377a6622`. Autorisation AGIcoreManager du
2026-10-09T12:50:15Z limitée à la finalisation de filiation. Les snapshots
historiques sont conservés dans Git ; le SHA de la révision 4 était
`e4b3936d45c07f341370847f04fc577f2e55f8d2ae9cdfabb7196342ac443081`. Ce nouveau hash identifie un rapport BLOCKED,
pas un dataset approuvé ni une autorisation de replay.

## Bindings immuables revérifiés

| Binding | SHA-256 |
| --- | --- |
| Stratégie `EMA_PULLBACK_V2_REGIME_GATED_BASELINE`, version 1 | `965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a` |
| DEVELOPMENT protocol | `68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402` |
| Transformation protocol PR #306 | `bb47e6a9b867dd6e35516f5c43e56b9259aa00c526deb4978b050783a1e47f62` |
| Source de transformation | `3ec9aadf9e4852d1ad4ef10ad6fd3f958d716a9de5df792a744c6926cf26d44c` |
| Reçu d'exécution PR #307 | `2b4c6b86da5749545a55b6173916a26be88644b252afb9afcaf6f86deb7ccbf1` |

Aucun seuil, module métier, protocole figé ou source de transformation modifié.
Les protocoles et l'exécution sont composés comme preuves ; la transformation
n'est pas réexécutée.

## Identité, transformation et intégrité résolues

| Fichier vérifié | SHA-256 | Octets | Lignes | Première / dernière fin de bougie UTC |
| --- | --- | ---: | ---: | --- |
| Parent `MNQ 09-26.Last.txt` | `6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5` | 5416523 | 101962 | 2026-06-07T22:01:00Z / 2026-09-18T13:31:00Z |
| Dérivé `MNQ_09-26_DEVELOPMENT_CANONICAL_V1.Last.txt` | `ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126` | 4785270 | 89841 | 2026-06-18T22:01:00Z / 2026-09-18T13:30:00Z |

PR #307 atteste l'unique exécution autorisée : 12120 lignes avant la fenêtre,
89841 retenues, 1 après ; 0 ligne retenue modifiée. La somme reste 101962.
Chaque ligne retenue est identique à sa ligne parent, fin de ligne incluse.
Les octets parent et dérivé ont été rehashés et la correspondance revérifiée
en lecture seule dans cette gate. Le nom du fichier dérivé ne le canonise pas.

L'audit indépendant PR #307 reste inchangé : source
`5d53cb9abe45c510ef2533f0b068d14b012bc0a9cb2c2d0cd74bd41dda3f44f5`, résultat
`2bb3a6169639336f48a34bb145daeb35627ae800b70989a7fb1a58d198852340`. Ses compteurs sont repris explicitement :

| Contrôle | Erreurs |
| --- | ---: |
| duplicate_timestamps | 0 |
| invalid_ohlc | 0 |
| invalid_timestamps | 0 |
| malformed_rows | 0 |
| negative_volume | 0 |
| non_chronological_rows | 0 |
| non_minute_timestamps | 0 |
| nonfinite_values | 0 |
| noninteger_volume | 0 |
| off_mnq_0_25_tick_grid | 0 |

L'ancien blocage de disponibilité/identité RAW et celui de l'intégrité
non évaluée sont levés. Les attestations humaines de non-utilisation et de
non-inspection V2, reçues le 2026-10-06T18:17:06Z, restent reçues et inchangées :
preuve `395b1f96429da11604248d0760fe6fc71e88acfa8c9b55aa7e9d078f0ba6a264`. L'audit du dépôt sur 737 commits accessibles
ne retrouve que des références procédurales ; il reste une preuve partielle,
distincte de cette attestation. Aucun contrôle de contamination déjà résolu
n'est rouvert.

## Fenêtre et timestamps résolus

Les [expirations CME](https://www.cmegroup.com/trading/equity-index/rolldates.html)
confirment le 18 juin et le 18 septembre 2026. Le
[calendrier NinjaTrader des indices 2026](https://support.ninjatrader.com/eu/s/article/2026-Holiday-Trading-Hours?language=en_US)
confirme l'ouverture du 18 juin à 17:00 CT. La fermeture contractuelle MNQ
est 08:30 CT le 18 septembre, selon le
[chapitre 361](https://www.cmegroup.com/rulebook/CME/IV/350/361.pdf) et la
[fiche Micro E-mini](https://www.cmegroup.com/trading/equity-index/files/cme-micro-e-mini-futures-fact-card.pdf).

La convention préengagée reste donc ouverture canonique 2026-06-18T22:00:00Z,
première fin de bougie 22:01:00Z, dernière 2026-09-18T13:30:00Z inclusive.
Les deux bornes sont présentes. La seule ligne parent après la terminaison
a été retirée par l'exécution PR #307 ; aucune ligne dérivée post-terminaison.
Les dates de roll usuelles ne remplacent pas cette fenêtre.

`NINJATRADER_END_OF_BAR` et `UTC` sont établis par l'instruction humaine
préengagée et la [documentation native d'export](https://static.ninjatrader.com/support/helpGuides/nt8/exporting.htm).
L'UI contemporaine montre `Minute` ; l'export reprend le
[format natif une minute](https://static.ninjatrader.com/support/helpGuides/nt8/importing.htm),
compatible avec les octets vérifiés. Cette déduction documentaire explicite
résout l'ancienne demande d'une valeur numérique d'intervalle : l'UI native
d'export ne comporte pas ce champ. L'intervalle `1 Minute` n'est plus bloquant.

## Reçu propre au full-parent exact

Le nouveau reçu `EMA_PULLBACK_V2_DEVELOPMENT_DATASET_EXPORT_RECEIPT.json`, SHA `4e341ee372eb5729bafcaffd39ecb3642c365b2a37e0340f2f8f20d6676b1ff6`, est assemblé maintenant
à partir des preuves de l'export du 8 octobre, pas antidaté en reçu natif.
La déclaration exacte du parent et l'image contemporaine
`image(20261008-201428).png`, SHA `23d71b7df0fd624fef430210a1febc82820f28f5fcac4a9d67ef33c8f4a20fc9`,
montrent MNQ 09-26, Last, Minute, dates demandées 01/06/2026 à 18/09/2026
et succès. Les dates du panneau Download ne sont pas celles du panneau Export.
L'image ne montre ni version précise, ni fournisseur, ni merge policy,
ni template, ni identifiant de fuseau Windows.

Création filesystem déclarée : 2026-10-08T22:14:07+02:00 = 20:14:07Z.
LastWriteTime déclaré : 2026-10-08T22:14:09+02:00 = 20:14:09Z.
Le second est uniquement une approximation de l'heure d'export par le système
de fichiers, jamais un timestamp natif NinjaTrader. L'offset +02:00 suffit à
cette conversion ; il ne prouve pas le nom du fuseau Windows. La preuve
`Romance Standard Time` du 6 octobre concerne le parent fa41... ; elle n'est
pas recopiée dans l'export actuel. Les champs encore inconnus restent `null`.

## Réconciliation des 71 gaps sans correction

Audit `EMA_PULLBACK_V2_DEVELOPMENT_DATASET_GAP_AUDIT.json`, SHA `386650569726c6f46a650a2eb16ff679264d7a2e3fedd7eae93f967c5eaf7005`. Inventaire identique à PR #307,
parent et dérivé inchangés, toutes les absences conservées. Les horaires
ordinaires proviennent des [horaires CME](https://www.cmegroup.com/markets/equities/sp-500-and-nasdaq-100-futures.html) ;
les jours fériés du calendrier primaire NinjaTrader cité ci-dessus. Les heures
CT sont converties via `America/Chicago`, offset -05:00 durant cette fenêtre.
La classification du calendrier ne prouve pas le template installé.

| Classe | Gaps | Slots d'une minute absents |
| --- | ---: | ---: |
| Maintenance quotidienne publiée | 51 | 3060 |
| Week-end ordinaire publié | 11 | 32340 |
| Fermeture jour férié / week-end publiée | 3 | 6359 |
| Fermeture anticipée du 7 septembre | 1 | 300 |
| `UNEXPECTED_DATA_GAP_PRESERVED` | 5 | 70 |
| Total | 71 | 42129 |

Les cinq gaps non expliqués par une fermeture publiée se trouvent entre
14:53 et 16:00Z le 17 juillet, puis aux minutes absentes 20:40Z, 20:55Z et
22:49Z le 17 septembre, et 06:55Z le 18 septembre. Leur cause n'est pas
inventée. Le protocole figé exige des gaps explicites, pas une couverture
intégrale : ces absences seules ne font pas échouer la filiation.

Une contradiction distincte reste à expliquer : la ligne parent 26821 /
dérivée 14701 existe à **2026-07-04T14:40:00Z**, soit **09:40 CT un samedi fermé**.
Elle coupe en deux le gap du week-end du 3 au 5 juillet ; les minutes absentes
des deux intervalles restent des minutes de fermeture publiée, mais leurs
extrémités observées portent un avertissement explicite. La ligne reste
intacte. Il faut établir son origine et sa cohérence de session, sans
la qualifier silencieusement de bougie de session normale, sans filtre
additionnel ni transformation implicite. L'audit de tous les timestamps
de la fenêtre retrouve exactement une ligne hors des horaires publiés.

| Gap | Fin observée précédente UTC | Fin observée suivante UTC | Minutes absentes | Classification / avertissement |
| --- | --- | --- | ---: | --- |
| G001 | 2026-06-19T17:00:00Z | 2026-06-21T22:01:00Z | 3180 | SCHEDULED_HOLIDAY_WEEKEND_CLOSURE_PRESERVED |
| G002 | 2026-06-22T21:00:00Z | 2026-06-22T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G003 | 2026-06-23T21:00:00Z | 2026-06-23T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G004 | 2026-06-24T21:00:00Z | 2026-06-24T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G005 | 2026-06-25T21:00:00Z | 2026-06-25T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G006 | 2026-06-26T21:00:00Z | 2026-06-28T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G007 | 2026-06-29T21:00:00Z | 2026-06-29T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G008 | 2026-06-30T21:00:00Z | 2026-06-30T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G009 | 2026-07-01T21:00:00Z | 2026-07-01T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G010 | 2026-07-02T21:00:00Z | 2026-07-02T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G011 | 2026-07-03T17:00:00Z | 2026-07-04T14:40:00Z | 1299 | SCHEDULED_HOLIDAY_WEEKEND_CLOSURE_PRESERVED ; NEXT_OBSERVED_ROW_OUTSIDE_PUBLISHED_SESSION |
| G012 | 2026-07-04T14:40:00Z | 2026-07-05T22:01:00Z | 1880 | SCHEDULED_HOLIDAY_WEEKEND_CLOSURE_PRESERVED ; PREVIOUS_OBSERVED_ROW_OUTSIDE_PUBLISHED_SESSION |
| G013 | 2026-07-06T21:00:00Z | 2026-07-06T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G014 | 2026-07-07T21:00:00Z | 2026-07-07T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G015 | 2026-07-08T21:00:00Z | 2026-07-08T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G016 | 2026-07-09T21:00:00Z | 2026-07-09T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G017 | 2026-07-10T21:00:00Z | 2026-07-12T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G018 | 2026-07-13T21:00:00Z | 2026-07-13T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G019 | 2026-07-14T21:00:00Z | 2026-07-14T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G020 | 2026-07-15T21:00:00Z | 2026-07-15T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G021 | 2026-07-16T21:00:00Z | 2026-07-16T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G022 | 2026-07-17T14:53:00Z | 2026-07-17T16:00:00Z | 66 | UNEXPECTED_DATA_GAP_PRESERVED |
| G023 | 2026-07-17T21:00:00Z | 2026-07-19T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G024 | 2026-07-20T21:00:00Z | 2026-07-20T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G025 | 2026-07-21T21:00:00Z | 2026-07-21T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G026 | 2026-07-22T21:00:00Z | 2026-07-22T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G027 | 2026-07-23T21:00:00Z | 2026-07-23T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G028 | 2026-07-24T21:00:00Z | 2026-07-26T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G029 | 2026-07-27T21:00:00Z | 2026-07-27T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G030 | 2026-07-28T21:00:00Z | 2026-07-28T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G031 | 2026-07-29T21:00:00Z | 2026-07-29T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G032 | 2026-07-30T21:00:00Z | 2026-07-30T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G033 | 2026-07-31T21:00:00Z | 2026-08-02T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G034 | 2026-08-03T21:00:00Z | 2026-08-03T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G035 | 2026-08-04T21:00:00Z | 2026-08-04T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G036 | 2026-08-05T21:00:00Z | 2026-08-05T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G037 | 2026-08-06T21:00:00Z | 2026-08-06T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G038 | 2026-08-07T21:00:00Z | 2026-08-09T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G039 | 2026-08-10T21:00:00Z | 2026-08-10T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G040 | 2026-08-11T21:00:00Z | 2026-08-11T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G041 | 2026-08-12T21:00:00Z | 2026-08-12T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G042 | 2026-08-13T21:00:00Z | 2026-08-13T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G043 | 2026-08-14T21:00:00Z | 2026-08-16T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G044 | 2026-08-17T21:00:00Z | 2026-08-17T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G045 | 2026-08-18T21:00:00Z | 2026-08-18T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G046 | 2026-08-19T21:00:00Z | 2026-08-19T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G047 | 2026-08-20T21:00:00Z | 2026-08-20T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G048 | 2026-08-21T21:00:00Z | 2026-08-23T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G049 | 2026-08-24T21:00:00Z | 2026-08-24T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G050 | 2026-08-25T21:00:00Z | 2026-08-25T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G051 | 2026-08-26T21:00:00Z | 2026-08-26T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G052 | 2026-08-27T21:00:00Z | 2026-08-27T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G053 | 2026-08-28T21:00:00Z | 2026-08-30T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G054 | 2026-08-31T21:00:00Z | 2026-08-31T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G055 | 2026-09-01T21:00:00Z | 2026-09-01T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G056 | 2026-09-02T21:00:00Z | 2026-09-02T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G057 | 2026-09-03T21:00:00Z | 2026-09-03T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G058 | 2026-09-04T21:00:00Z | 2026-09-06T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G059 | 2026-09-07T17:00:00Z | 2026-09-07T22:01:00Z | 300 | SCHEDULED_HOLIDAY_EARLY_CLOSE_PRESERVED |
| G060 | 2026-09-08T21:00:00Z | 2026-09-08T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G061 | 2026-09-09T21:00:00Z | 2026-09-09T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G062 | 2026-09-10T21:00:00Z | 2026-09-10T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G063 | 2026-09-11T21:00:00Z | 2026-09-13T22:01:00Z | 2940 | SCHEDULED_WEEKEND_CLOSURE_PRESERVED |
| G064 | 2026-09-14T21:00:00Z | 2026-09-14T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G065 | 2026-09-15T21:00:00Z | 2026-09-15T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G066 | 2026-09-16T21:00:00Z | 2026-09-16T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G067 | 2026-09-17T20:39:00Z | 2026-09-17T20:41:00Z | 1 | UNEXPECTED_DATA_GAP_PRESERVED |
| G068 | 2026-09-17T20:54:00Z | 2026-09-17T20:56:00Z | 1 | UNEXPECTED_DATA_GAP_PRESERVED |
| G069 | 2026-09-17T21:00:00Z | 2026-09-17T22:01:00Z | 60 | SCHEDULED_DAILY_MAINTENANCE_PRESERVED |
| G070 | 2026-09-17T22:48:00Z | 2026-09-17T22:50:00Z | 1 | UNEXPECTED_DATA_GAP_PRESERVED |
| G071 | 2026-09-18T06:54:00Z | 2026-09-18T06:56:00Z | 1 | UNEXPECTED_DATA_GAP_PRESERVED |

## Preuves humaines encore nécessaires

Les preuves suivantes doivent concerner le full-parent du 8 octobre,
SHA `6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5`, et non un export antérieur :

- **CURRENT_EXPORT_NINJATRADER_VERSION_UNPROVEN** : Exact NinjaTrader version/build used for the full-parent export of 2026-10-08, tied to parent SHA-256 6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5.
- **CURRENT_EXPORT_PROVIDER_SOURCE_CHAIN_UNPROVEN** : Provider and complete source chain of the stored MNQ 09-26 Last minute data exported on 2026-10-08, including any historical downloads, imports, cached or live-collected contributions; evidence of individual-contract identity and absence of merged/continuous/back-adjusted substitution.
- **CURRENT_EXPORT_MERGE_POLICY_UNPROVEN** : Evidence that DoNotMerge applied to this exact full-parent export/source chain, rather than a setting shown for an older export.
- **CURRENT_EXPORT_TRADING_HOURS_TEMPLATE_UNPROVEN** : Evidence of the actual CME US Index Futures ETH template/settings for this export/source chain, including its configured timezone, DST/session and holiday definitions. Published exchange calendars do not prove the local template configuration.
- **CURRENT_EXPORT_WINDOWS_TIMEZONE_IDENTIFIER_UNPROVEN** : Windows timezone identifier for the machine at this exact 2026-10-08 export. The explicit +02:00 filesystem offset and its UTC conversion are already established; the older fa41... export does not establish the current identifier.
- **OBSERVED_BAR_DURING_PUBLISHED_CLOSURE_UNRESOLVED** : Source/session evidence explaining the unchanged parent row 26821 / derived row 14701 at 2026-07-04T14:40:00Z (09:40 CT), during the published Saturday closure. Resolve its origin and timestamp/session coherence without deleting, shifting or correcting the row.

Le manifest comporte une matrice de tous les champs exigés par le protocole.
Les anciens blockers RAW, intégrité, ouverture de fenêtre, contamination et
UTC/End-of-Bar sont réconciliés avec les preuves actuelles. Seuls les six
points précis ci-dessus empêchent PASS. Une absence d'information reste une
absence ; aucun réglage n'est inventé.

## États et limite d'autorisation

`CANONICAL_DEVELOPMENT_CONTRACT`, `CANONICAL_DATASET_ID` et le hash de source
canonique restent `NONE`. Le hash vérifié du dérivé est conservé comme preuve
candidate, pas comme source approuvée. L'identifiant réservé après PASS serait
`mnq-09-26-minute-last-development-ee6eeed4-v1`.

La prochaine action est la reprise de la même gate avec les seules preuves
manquantes. `EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_IMPLEMENTATION_REQUIRED` reste
fermée jusqu'à PASS. Aucun signal V2, trade, PnL, replay, screening,
optimisation, OOS, broker ou paper trading. Aucune correction, reconstruction,
interpolation, suppression ou deuxième exécution de transformation.

JSON canonique UTF-8, clés triées, séparateurs compacts, LF final, sans NaN ;
SHA-256 sur les octets du fichier et stocké dans cette note, hors payload.
Les preuves PR #306/#307, le protocole DEVELOPMENT, le manifest stratégie,
l'attestation et les deux exports historiques restent inchangés.
