# AGIcore current state — checkpoint

Date : 2026-09-26 UTC.
Statut : BLOCKED_HUMAN_GATE — NEXT_BAR_EXECUTION_MODEL_REQUIRED ;
CLEAN_LINEAGE_SOURCE_EVIDENCE = PASS ; D003_PROVISIONAL_DEVELOPMENT = PASS_WITH_ASSUMPTIONS ;
EMA_PULLBACK_V1_MNQ_PULLBACK_PREDICATE = PASS ;
EMA_PULLBACK_V1_MNQ_EMA20_SLOPE = PASS ;
EMA_PULLBACK_V1_MNQ_MACD = PASS ;
EMA_PULLBACK_V1_MNQ_ENTRY_SIGNAL = PASS ;
EMA_PULLBACK_V1_MNQ_EMA20_POSITION_EXIT = PASS ;
EMA_PULLBACK_V1_MNQ_T_MINUS_2_TOUCH_OR_PROXIMITY = PASS ;
le RAW legacy reste PROVISIONAL et D003 legacy reste BLOCKED_PROVENANCE.
Branche de vérification : feature/ema-pullback-v1-mnq-t-minus-2-touch.
Base GitHub vérifiée et récupérée : 0880da6fb2dd916ba53ed1caf069f66342130f67.

## Acquis vérifiés

- SINK-B3 intégré par PR #238, merge 248d762038164cd6a58842382e06207baf0e63d0.
- D001 approuvée le 2026-09-12 ; aucune nouvelle approbation du profil n'est requise.
- D002 intégrée par PR #240, merge d52e9212eadac55e9d3d24482fd744ca54839771.
- CI #161 du head 242991685f8f23268a9bc7e0456528afed43dddf : success.
- Avant fusion D002 : 26 tests ciblés PASS ; suite 5868 passed, 6 warnings in 57.23s.
  Ruff et diff-check PASS ; revue Codex indépendante sans défaut bloquant dans ce périmètre.
- Les gates commit/publication/fusion D002 ont été autorisées successivement et franchies.
- PR #239 contient la première version documentaire ; son ancienne attente D001 est historique.
- Reconstruction L5/outbox/inbox intégrée par PR #241 : head b1e5e37080e88f755353bb6cd1f7b5fcf4d26811,
  merge 6c3c6bb5299e0fe8ee6db646e94b79fb4bed45df, arbre e95abdedc2183b22b97d323135db420e17290854.
- CI PR #163 (run 34780120469) : success sur le head exact b1e5e37080e88f755353bb6cd1f7b5fcf4d26811.
- Checkpoint post-fusion intégré par PR #242 : head 0c8e895b6563ab4a790891d2d153738b85d8094e,
  CI #165 (run 34781880719) success, merge d41103265f3afc5e324a01d45dd66b14bea0d148,
  arbre d352e3daf60cae41bfe1935577f60b3b64fb8785.
- Gate 5 intégrée par PR #243, merge 111c23657a4614c38c73d6bbbd51605c4fec80af.
- Audit de filiation D003 intégré par PR #244 : head c5654d7d39bf67ecafb2a26c01d86d2ae783b3d3,
  CI #169 (run 34995972384) success, merge 61643be37ba70f18286e9be8baefc168eba713f3,
  arbre 1e1ede4b6517b01f1b521ffadbdf7188a3fe1368.
- Séparation NQ/MNQ intégrée par PR #245 : head 674065adde62e35f3430b24d77105d68e4fd252b,
  CI #171 (run 35435261872) success, merge a2a64fd921a0f288796788c3837bbab7c6df63f6,
  arbre 385264bd09aa9e18a91f9330f4638c00d51dd89a.
- Contrat DATASET_LINEAGE_MANIFEST_V1 intégré par PR #246 : head
  93b7fc22ea86b8f7befe3ab015f51339ec90f9b4, CI #173 (run 35436126126) success,
  merge 17c747d005e2b6699b04bc19fe70267dfe5a2557,
  arbre 7944221d3b263c44282bbbe0351c35c520a24483.

## Gate 5 auditée

Le scénario intégré par PR #241 compose, dans des processus neufs, le store L5, l'outbox,
l'inbox, ExecutionService, ExecutionAgent, la mémoire SQLite et l'autorité EventBus canonique.
Il couvre tous les composants obligatoires du profil offline borné approuvé par D001. L'audit
n'a trouvé aucune preuve manquante dans ce périmètre et n'a donc nécessité aucun changement runtime.
RuntimeEngine, SignalLoopOrchestrator et RuntimeEventBridge restent explicitement hors de cette
garantie, conformément à D001 ; « Gate 5 validée » ne signifie pas runtime global certifié.

## Preuves obtenues

- 24 tests ciblés PASS en 23.27s ; neuf frontières de crash avec nouveaux processus et os._exit(73).
- Position MNQ = 1, ordre, fill, outbox, inbox, effets et ACK restaurés sans nouveau fill au retry.
- Une demande MNQ +2 après restauration est refusée par les limites existantes ; Risk Engine inchangé.
- État final L5/outbox/inbox et effet mémoire identiques à une exécution indépendante de référence.
- Base absente en RESUME, manifeste différent, corruption simple ou rehashée, stale writer,
  outcome étranger, ACK forgé et autorités mémoire/EventBus absentes, conflictuelles ou étrangères refusés.
- Handler mémoire obligatoire conduit séparément émission et livraison à COMPLETED puis reste replayable.
- Suite complète : 5892 passed, 6 warnings in 77.02s. Ruff, py_compile et git diff --check passent.
- Hashes SHA-256 : sqlite_l5_recovery.py 4e64a636...7701 ; test 2de24c89...f1b6.
- Après fusion #242, le test d'intégration complet de ce profil a été relancé depuis
  d41103265f3afc5e324a01d45dd66b14bea0d148 : 24 passed in 30.01s.
- Suite complète de la branche documentaire : 5892 passed, 6 warnings in 114.32s.
- Les retries utilisent le même intent MNQ dans de nouveaux processus ; la comparaison finale
  impose un seul ordre, fill et effet mémoire, avec document L5 et effets identiques à une
  exécution indépendante de référence.

## Portée actuelle de D003

L'audit D003_NQ_MNQ_LINEAGE_READONLY est terminé et intégré. Son verdict historique reste
BLOCKED_PROVENANCE pour la filiation legacy MNQ : aucune nouvelle preuve ne l'annule.
La décision de pilotage du 2026-09-19 retire cependant ce blocage du statut global du projet.
D002, SINK-B3 et Gate 5 restent acquis et ne sont pas recommencés.

L'archive existante autorisée a un SHA-256 recalculé conforme à la déclaration et contient neuf fichiers.
Elle et ses membres restent EXPOSED_DEVELOPMENT, sans admissibilité comme holdout OOS ou preuve indépendante.
Le disque Windows de rapports n'est pas accessible dans cet environnement. Une extraction assainie
conservée contient les 83 entrées historiques ; leurs originaux n'ont pas été relus. Les doublons sont
conservés. Les 145 manifestes locaux supplémentaires ont été lus séparément et ne remplacent pas ces 83.
Aucun hash des neuf membres ne correspond directement aux input_sha256 de ces deux ensembles.
Aucun des 228 enregistrements ne fournit source_raw_sha256, parent_dataset_sha256 ou commande de transformation.
Cette absence de lien direct ne prouve pas une différence de contenu économique après transformation.

Les entrées NQ_* restent LEGACY_UNVERIFIED et leur instrument réel reste UNKNOWN_INSTRUMENT :
un nom de fichier seul ne suffit pas à établir NQ. Elles ne deviennent jamais des preuves MNQ.
L'identité réelle des contrats reste UNKNOWN : nom, étiquette et coût ne sont pas des preuves.
Le candidat séparé reste CANDIDATE_MNQ_NOT_LINKED ; le registre historique le classe déjà comme exposé.
Son hash est documentaire, non recalculé dans cet audit ; aucun fichier de données du candidat/OOS n'a été ouvert.
Le manifeste privé assaini contient uniquement les douze champs autorisés, sans prix ni ligne OHLCV.
Les exports, le registre privé et le manifeste détaillé ne sont pas versionnés dans ce dépôt public.

Une preuve d'export/transformation existante, assainie, reliant un membre de l'archive par SHA-256
à un input_sha256 de rapport avec identité de contrat attestée peut encore débloquer la filiation legacy.
Elle n'est plus un prérequis à la création d'une nouvelle lignée MNQ propre. Ne jamais reconstruire
une preuve à partir des noms ni requalifier rétrospectivement les anciens résultats.

Deux chaînes de preuve sont désormais obligatoires et non substituables : NQ et MNQ conservent
séparément source, dataset versionné, SHA-256, backtest, replay, validation du risque et résultats paper.
Les résultats peuvent être comparés, jamais fusionnés. Pour toute nouvelle lignée, le contrat G6
de provenance reste requis avant son protocole quantitatif :
sémantique des timestamps de barres et fuseau/DST ; règle de rollover et identité des contrats ;
sémantique OHLCV/volume ; calendrier de sessions, jours fériés et clôtures anticipées ; hash,
période et frontières garantissant que l'OOS reste réservé. Aucun de ces éléments ne peut être
inféré silencieusement.

Prochaine tranche technique non bloquée : figer et tester le contrat de manifeste d'une nouvelle
lignée de données, sans acquérir de données, lire l'OOS, lancer de replay ou modifier stratégie/Risk Engine.
EMA_PULLBACK_V1 sera ensuite formalisée puis validée séparément comme EMA_PULLBACK_V1_NQ et
EMA_PULLBACK_V1_MNQ. Toute règle métier ambiguë impose une gate stratégie avant implémentation.
V1_VALIDATED_OFFLINE_PAPER n'est pas atteint.

## Contrat de nouvelle lignée intégré

La tranche DATASET_LINEAGE_MANIFEST_V1 ajoute un contrat de métadonnées déterministe et fail-closed.
Elle exige instrument explicite, preuve d'identité du contrat hashée, source/exporteur/version/date,
hashes source/dataset/parent, transformation, intervalle, timestamp/fuseau/DST, rollover, OHLCV/volume,
sessions/calendrier et rôle. Elle sépare NQ de MNQ, refuse les parents croisés, doublons, cycles,
parents absents et réutilisations inter-instruments d'un hash déjà enregistré.

OOS_TEST exige une source UNEXPOSED, un accès SEALED et une frontière dédiée ; une source ne peut
alimenter à la fois OOS et développement. Le validateur ne lit aucun dataset : son PASS structurel
n'est ni une preuve d'instrument, ni PROVENANCE_CONFIRMED, ni une validation de stratégie.

Preuves locales : 17 tests ciblés PASS en 0.10s ; suite complète 5909 passed, 6 warnings
in 110.62s ; Ruff, py_compile et git diff --check PASS. CI #173 sur le head exact :
5909 passed, 6 warnings in 132.04s ; contrôle whitespace PASS. L'arbre fusionné est identique
à l'arbre local testé et à l'arbre publié.

Action unique qui restait alors pour la gate CLEAN_LINEAGE_SOURCE_EVIDENCE : fournir le dossier
technique assaini d'un nouvel export MNQ destiné à DEVELOPMENT — source/fournisseur,
logiciel/version, date UTC,
contract_id et preuve d'identité hashée, intervalle, timestamp/fuseau/DST, rollover, OHLCV/volume,
sessions/jours fériés, nom/hash source et transformation/parent. Les octets de marché restent privés ;
les valeurs UNKNOWN ne sont pas acceptées. Ne pas ouvrir, déplacer ni reclasser l'OOS.

## Audit du candidat MNQ 06-26 Minute/Last

Le fichier privé `MNQ 06-26.Last.txt` a été audité localement sans publier de ligne OHLCV ni de
prix. Son SHA-256, identique sur deux lectures, est
`46f2e42304573bd5e9a6c8c78a83a3cd655d493c9c1c0dc66fa2ed7406793b40` ; il contient 42 541
lignes pour 2 265 516 octets. Les six champs séparés par point-virgule, les timestamps source-naive
du `2026-04-29 22:01:00` au `2026-06-11 21:00:00`, l'ordre strict, l'absence de doublon et les
invariants structurels OHLC/volume passent. Le RAW reste privé et hors Git.

Ces faits établissent seulement une structure `BAR_ONLY_DEVELOPMENT`. Le fichier n'embarque ni
en-tête, ni instrument, ni fuseau, ni provenance. Le nom et la déclaration fournie ne prouvent donc
pas l'identité `MNQ 06-26`, le fournisseur, la version exacte NinjaTrader, la date UTC d'export,
la sémantique des timestamps, le template Trading Hours, le calendrier, l'application effective de
`DoNotMerge` ou l'absence de réécriture. Aucun manifeste canonique n'a été préparé avec des valeurs
inventées. Le dossier assaini est conservé sous
`docs/evidence/MNQ_06-26_DEVELOPMENT_EVIDENCE/` avec statut `BLOCKED_HUMAN_GATE`.

Preuves logicielles de cette tranche : 17 tests de filiation PASS ; suite complète 5909 passed,
6 warnings in 88.83s ; Ruff passe sur le contrat de filiation et py_compile passe. Le contrôle Ruff
global expose 1494 constats historiques hors périmètre sur `main` ; aucun fichier Python n'est modifié.

Action humaine qui restait alors requise : fournir un seul bundle assaini et hashable, lié au SHA-256 ci-dessus,
avec les écrans NinjaTrader originaux d'export, Help/About, fournisseur, fuseau, `DoNotMerge` et
Trading Hours, plus un reçu indiquant date UTC, sémantique des timestamps, fuseau IANA/DST,
calendrier, sémantique OHLC/volume et absence ou présence de réécriture. Les comptes et prix doivent
être masqués. La gate `CLEAN_LINEAGE_SOURCE_EVIDENCE` était bloquée jusqu'à cette pièce.

## Dérogation provisoire EXPOSED_DEVELOPMENT

La décision humaine du 2026-09-20 autorise un profil provisoire strictement limité au développement
exposé. Le bundle assaini `MNQ_06-26_NINJATRADER_SANITIZED_BUNDLE.zip`, SHA-256
`853edb74f4439f4a0d984c91cab04a34d6880df7cf11cd17c8ef520360fc4d19`, contient sept captures
et un reçu dont l'intégrité a été vérifiée. Les captures montrent `MNQ 06-26`, `Minute`,
`Last / Dernier`, `DoNotMerge / Ne pas fusionner` et le début du fuseau Windows
`(UTC+01:00) Bruxelles, Copenhague, Madrid, Paris`. Elles ne relient pas temporellement ces réglages
à l'export original du RAW.

Le manifeste `provisional_development_profile.json` sépare chaque fait en `VERIFIED_EVIDENCE`,
`OWNER_DECLARED`, `WORKING_ASSUMPTION` ou `UNKNOWN_NOT_APPROXIMABLE`. `APEX` est seulement
l'environnement commercial déclaré par le propriétaire et ne devient pas le fournisseur technique
du flux. Les hypothèses NinjaTrader 8.x, Europe/Paris, DST européen, CME US Index Futures ETH,
timestamp de fin de barre, `DoNotMerge` et barres Minute/Last portent toutes la restriction
`NOT_VALID_FOR_OOS_OR_PERFORMANCE_CLAIMS`.

`D003_PROVISIONAL_DEVELOPMENT = PASS_WITH_ASSUMPTIONS` autorise uniquement le test du parseur,
du pipeline déterministe, des contrôles structurels, le développement des outils et des résultats
exploratoires explicitement non indépendants. Il n'autorise aucune validation de stratégie,
rentabilité, OOS, paper trading, décision Apex Eval/PA/réelle ou calibration définitive du Risk Engine.
Le RAW, les captures et l'OOS restent hors Git.

À l'issue de cette tranche provisoire, `CLEAN_LINEAGE_SOURCE_EVIDENCE` restait
`BLOCKED_HUMAN_GATE`. La gate précise était
`CONTEMPORANEOUS_RAW_EXPORT_ATTESTATION_REQUIRED` : version NinjaTrader exacte, fournisseur
technique réel, date UTC, liaison contemporaine export/SHA-256, Trading Hours et calendrier
effectivement appliqués, ainsi que preuve que les octets sont l'export intact restent non
approximables.

Validations de cette tranche : JSON et classifications PASS ; scan anti-fuite de lignes marché PASS ;
17 tests de filiation PASS en 0.09s ; suite complète 5909 passed, 6 warnings in 123.49s ;
`git diff --check` PASS. Aucun fichier Python n'est modifié.

## D003 — nouvelle lignée MNQ 06-26 propre

La preuve complémentaire `PRESERVED_EXPORT_ATTESTATION.txt`, SHA-256
`043a4467a26c9494f61526a6a2d4cb0f5187837bf2fd1cc311677c729debbf59`, a été vérifiée sur ses
octets exacts. Elle enregistre les noms, `CreationTime`, `LastWriteTime`, fuseau/offset NTFS,
tailles et SHA-256 des exports Ask, Bid et Last. Les trois tailles et empreintes correspondent aux
RAW privés déjà audités. Leur création est strictement successive entre 19:36:06Z et 19:36:52Z.

La combinaison acceptée par le contrat fail-closed est : captures NinjaTrader pré-export hashées,
version `8.0.28.0 64-bit`, chaîne Apex/Rithmic/NinjaTrader, `DoNotMerge`, template
`CME US Index Futures ETH`, règle documentée UTC/fin de barre, métadonnées système exactes, hashes
des trois RAW et attestation de conservation post-export. L'attestation ne prétend pas prouver à
elle seule la sémantique des timestamps ; cette propriété reste sourcée séparément par la règle
documentée du format d'export NinjaTrader.

La racine canonique `DEVELOPMENT` / `EXPOSED_DEVELOPMENT` est désormais
`MNQ 06-26.Last.txt`, SHA-256
`3bd8c078d40143ccb1977562e47afadfd173f9c123e3a062ba28dbcb7721ba1a`. Elle est un root sans
transformation ni parent. Ask `604964a5...e0e6d51` et Bid `2437ecf0...be960b` sont des preuves
associées, pas des parents. Le manifeste canonique price-free est conservé sous
`docs/evidence/MNQ_06-26_CLEAN_LINEAGE/`.

Le RAW antérieur `46f2e423...793b40` reste explicitement `PROVISIONAL`; il n'est ni reclassé,
ni parent de la nouvelle lignée. `CLEAN_LINEAGE_SOURCE_EVIDENCE = PASS` ferme D003 uniquement pour
la nouvelle racine exposée de développement. Cela ne valide ni OOS, ni performance, ni replay,
ni paper trading, ni trading réel, et ne permet aucune calibration définitive du Risk Engine.

Validations de clôture D003 : 20 tests ciblés manifeste/filiation PASS ; 108 tests ciblés incluant
séparation NQ/MNQ, scellement OOS et déterminisme/replay PASS ; suite complète 5 912 passed,
6 warnings in 79.70s. JSON, Ruff ciblé, format Ruff, `py_compile`, scan anti-fuite et
`git diff --check` passent.

## EMA_PULLBACK_V1_MNQ — prédicat pullback initial figé

La décision métier du 2026-09-22 fixe sans optimisation la fenêtre de pullback aux trois bougies
clôturées immédiatement antérieures à la confirmation. Au moins l'une d'elles doit toucher l'EMA20
ou placer sa plage complète à une distance inférieure ou égale à huit ticks MNQ, soit 2,00 points.
Une mèche peut traverser l'EMA20 : l'intersection de la plage `Low..High` avec l'EMA vaut distance
zéro. La bougie de confirmation est exclue de cette recherche.

La confirmation LONG exige `Close > EMA20` et la confirmation SHORT exige `Close < EMA20` ;
l'égalité est refusée. Les trois indices antérieurs doivent être strictement `t-3`, `t-2`, `t-1`.
Le contrat travaille exclusivement sur des bougies clôturées, décide à la clôture `t` et conserve
l'exécution au plus tôt sur `t+1`. L'évaluation en `Decimal` protège la limite inclusive de huit ticks.

Le module `ema_pullback_v1_mnq.py` évalue ce sous-prédicat sans émettre de signal de trading. Le
croisement MACD reste obligatoire, sans valeur par défaut. Stop-loss, take-profit et filtres de
session restent également hors du contrat exécutable. Aucun dataset, OOS, PnL, replay, Risk Engine
ou broker n'est utilisé.

Preuves de cette tranche : 14 tests synthétiques PASS couvrent LONG, SHORT, distance exactement
huit ticks, rejet à neuf ticks, mèche traversante, clôture égale refusée, exclusion de la confirmation
et causalité stricte. Les 56 tests stratégie ciblés passent ; la suite complète passe avec
5 926 tests et 6 warnings historiques en 255,75 s. Ruff ciblé, format Ruff, `py_compile` et
`git diff --check` passent. Cette tranche a été intégrée par la PR #251, merge
bc9508ddd05b3537438c7fa9fe48ba55902af5ec.

## EMA_PULLBACK_V1_MNQ — pente EMA20 initiale figée

La décision métier du 2026-09-23 fixe sans optimisation `K = 3` et la formule causale
`(EMA20[t] - EMA20[t-3]) / 3`, en points par bougie. Le seuil minimal est exactement
`0,0 point/bar`. LONG exige une pente strictement positive ; SHORT exige une pente strictement
négative. Une pente nulle, y compris l'égalité exacte au seuil, est refusée. Aucune force minimale
supplémentaire n'est ajoutée.

L'évaluation accepte uniquement deux valeurs EMA20 fournies sur des bougies déjà clôturées : la
confirmation `t` et la référence exactement `t-3`. Un warmup insuffisant ou tout autre écart
d'indice échoue explicitement. Le calcul en `Decimal` conserve le signe de valeurs positives ou
négatives arbitrairement faibles et n'utilise aucun point futur. Il ne calcule pas l'EMA20.
L'assemblage décrit ci-dessous combine désormais les trois prédicats en signal non exécutable ;
il ne crée aucun ordre.

Preuves locales : les 12 nouveaux cas de pente portent le fichier synthétique à 26 tests PASS et
couvrent LONG, SHORT, zéro, égalité au seuil, valeurs très faibles positives/négatives, warmup
insuffisant et rejet des indices non causaux. Les 68 régressions stratégie passent ; la suite
complète passe avec 5 938 tests et 6 warnings historiques en 86,03 s. Ruff ciblé et format Ruff
passent, ainsi que `py_compile`, les 4 gardes de confidentialité, `git diff --check` et le scan
anti-fuite des ajouts. Aucun fichier binaire ou ligne de marché n'est présent dans le diff.

Cette tranche a été intégrée par la PR #252, merge
8c90ba79fb0492676cbb321c7c5ee41a46ca8f8b. `EMA_PULLBACK_V1_MNQ_EMA20_SLOPE = PASS`.

## EMA_PULLBACK_V1_MNQ — MACD et signal d'entrée assemblé

La décision métier du 2026-09-23 fixe sans optimisation le MACD `12/26/9`. La ligne MACD est
`EMA12(Close) - EMA26(Close)` et sa ligne signal est `EMA9(MACD_LINE)`. Les deux calculs réutilisent
directement `market_replay.calculate_ema`, convention déterministe existante avec amorçage au
premier close et `alpha = 2 / (period + 1)` ; aucune seconde implémentation d'EMA n'est introduite.

Le croisement haussier exige `MACD[t-1] <= SIGNAL[t-1]` puis `MACD[t] > SIGNAL[t]`. Le croisement
baissier exige `MACD[t-1] >= SIGNAL[t-1]` puis `MACD[t] < SIGNAL[t]`. L'égalité est donc admise
uniquement à `t-1` et refusée à `t`. La validité vaut exactement la bougie clôturée courante : un
croisement antérieur n'est jamais réutilisé. Trente-cinq bougies clôturées causales et contiguës
sont requises pour disposer du warmup EMA26, du warmup EMA9 et des deux points `t-1`/`t` ; sinon
`macd_status = INSUFFICIENT_WARMUP` et `signal = NONE`.

L'assembleur émet un signal non exécutable LONG ou SHORT seulement lorsque, sur la même confirmation
`t`, le pullback et la clôture directionnelle, la pente EMA20 et le nouveau croisement MACD qualifient
tous le même côté. Toute condition absente produit `NONE`. Les valeurs postérieures à `t` sont
ignorées ; l'exécution reste au plus tôt sur `t+1`, sans prix ni politique d'ordre encore présumés.

Preuves locales : 41 tests synthétiques ciblés PASS en 0,07 s, dont croisement haussier/baissier,
égalité à `t-1`, égalité refusée à `t`, absence de nouveau croisement, warmup insuffisant, causalité,
mutation de `t+1`, assemblages LONG/SHORT et refus si un prédicat manque. Les 90 régressions stratégie
et replay ciblées passent en 0,23 s. La suite complète passe avec 5 953 tests et 6 warnings historiques
en 85,88 s. Ruff ciblé et format Ruff, `py_compile`, les 4 gardes de confidentialité et
`git diff --check` passent. Aucun dataset, OOS, PnL, replay de données, Risk Engine, broker ou ordre
n'a été utilisé ; le diff ne contient aucun fichier ni ligne de marché.

`EMA_PULLBACK_V1_MNQ_MACD = PASS` et `EMA_PULLBACK_V1_MNQ_ENTRY_SIGNAL = PASS`.

Cette tranche a été intégrée par la PR #253, merge
b4573f3b7525dff4e1af33541e5ccec6e1c662f0.

## EMA_PULLBACK_V1_MNQ — sortie principale EMA20 figée

La décision métier du 2026-09-23 fixe sans optimisation la sortie principale d'une position. Une
position LONG qualifie une sortie uniquement si `Close[t] < EMA20[t]`. Une position SHORT qualifie
une sortie uniquement si `Close[t] > EMA20[t]`. L'égalité exacte produit `HOLD` pour les deux côtés.

Seule la clôture de la bougie `t` est évaluée. Une mèche sous EMA20 pour LONG, ou au-dessus pour
SHORT, ne déclenche aucune sortie lorsque la clôture reste du bon côté ou égale à EMA20. Le résultat
est un prédicat non exécutable `EXIT_LONG`, `EXIT_SHORT` ou `HOLD` ; il ne contient ni ordre ni prix
de fill. L'exécution sur `t` est explicitement interdite et le premier indice admissible exposé est
`t+1`. La sélection exacte de la bougie `t` rend toute mutation de `t+1` sans effet.

Preuves locales : neuf nouveaux cas portent le fichier synthétique à 50 tests PASS en 0,14 s. Ils
couvrent sorties LONG/SHORT, égalité des deux côtés, mèches traversantes sans clôture adverse,
causalité, mutations opposées de `t+1`, premier indice d'exécution, bougie `t` absente et doublonnée.
Les 99 régressions stratégie/replay ciblées passent en 0,20 s. La suite complète passe avec
5 962 tests et 6 warnings historiques en 85,10 s. Aucun dataset, OOS, PnL, replay de données,
Risk Engine, broker ou ordre n'a été utilisé.

`EMA_PULLBACK_V1_MNQ_EMA20_POSITION_EXIT = PASS`.

Cette tranche a été intégrée par la PR #254, merge
0880da6fb2dd916ba53ed1caf069f66342130f67.

## EMA_PULLBACK_V1_MNQ — toucher/proximité EMA20 sur la deuxième bougie

La décision métier du 2026-09-26 précise, sans optimisation, le prédicat de pullback. Dans la
fenêtre ordonnée `t-3`, `t-2`, `t-1`, la deuxième bougie est exactement `t-2`. Sa plage fermée
`Low[t-2]..High[t-2]` doit toucher/croiser `EMA20[t-2]` ou s'en approcher à une distance maximale
inclusive de huit ticks MNQ, soit 2,00 points. Un contact par une extrémité ou une mèche traversante
vaut une distance nulle.

La condition de distance s'applique uniquement à `t-2`. Un contact ou une proximité admissible sur
`t-3` ou `t-1` ne remplace jamais un `t-2` situé à plus de huit ticks. La confirmation directionnelle,
la pente EMA20, le croisement MACD, la causalité à la clôture `t` et l'exécution au plus tôt sur
`t+1` restent inchangés.

Preuves locales : le fichier synthétique passe avec 54 tests en 0,18 s. Il couvre LONG/SHORT,
contact par mèche, contacts aux deux extrémités, acceptation de la limite exacte de huit ticks,
rejet à neuf ticks et lorsque seul `t-3` ou `t-1` satisfait, clôture directionnelle et causalité. Les 103 régressions
stratégie/replay ciblées passent en 0,30 s. La suite complète passe avec 5 966 tests et 6 warnings
historiques en 106,30 s. Ruff ciblé, format Ruff et `py_compile` passent. Aucun dataset, OOS, PnL,
replay de données, Risk Engine, broker ou ordre n'a été utilisé.

`EMA_PULLBACK_V1_MNQ_T_MINUS_2_TOUCH_OR_PROXIMITY = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — NEXT_BAR_EXECUTION_MODEL_REQUIRED`.
Action humaine unique : confirmer ou corriger le modèle candidat suivant pour les entrées et sorties :
un signal formé à la clôture `t` produit un ordre simulé MARKET rempli à `Open[t+1]`, et expire sans
fill si la bougie `t+1` n'existe pas. Aucun type d'ordre, prix de fill ou comportement de fin de série
n'est présumé avant cette décision. Stop-loss, take-profit, trailing stop, breakeven et priorité entre
sorties restent volontairement non définis.

## Limites du produit

V1_VALIDATED_OFFLINE_PAPER non atteint. D002 prouve le sink mémoire canonique ; les PR #241/#242
et le nouvel audit prouvent la reconstruction et la Gate 5 du profil offline borné, pas le runtime global complet.
SignalLoopOrchestrator et RuntimeEventBridge restent hors garantie durable initiale (D001).
Aucun ancien événement legacy migré implicitement. Aucun accès data/, secret ou broker.
Le CAS protège la publication des journaux, pas l'exécution concurrente d'un callback externe ;
les sinks obligatoires conservent leur propre contrat d'idempotence. Une ancre conservée hors
de la base reste nécessaire pour détecter le rollback cohérent de toute la base SQLite.
Les entrées et la sortie principale EMA20 de la stratégie personnelle sont désormais formalisées.
Le modèle d'exécution et les sorties protectrices restent à définir avant son évaluation ; cette
stratégie demeure distincte de EMA19/50 V3 rejetée.
