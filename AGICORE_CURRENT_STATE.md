# AGIcore current state — checkpoint

Date : 2026-10-09 UTC.
Statut : BLOCKED_HUMAN_GATE — EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE ;
CLEAN_LINEAGE_SOURCE_EVIDENCE = PASS ; D003_PROVISIONAL_DEVELOPMENT = PASS_WITH_ASSUMPTIONS ;
EMA_PULLBACK_V1_MNQ_PULLBACK_PREDICATE = PASS ;
EMA_PULLBACK_V1_MNQ_EMA20_SLOPE = PASS ;
EMA_PULLBACK_V1_MNQ_MACD = PASS ;
EMA_PULLBACK_V1_MNQ_ENTRY_SIGNAL = PASS ;
EMA_PULLBACK_V1_MNQ_EMA20_POSITION_EXIT = PASS ;
EMA_PULLBACK_V1_MNQ_T_MINUS_2_TOUCH_OR_PROXIMITY = PASS ;
EMA_PULLBACK_V1_MNQ_NEXT_BAR_EXECUTION = PASS ;
EMA_PULLBACK_V1_MNQ_INITIAL_STRUCTURAL_STOP = PASS ;
EMA_PULLBACK_V1_MNQ_TAKE_PROFIT_NONE = PASS ;
EMA_PULLBACK_V1_MNQ_EXIT_PRIORITY = PASS ;
EMA_PULLBACK_V1_MNQ_BREAKEVEN_NONE = PASS ;
EMA_PULLBACK_V1_MNQ_TRAILING_STOP_NONE = PASS ;
EMA_PULLBACK_V1_MNQ_SESSION_FILTER_NONE = PASS ;
EMA_PULLBACK_V1_MNQ_OPEN_POSITION_SIGNAL_POLICY = PASS ;
EMA_PULLBACK_V1_MNQ_FIXED_POSITION_SIZE_ONE_MNQ = PASS ;
EMA_PULLBACK_V1_MNQ_END_OF_DATA_KEEP_OPEN_UNREALIZED = PASS ;
EMA_PULLBACK_V1_MNQ_FEES_AND_SLIPPAGE_MODEL = PASS ;
EMA_PULLBACK_V1_MNQ_FORMALIZATION = PASS ;
EMA_PULLBACK_V1_MNQ_DEVELOPMENT_SCREENING_PROTOCOL = PASS ;
EMA_PULLBACK_V1_MNQ_DEVELOPMENT_REPLAY_EXECUTION = COMPLETED_ONCE ;
EMA_PULLBACK_V1_MNQ_DEVELOPMENT_SCREENING_VERDICT = NO_GO_BASELINE ;
EMA_PULLBACK_V1A_MNQ_VARIANT_PROTOCOL = PASS ;
EMA_PULLBACK_V1A_MNQ_DEVELOPMENT_REPLAY_EXECUTION = COMPLETED_ONCE ;
EMA_PULLBACK_V1A_MNQ_DEVELOPMENT_SCREENING_VERDICT = NO_GO_VARIANT ;
EMA_PULLBACK_V1B_MNQ_VARIANT_PROTOCOL = PASS ;
EMA_PULLBACK_V1B_MNQ_DEVELOPMENT_REPLAY_EXECUTION = COMPLETED_ONCE ;
EMA_PULLBACK_V1B_MNQ_DEVELOPMENT_SCREENING_VERDICT = NO_GO_VARIANT ;
EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_PROTOCOL = PASS ;
EMA_PULLBACK_V1B_MNQ_03_26_CLEAN_LINEAGE = PASS ;
EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_IMPLEMENTATION = PASS ;
EMA_PULLBACK_V1B_MNQ_03_26_REPLAY_EXECUTION = COMPLETED_ONCE ;
EMA_PULLBACK_V1B_MNQ_03_26_SCREENING_VERDICT = NO_GO_VARIANT ;
EMA_PULLBACK_V1B_MNQ_03_26_EXPERIMENT_OUTCOME = STOP_INCREMENTAL_EMA_PULLBACK_V1_PATH ;
EMA_PULLBACK_V1_PATH = TERMINATED ;
STRATEGY_FAMILY = EMA_PULLBACK_V2_REGIME_GATED ;
STRATEGY_ID = EMA_PULLBACK_V2_REGIME_GATED_BASELINE ;
FORMALIZATION_VERSION = 1 ; MODE = OFFLINE_DETERMINISTIC ;
EMA_PULLBACK_V2_REGIME_GATED = FORMALIZED_PRE_REPLAY ;
REGIME_CONTEXT_V2_EVENT_COMPOSITION = IMPULSE_OR_REVERSAL_DISTINCT ;
REGIME_CONTEXT_V2_EVENT_COMPOSITION_STATUS = PASS ;
DIRECTIONAL_IMPULSE_EMERGING_DIRECTION = PASS ;
DIRECTIONAL_IMPULSE_EVENT_RANGE = PASS ;
DIRECTIONAL_IMPULSE_EVENT_VOLUME = PASS ;
DIRECTIONAL_IMPULSE_EVENT_BODY_WICK = PASS ;
DIRECTIONAL_IMPULSE_EVENT = PASS ;
REVERSAL_TRANSITION_EVENT_PRIOR_DIRECTION = PASS ;
REVERSAL_TRANSITION_EVENT_REJECTION_BAR = PASS ;
REVERSAL_TRANSITION_EVENT_OPPOSITE_TRANSITION = PASS ;
REVERSAL_TRANSITION_EVENT = PASS ;
REGIME_CONTEXT_V2_EVENT_LIFETIME = PASS ;
EMA20_PULLBACK_V2 = PASS ;
EMA_PULLBACK_V2_ENTRY_CONFIRMATION_MOMENTUM = PASS ;
EMA_PULLBACK_V2_ENTRY_EXECUTION = PASS ;
EMA_PULLBACK_V2_INITIAL_STOP = PASS ;
EMA_PULLBACK_V2_STRUCTURAL_STOP_TRIGGER_FILL = PASS ;
EMA_PULLBACK_V2_OPEN_POSITION_SIGNAL_POLICY = PASS ;
EMA_PULLBACK_V2_RISK_ENGINE_POSITION_SIZING = PASS ;
EMA_PULLBACK_V2_FEES_AND_SLIPPAGE_MODEL = PASS ;
EMA_PULLBACK_V2_EXIT_POLICY = PASS ;
EMA_PULLBACK_V2_PENDING_OPPORTUNITY_POLICY = PASS ;
EMA_PULLBACK_V2_FORMALIZATION = PASS ;
EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL = PASS, PR #301 fusionnée après CI verte ;
EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE = BLOCKED_HUMAN_GATE ;
EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION = PASS_PRECOMMITTED, PR #306 fusionnée ;
EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION = PASS ;
REAL_PARENT_TRANSFORMATION = EXECUTED_ONCE ; REAL_STRATEGY_REPLAY = NOT_EXECUTED ;
NEXT = EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED ;
le RAW legacy reste PROVISIONAL et D003 legacy reste BLOCKED_PROVENANCE.
Branche de vérification : feature/ema-pullback-v2-transformation-execution.
Base GitHub vérifiée : 7e46769f3b12ba8cf71e20cdf99b057bef4c5310.

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

Cette tranche a été intégrée par la PR #255, merge
eadd4f3df578c8fec252e91fe6850a7d8d882886.

## EMA_PULLBACK_V1_MNQ — modèle d'exécution bar-based figé

La décision métier du 2026-09-26 fixe sans optimisation le modèle initial commun aux entrées et à
la sortie principale EMA20. Une décision qualifiée à la clôture de `t` produit un ordre simulé
`MARKET`, rempli exclusivement à `Open[t+1]`. L'exécution sur `t`, à `Close[t]`, au dernier prix
connu ou sur une bougie ultérieure arbitraire est interdite.

Si la bougie exacte `t+1` est absente, le résultat est `EXPIRED_NO_EXECUTION`, sans prix inventé.
Une entrée expirée n'ouvre aucune position et une sortie expirée ne ferme pas artificiellement la
position. Les bougies postérieures à `t+1` sont ignorées ; leur mutation ne peut modifier le fill.
Une décision non qualifiée, un indice de décision incohérent ou un doublon de `t+1` échoue
explicitement.

Ce modèle est volontairement bar-based. Il ne modélise ni slippage, ni spread Bid/Ask, ni latence,
ni fill tick-réaliste, et n'exécute aucune action broker ou live. Ces limites sont exposées dans le
contrat plutôt que transformées en hypothèses silencieuses.

Preuves locales : douze nouveaux cas portent le fichier synthétique à 66 tests PASS en 0,26 s. Ils
couvrent les entrées LONG/SHORT, les sorties LONG/SHORT, l'absence de `t+1`, l'indépendance vis-à-vis
des bougies postérieures, l'interdiction de `Close[t]` et du same-bar, la répétabilité, les doublons
et les décisions non qualifiées. Les 115 régressions stratégie/replay ciblées passent en 0,30 s.
La suite complète passe avec 5 978 tests et 6 warnings historiques en 108,56 s. Ruff ciblé, format
Ruff, `py_compile` et `git diff --check` passent. Aucun dataset, OOS, PnL, replay de données, Risk
Engine, broker ou ordre réel n'a été utilisé.

`EMA_PULLBACK_V1_MNQ_NEXT_BAR_EXECUTION = PASS`.

Cette tranche a été intégrée par la PR #256, merge
f9cc8c835b538d7df1ad0a660cabb7da619f13db.

## EMA_PULLBACK_V1_MNQ — stop structurel initial figé

La décision métier du 2026-09-26 fixe sans optimisation un stop structurel construit à la clôture
de `t` depuis la bougie obligatoire `t-2`. LONG utilise `Low[t-2] - 0,25 point` et SHORT utilise
`High[t-2] + 0,25 point`, soit exactement un tick MNQ de marge. Une décision d'entrée qualifiée,
une barre de décision exactement `t` et une source exactement `t-2` sont obligatoires.

Le stop est calculé avant l'ouverture éventuelle de la position à `Open[t+1]`, puis stocké dans un
objet immuable. LONG refuse l'entrée si `stop >= entry_price` ; SHORT la refuse si
`stop <= entry_price`. Une barre `t+1` absente conserve `EXPIRED_NO_EXECUTION` et n'ouvre aucune
position.

Pour une position ouverte, LONG déclenche lorsque `Low[k] <= stop` et SHORT lorsque
`High[k] >= stop`. Un gap strict au-delà du stop est rempli à `Open[k]`; sinon une touche intrabar
inclusive est remplie au niveau du stop. Cette convention est bar-based et ne prétend pas modéliser
le slippage réel. Aucun recalcul automatique, breakeven, trailing stop, ATR, stop monétaire ou
Risk Engine dynamique n'est introduit.

Preuves locales : dix-neuf nouveaux cas portent le fichier synthétique à 85 tests PASS en 0,25 s.
Ils couvrent LONG/SHORT, marge d'un tick, touche exacte, distance d'un tick sans déclenchement,
gaps, immutabilité, quatre frontières de rejet d'entrée, expiration, causalité et absence de
lookahead. Les 131 régressions stratégie/replay ciblées passent en 0,47 s. La suite complète passe
avec 5 997 tests et 6 warnings historiques en 129,21 s. Ruff ciblé, format Ruff, `py_compile`,
gardes de confidentialité, scan anti-fuite et `git diff --check` passent.

`EMA_PULLBACK_V1_MNQ_INITIAL_STRUCTURAL_STOP = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — TAKE_PROFIT_RULE_REQUIRED`.
Action humaine unique : définir la règle initiale exacte de prise de profit LONG et SHORT, sans
l'optimiser sur les données. Breakeven, trailing stop et priorité entre sorties restent non définis.

Cette tranche a été intégrée par la PR #257, merge
2a9b334dbeb881f5b233534cd97863e646fe56f7.

## EMA_PULLBACK_V1_MNQ — absence de take-profit figée

La décision métier du 2026-09-26 fixe `TAKE_PROFIT = NONE`,
`take_profit_enabled = false` et `take_profit_price = null`. V1 ne contient aucune cible fixe,
monétaire, en ticks, en points ou en multiple de risque. Aucun niveau favorable, gain latent ou
seuil de PnL ne peut produire une sortie take-profit implicite.

Une position reste donc ouverte jusqu'au stop structurel initial ou jusqu'à une décision de sortie
EMA20 déjà définie. Cette absence de take-profit est une décision initiale sans optimisation. Elle
n'autorise ni breakeven, ni trailing stop, et ne fixe pas l'arbitrage lorsque les deux sorties
existantes deviennent concurrentes.

Preuves locales : neuf nouveaux cas portent le fichier synthétique à 94 tests PASS en 0,23 s. Ils
couvrent LONG/SHORT, prix arbitrairement favorable, PnL extrême, absence de cible monétaire,
ticks, points et multiple de risque, refus d'une activation cachée et répétabilité. Les 140 tests
stratégie/replay ciblés passent en 0,49 s. La suite complète passe avec 6 006 tests et 6 warnings
historiques en 77,13 s. Ruff ciblé, format Ruff et `git diff --check` passent.

`EMA_PULLBACK_V1_MNQ_TAKE_PROFIT_NONE = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — EXIT_PRIORITY_RULE_REQUIRED`.
Action humaine unique : définir la priorité déterministe lorsque le stop structurel et la sortie
EMA20 peuvent tous deux fermer la même position, notamment si une sortie EMA20 en attente et un
gap au-delà du stop deviennent exécutables au même `Open[k]`.

Cette tranche a été intégrée par la PR #258, merge
8b410b9c00b0e3ff84822b068f54732d5f1886cf.

## EMA_PULLBACK_V1_MNQ — priorité des sorties figée

La décision métier du 2026-09-26 fixe `STRUCTURAL_STOP_FIRST` et la hiérarchie exclusive
`STRUCTURAL_STOP`, puis `EMA20_EXIT`. Lorsqu'une sortie EMA20 est en attente pour `Open[k]`, un
stop structurel déclenché inclusivement par cette même ouverture gagne : le fill simulé est
`Open[k]`, le motif est `STRUCTURAL_STOP` et la sortie EMA20 est annulée.

Si le stop n'est pas déclenché à `Open[k]`, la sortie EMA20 en attente est exécutée à cette
ouverture et le stop structurel est annulé. L'arbitre fail-closed impose exactement un motif,
un fill et une fermeture de position ; deux exécutions ou deux fermetures sont invalides. Seule
l'ouverture concernée participe à l'arbitrage, sans donnée intrabar future ni lookahead.

Preuves locales : quatorze nouveaux cas portent le fichier synthétique à 108 tests PASS en 0,23 s.
Ils couvrent LONG/SHORT, collision avec gap, égalité inclusive au stop, sortie EMA20 lorsque le stop
n'est pas déclenché, annulation de l'autre sortie, refus d'un double fill/d'une double fermeture,
cohérence des côtés, barre exacte et répétabilité. Les 154 tests stratégie/replay ciblés passent en
0,34 s. La suite complète passe avec 6 020 tests et 6 warnings historiques en 82,13 s. Ruff ciblé
et `py_compile` passent.

`EMA_PULLBACK_V1_MNQ_EXIT_PRIORITY = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — BREAKEVEN_RULE_REQUIRED`.
Action humaine unique : déclarer soit `BREAKEVEN = NONE`, soit la condition exacte d'activation,
le niveau de remplacement et sa convention d'exécution, sans optimisation sur les données.

Cette tranche a été intégrée par la PR #259, merge
c38482176044224fdc82a2f2fcc8d252bd38e126.

## EMA_PULLBACK_V1_MNQ — absence de breakeven figée

La décision métier du 2026-09-26 fixe sans optimisation `BREAKEVEN = NONE`,
`move_stop_to_entry = false`, `breakeven_trigger = null` et `breakeven_price = null`. Le stop
structurel initial attaché à la position reste le même objet immuable pendant toute sa durée.

Ni prix favorable, ni ticks gagnés, ni multiple de risque `R`, ni PnL monétaire, ni durée en
position ne peut déplacer le stop vers l'entrée ou vers un autre niveau. Un prix qui dépasse
l'entrée puis retrace conserve exactement le stop initial. Le contrat fail-closed refuse toute
activation, tout niveau ou tout déclencheur de breakeven caché.

Les seules sorties restent `STRUCTURAL_STOP`, puis `EMA20_EXIT`, avec la priorité déjà figée
`STRUCTURAL_STOP_FIRST`. Cette tranche n'ajoute ni trailing stop, ni nouvelle sortie, ni règle
d'exécution. L'évaluateur ne reçoit aucune barre future et conserve le même stop pour LONG et SHORT.

Preuves locales : seize nouveaux cas portent le fichier synthétique à 124 tests PASS en 0,25 s.
Ils couvrent LONG/SHORT, profit favorable, dépassement de l'entrée puis retracement, absence de
déclencheur caché, seuils 1R/2R/25R et 4/8/1 000 ticks, immutabilité après nouvelles observations,
symétrie, causalité et répétabilité. Les 170 régressions stratégie/replay ciblées passent en 0,39 s.
La suite complète passe avec 6 036 tests et 6 warnings historiques en 84,05 s. Ruff ciblé, format
Ruff et `py_compile` passent.

`EMA_PULLBACK_V1_MNQ_BREAKEVEN_NONE = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — TRAILING_STOP_RULE_REQUIRED`.
Action humaine unique : déclarer soit `TRAILING_STOP = NONE`, soit sa condition exacte
d'activation, sa formule de déplacement, sa fréquence de mise à jour et sa convention d'exécution,
sans optimisation sur les données.

Cette tranche a été intégrée par la PR #260, merge
957b1926612d00f8b48c7b5cb4acb983e0cb1205.

## EMA_PULLBACK_V1_MNQ — absence de trailing stop figée

La décision métier du 2026-09-27 fixe sans optimisation `TRAILING_STOP = NONE`,
`trailing_stop_enabled = false` et des valeurs nulles pour activation, distance, step, fréquence
de mise à jour et référence. Le stop structurel initial attaché à la position reste strictement
immuable jusqu'à sa fermeture.

Ni nouveau High/Low, ni mouvement favorable, ni ticks, ni multiple `R`, ni PnL, ni EMA20, ni
durée en position ne peut recalculer ou déplacer le stop. Le résultat fail-closed exige que le stop
actif soit exactement la même instance que `initial_structural_stop`; une copie distincte, même
égale en valeur, est refusée. Toute configuration trailing cachée est également refusée.

Les seules sorties restent `STRUCTURAL_STOP`, puis `EMA20_EXIT`, avec
`STRUCTURAL_STOP_FIRST`. `TAKE_PROFIT = NONE`, `BREAKEVEN = NONE` et `TRAILING_STOP = NONE`
forment désormais la baseline déterministe initiale de gestion de position.

Preuves locales : vingt-quatre nouveaux cas portent le fichier synthétique à 148 tests PASS en
0,12 s. Ils couvrent LONG/SHORT, nouveaux extrêmes, profits élevés, seuils 1R/2R/25R et
4/8/1 000 ticks, nouvelles observations clôturées, champs cachés, identité exacte du stop,
causalité et répétabilité. Les 152 tests contrat/confidentialité passent en 0,27 s et les 194
régressions stratégie/replay en 0,51 s. La suite complète passe avec 6 060 tests et 6 warnings
historiques en 77,15 s. Ruff ciblé, format Ruff et `py_compile` passent.

`EMA_PULLBACK_V1_MNQ_TRAILING_STOP_NONE = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — SESSION_FILTER_RULE_REQUIRED`.
Action humaine unique : déclarer soit `SESSION_FILTER = NONE`, soit les jours, heures, fuseau/DST
et règles de frontière exacts autorisant les nouvelles entrées, ainsi que le comportement des
sorties d'une position déjà ouverte hors de cette fenêtre, sans optimisation sur les données.

## EMA_PULLBACK_V1_MNQ — absence de filtre de session figée

La décision métier du 2026-09-27 fixe sans optimisation `SESSION_FILTER = NONE`,
`strategy_entry_session_filter_enabled = false` et des valeurs nulles pour jours autorisés,
heure de début, heure de fin, timezone stratégique et règle DST stratégique.

Cette absence de filtre stratégique ne remplace pas le calendrier source. L'évaluateur exige une
barre clôturée et valide déjà admise par le template exact `CME US Index Futures ETH`; une barre
non clôturée, invalide ou attribuée à un autre template est refusée fail-closed. Il ne reçoit aucun
timestamp, jour, heure locale, timezone, DST, RTH ou ETH et ne peut donc ajouter une frontière
cachée ni dépendre de l'horloge de la machine.

Toute barre source valide peut laisser une entrée qualifiée poursuivre le pipeline. Pour une
position ouverte, `STRUCTURAL_STOP` et `EMA20_EXIT` restent actifs sur chaque barre source valide.
Le contrat refuse toute suppression horaire d'une entrée ou d'une sortie. Il conserve
`STRUCTURAL_STOP_FIRST`, `TAKE_PROFIT = NONE`, `BREAKEVEN = NONE` et `TRAILING_STOP = NONE`.

Preuves locales : vingt-neuf nouveaux cas portent le fichier synthétique à 177 tests PASS en
0,45 s. Ils couvrent toute séquence de barre valide, absence de filtre temps/jour/timezone/DST,
refus du contournement du calendrier source, sorties toujours actives, immutabilité, causalité et
répétabilité. Les 181 tests contrat/confidentialité passent en 0,17 s et les 223 régressions
stratégie/replay en 0,38 s. La suite complète passe avec 6 089 tests et 6 warnings historiques en
78,59 s. Ruff ciblé, format Ruff et `py_compile` passent.

`EMA_PULLBACK_V1_MNQ_SESSION_FILTER_NONE = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — OPEN_POSITION_SIGNAL_POLICY_REQUIRED`.
Action humaine unique : définir ce que V1 fait d'un nouveau signal de même sens ou de sens opposé
alors qu'une position est déjà ouverte — l'ignorer jusqu'au retour à plat, renforcer la position,
ou fermer/inverser — sans optimisation sur les données.

## EMA_PULLBACK_V1_MNQ — nouveaux signaux ignorés tant que la position est ouverte

La décision métier du 2026-09-27 fixe sans optimisation
`OPEN_POSITION_SIGNAL_POLICY = IGNORE_ALL_NEW_SIGNALS_UNTIL_FLAT`.
À `Close[t]`, une position effectivement ouverte, LONG ou SHORT, fait ignorer tout nouveau signal
d'entrée, de même sens ou opposé. Ni ajout/pyramiding, ni renforcement, ni inversion, ni fermeture
et inversion, ni file d'attente ou exécution différée ne sont autorisés.

Une sortie EMA20 décidée à `Close[t]` reste en attente jusqu'à son éventuel fill à `Open[t+1]` :
le signal d'entrée formé à cette clôture est ignoré. Le retour à `FLAT` exige un fill de sortie
réellement enregistré, au stop structurel ou selon la priorité de sortie déjà établie. Un signal
de la clôture antérieure ne peut être réutilisé après cette fermeture ; une nouvelle entrée
requiert un nouveau signal formé sur une clôture au moins égale à la barre du fill.

Le résultat du prédicat est immuable et ne conserve ni signal ignoré, ni ordre différé. Les deux
sorties existantes et leurs priorités restent inchangées ; le calendrier source ETH reste obligatoire.
La formalisation est purement offline et ne choisit pas le nombre de contrats ni une métrique de PnL.

Preuves locales : 29 nouveaux cas portent le fichier synthétique à 206 tests PASS ; les 213 tests
stratégie/replay ciblés passent. Suite complète : 6 118 tests PASS, 6 warnings historiques en
79,84 s. Ruff ciblé, format Ruff, `py_compile` et `git diff --check` passent.

`EMA_PULLBACK_V1_MNQ_OPEN_POSITION_SIGNAL_POLICY = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — POSITION_SIZE_RULE_REQUIRED`.
Action humaine unique : choisir la taille initiale exacte d'une nouvelle position MNQ (nombre
fixe de contrats entre 1 et 2, ou formule exacte déjà approuvée), sans changer le Risk Engine ni
la limite maximale de deux contrats et sans optimiser sur les données.

## EMA_PULLBACK_V1_MNQ — taille fixe d'un contrat MNQ

La décision métier du 2026-09-27 fixe sans optimisation `POSITION_SIZE_MODE = FIXED`,
`INITIAL_POSITION_SIZE = 1 MNQ` et `MAX_POSITION_SIZE = 1 MNQ`. Après un fill causal exact à
`Open[t+1]`, une entrée LONG produit `+1 MNQ` et une entrée SHORT `-1 MNQ`. Aucun état de position
n'est créé au seul signal de `Close[t]` si le fill suivant n'est pas établi.

Le contrat ne reçoit ni solde, ni PnL, ni volatilité, ni distance du stop, ni pourcentage de risque,
ni historique de trades. Risk-percent sizing, volatility sizing, stop-distance sizing, PnL sizing,
martingale et anti-martingale sont explicitement désactivés et refusés fail-closed. Pendant une
position ouverte, la politique `IGNORE_ALL_NEW_SIGNALS_UNTIL_FLAT` conserve exactement `+1` ou
`-1` sans second fill, pyramiding ou inversion. Un fill de sortie V1 vérifié remet la taille à zéro.

Le plafond général de deux MNQ reste une contrainte supérieure externe du Risk Engine ; il n'est
ni modifié ni utilisé pour élargir la demande de cette stratégie, qui reste strictement à un MNQ.
Une comparaison future avec deux MNQ ou un sizing piloté par le Risk Engine devra constituer une
expérience séparée après mesure de cette baseline, sans modifier rétroactivement le contrat V1.

Preuves locales avant CI : 28 nouveaux cas portent le fichier synthétique à 234 tests PASS ; les
241 tests stratégie/replay ciblés et les 256 tests contrat/filiation/OOS passent. Suite complète :
6 146 tests PASS, 6 warnings historiques en 76,91 s. Ruff ciblé, format Ruff, `py_compile` et
`git diff --check` passent. Les cas couvrent LONG/SHORT, refus de ±2, modes cachés, indépendance
PnL/stop/volatilité, absence de pyramiding, sorties vers zéro et déterminisme.

`EMA_PULLBACK_V1_MNQ_FIXED_POSITION_SIZE_ONE_MNQ = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — END_OF_DATA_POSITION_POLICY_REQUIRED`.
Action humaine unique : décider le statut exact d'une position encore ouverte lorsque le flux
développement se termine — la conserver ouverte/non réalisée sans fill inventé, l'exclure des
métriques fermées, ou définir une liquidation causale explicite compatible avec le modèle t+1.

## EMA_PULLBACK_V1_MNQ — position ouverte non réalisée en fin de flux

La décision métier du 2026-09-27 fixe sans optimisation
`END_OF_DATA_POSITION_POLICY = KEEP_OPEN_UNREALIZED`. Une position LONG ou SHORT encore ouverte
après la dernière barre valide reste `OPEN_AT_END_OF_DATA`. Aucun ordre, fill, prix de sortie ou
trade fermé n'est créé au dernier Close, au dernier Open, à une cotation connue ou reconstruite.

Pour le reporting uniquement, le dernier `Close` valide devient `mark_price`. Le PnL latent est
calculé en points MNQ normalisés depuis le prix d'entrée rempli et reste séparé du PnL et de
l'equity réalisés. `realized_pnl_change = 0`, `closed_trade_count_change = 0`,
`unrealized_pnl_is_realized = false` et le latent n'affecte aucune métrique de trades fermés.
`marked_equity_at_end` additionne le latent uniquement dans le rapport informatif distinct.

Si la stratégie est déjà à plat, `unrealized_pnl_at_end = 0` et
`open_position_at_end = false`. L'évaluateur ne reçoit aucune barre future et refuse une marque
antérieure au fill d'entrée, un état partiel ou toute réalisation/fill caché.

Preuves locales : 23 nouveaux cas portent le fichier synthétique à 257 tests PASS. Ils couvrent
LONG/SHORT, gains/pertes latents, absence de fill et de trade fermé, invariance du réalisé, marque
au seul dernier Close, état à plat, causalité, immutabilité et déterminisme. Les 264 régressions
stratégie/replay ciblées et les 279 tests contrat/filiation/OOS passent. La suite complète passe
avec 6 169 tests et 6 warnings historiques en 77,56 s. Ruff ciblé, format Ruff, `py_compile` et
`git diff --check` passent.

`EMA_PULLBACK_V1_MNQ_END_OF_DATA_KEEP_OPEN_UNREALIZED = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = BLOCKED_HUMAN_GATE — FEES_AND_SLIPPAGE_MODEL_REQUIRED`.
Action humaine unique : définir le modèle initial exact de commission, spread et slippage pour un
aller-retour d'un MNQ, ainsi que l'unité et l'application à chaque fill, sans calibrage sur le PnL.

## EMA_PULLBACK_V1_MNQ — modèle de coûts V1 figé

La décision métier du 2026-09-27 fixe sans optimisation le modèle versionné
`EMA_PULLBACK_V1_MNQ_COSTS_2026_09_27`. Chaque fill simulé réel paie `0.51 USD` de commission et
reçoit exactement un tick MNQ de `0.25` point dans le sens défavorable. Le tarif est une hypothèse
de coût V1 datée, jamais une valeur remplaçable silencieusement. Sa référence publique est la page
[Apex Rithmic Commissions & Instruments](https://apextraderfunding.com/help-center/rithmic/rithmic-commissions-instruments/).

Le multiplicateur de contrat nécessaire à l'unité du PnL est la spécification CME de `2.00 USD`
par point MNQ, soit `0.50 USD` par tick ; référence :
[CME Micro E-mini Nasdaq-100](https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.html).
Cette spécification d'instrument n'est ni un paramètre de stratégie ni une optimisation.

Le prix bar-based causal reste enregistré comme `base_fill_price`. Le prix canonique de
comptabilité est ensuite : LONG entry `+1 tick`, SHORT entry `-1 tick`, LONG exit `-1 tick`, SHORT
exit `+1 tick`. Un stop normal part du stop structurel ; un gap-through part de l'Open observé.
Le spread est `ABSORBED_IN_FIXED_SLIPPAGE`, sans débit Bid/Ask séparé. Le PnL net utilise les prix
déjà slippés, convertis par le multiplicateur MNQ, puis retire seulement les commissions des fills.

Les entrées rejetées, signaux ignorés, ordres expirés et marques non réalisées de fin de flux ne
reçoivent ni commission ni slippage. Une position ouverte en fin de flux est marquée depuis son
entrée déjà slippée, mais la marque ne crée aucun nouveau coût. Prix hors grille, coût négatif,
slippage favorable, spread caché et second débit de slippage sont refusés fail-closed. Tous les
prix utilisent `Decimal` sur la grille de `0.25` ; les USD utilisent deux décimales `ROUND_HALF_UP`.

Preuves locales : 28 nouveaux cas portent le fichier synthétique à 285 tests PASS ; 292 régressions
stratégie/replay ciblées et 307 tests contrat/filiation/OOS passent. La suite complète passe avec
6 197 tests et 6 warnings historiques en 74,95 s. Ruff ciblé, format Ruff, `py_compile` et
`git diff --check` passent.

`EMA_PULLBACK_V1_MNQ_FEES_AND_SLIPPAGE_MODEL = PASS`.

`EMA_PULLBACK_V1_MNQ_FORMALIZATION = PASS`.

`EMA_PULLBACK_V1_MNQ_DEVELOPMENT_SCREENING_PROTOCOL = PASS`.

Le protocole préengagé canonique est
`docs/evidence/EMA_PULLBACK_V1_MNQ_DEVELOPMENT_PROTOCOL.json`, SHA-256
`13f3e1b71ce27a848a16a9598c37d76e9298a49331531fc7602118ec788c864f`. Il lie la baseline,
le modèle de coûts et le dataset propre
`mnq-06-26-minute-last-development-3bd8c078-v1` / `EXPOSED_DEVELOPMENT` avant toute lecture
de résultat. La PR #267 a fusionné ce préengagement avec CI verte avant l'unique replay.

Les seuils inclusifs sont : 100 trades clôturés, PnL net réalisé d'au moins `200.00 USD`,
profit factor net d'au moins `1.15`, drawdown mark-to-market d'au plus `750.00 USD` et au plus
8 pertes consécutives. Les trois tiers sont fixés par durée calendaire contiguë ; un trade clôturé
est attribué par timestamp de fill de sortie. Chaque tiers exige 15 clôtures, au moins deux tiers
strictement profitables, aucun profit factor inférieur à `0.80` et aucun PnL inférieur à
`-200.00 USD`. La convention projet sans perte est `+Infinity` si le numérateur est positif,
sinon zéro.

`GO_TO_INDEPENDENT_VALIDATION` reste un simple résultat de screening DEVELOPMENT : il ne valide
ni stratégie, ni rentabilité, ni paper trading, ni aptitude Apex. Après le premier replay, les
seuils sont immuables ; un échec est conservé et toute modification de stratégie devient une
nouvelle variante explicite. OOS reste fermé.

Preuves avant replay : 15 tests du protocole, 300 tests protocole + contrat EMA, 322 tests ciblés
avec filiation/OOS et suite complète de 6 212 tests PASS (6 warnings historiques). Ruff,
`py_compile`, validation JSON et `git diff --check` passent.

## Résultat du replay DEVELOPMENT préengagé

Le runner a été figé avant résultat au commit local
`e56f57f72f64f41dc84a5a6a0569b38cded60bf1`, module SHA-256
`26711662c3ea2d3df7e92dafe4cee3b972862eeefb642e6147123d5a912b3765`. Ses 14 tests,
336 tests ciblés et la suite complète de 6 226 tests passaient avant lecture du RAW. L'unique
replay effectif porte le run `ema-pullback-development-8bfe99a3f4beec32`. Une première commande
shell avait échoué avant import du module ; elle n'a ni lu le RAW ni appelé le runner.

Le RAW privé SHA-256 `3bd8c078d40143ccb1977562e47afadfd173f9c123e3a062ba28dbcb7721ba1a`
a été vérifié à 2 791 485 octets et 52 431 lignes, sans exposer de prix. Le replay a produit
1 372 trades clôturés, `4 138.56 USD` de PnL net réalisé et un profit factor net de
`1.166145174693789066734111356` : ces trois seuils passent. Il échoue sur le drawdown marqué
de `2 501.21 USD` (limite `750.00`) et 23 pertes consécutives (limite 8).

Les segments S1/S2/S3 contiennent respectivement 257/464/651 trades et des PnL nets de
`197.86`, `4 276.72` et `-336.02 USD`. Deux segments sont profitables et tous les profit factors
restent au-dessus de `0.80`, mais S3 franchit la limite de `-200.00 USD` ; stabilité `FAIL`.
Le verdict mécanique conservé est donc `NO_GO_BASELINE`.

Rapport assaini : `docs/evidence/EMA_PULLBACK_V1_MNQ_DEVELOPMENT_REPLAY_RESULT.json`, SHA-256
`4351d82e2b965b75843b0e24545358c80e2dc544a0549d085ceb8e93f4ceb3f6`. Il contient zéro prix,
zéro ligne RAW et confirme `oos_accessed = false`. Aucun seuil ne peut être modifié pour renverser
ce verdict ; l'OOS et l'étape indépendante restent fermés.

Gate historique : `EMA_PULLBACK_V1_MNQ_NO_GO_VARIANT_DECISION_REQUIRED`. Elle est acquittée par
l'autorisation explicite V1A ci-dessous ; le résultat de la baseline n'est ni modifié ni relabellisé.

## EMA_PULLBACK_V1A_MNQ — variante de pente préengagée avant replay

La décision humaine autorise exactement la variante
`EMA_PULLBACK_V1A_MNQ_EMA20_MIN_SLOPE_1_TICK`, avec l'unique hypothèse que le rejet des
conditions EMA20 presque plates pourrait réduire les whipsaws, les pertes groupées et le
drawdown. La baseline V1 et son verdict `NO_GO_BASELINE` restent immuables.

Le seul delta est le seuil inclusif de pente EMA20 : formule causale V1 inchangée sur `K = 3`,
LONG si pente `>= +0.25` point/bar et SHORT si pente `<= -0.25` point/bar, sans arrondi avant
comparaison. Le pullback `t-2`, MACD, les sorties, le stop, les absences de TP/breakeven/trailing,
le calendrier, la taille d'un MNQ, les coûts, l'exécution et la comptabilité de fin de données
restent inchangés.

Contrat préengagé : `docs/evidence/EMA_PULLBACK_V1A_MNQ_VARIANT_PROTOCOL.json`, SHA-256
`1dc90028d9de807a28218075c09b7d9b32d2eb8cc86b41a84814107a898f77df`. Il réutilise sans
assouplissement le protocole de screening SHA-256 `13f3e1b7...864f`, le même dataset
`EXPOSED_DEVELOPMENT`, et autorise au maximum un replay. Toute deuxième valeur de pente après
résultat exige une nouvelle décision humaine ; OOS et optimisation restent interdits.

Preuves locales pré-replay : 10 tests V1A, 39 tests variante/protocole/runner, 350 tests ciblés
stratégie/filiation/OOS et suite complète de 6 236 tests PASS avec 6 warnings historiques. Ruff,
format Ruff, `py_compile`, validation JSON, scan anti-fuite de données et `git diff --check` passent.
Le replay V1A n'a pas été lancé pendant ces validations.

La PR #269 a fusionné ce préengagement avec CI verte avant le replay : head
`ed3a751246e1cda03b99017d481acc4de4f9b1c1`, CI #220/run `36343021654` success, merge
`92e6a5d3de8dd8bd13c2014d52f6ba63a3209d5b`, arbre
`566cf2ebf82acbd55ea614f3ac920d673e82e1e7`.

`EMA_PULLBACK_V1A_MNQ_VARIANT_PROTOCOL = PASS`.

`EMA_PULLBACK_V1A_MNQ_DEVELOPMENT_REPLAY_EXECUTION = COMPLETED_ONCE`.

## Résultat du replay DEVELOPMENT V1A préengagé

L'unique replay autorisé est le run `ema-pullback-development-f76f2d17c5ea7ab8`, achevé le
2026-09-28 à 16:57:52 UTC. Il a utilisé le même RAW propre `EXPOSED_DEVELOPMENT`, le même modèle
de coûts et exactement le même protocole de screening que V1. Aucun OOS n'a été ouvert.

V1A réduit les signaux qualifiés de 1 471 à 1 119 et les trades clôturés de 1 372 à 1 049.
Le drawdown marqué baisse de `2 501.21` à `2 167.82 USD` et les pertes consécutives de 23 à 19,
mais ces valeurs enfreignent encore les limites `750.00 USD` et 8. Le PnL net reste positif à
`3 918.52 USD` et le profit factor progresse à `1.183757573483896381609799103`.

S1/S2/S3 contiennent 189/342/518 trades et produisent `-458.28` / `3 879.16` / `497.64 USD`.
Deux segments sont profitables et aucun profit factor ne descend sous `0.80`, mais S1 enfreint
le plancher de `-200.00 USD`. La stabilité segmentaire reste donc `FAIL`.

Le verdict mécanique est `NO_GO_VARIANT`. La baseline reste séparément et définitivement
`NO_GO_BASELINE`; aucun seuil n'est modifié et aucune pente supplémentaire n'est testée.

Rapport comparatif assaini :
`docs/evidence/EMA_PULLBACK_V1A_MNQ_DEVELOPMENT_REPLAY_RESULT.json`, SHA-256
`29eef4a574fc46aab07a5ab60fc0c09fe111c3e72acc6d91ae3e5f04450582de`. Il contient uniquement
des métriques agrégées, zéro prix, zéro ligne RAW et `oos_accessed = false`.

Validations post-résultat : 11 tests V1A, 40 tests variante/protocole/runner, 351 tests ciblés
stratégie/filiation/OOS et suite complète de 6 237 tests PASS avec 6 warnings historiques. Ruff,
format Ruff, validation JSON et `git diff --check` passent ; aucun test ne relance le RAW privé.

`BLOCKED_HUMAN_GATE — EMA_PULLBACK_V1A_MNQ_NO_GO_NEXT_EXPERIMENT_DECISION_REQUIRED`.
Cette gate historique a été levée le 2026-09-28 par l'autorisation explicite de l'unique enfant V1B
ci-dessous. V1 et V1A restent immuables avec leurs verdicts NO_GO respectifs.

## Préengagement V1B — entrées US RTH uniquement

L'unique nouvelle expérience autorisée est
`EMA_PULLBACK_V1B_MNQ_V1A_US_RTH_ENTRY_ONLY`, enfant de
`EMA_PULLBACK_V1A_MNQ_EMA20_MIN_SLOPE_1_TICK`. Son hypothèse unique est que la restriction des
nouvelles entrées à la fenêtre principale US réduit les entrées de faible liquidité/agitées, les
pertes groupées et le drawdown sans modifier les sorties existantes.

Le seul delta est un filtre des décisions d'entrée sur le timestamp UTC de la barre clôturée,
converti par IANA vers `America/Chicago` : lundi-vendredi, `08:30:00` inclus à `15:00:00` exclu.
Aucun offset UTC fixe n'est permis. Le stop structurel et la sortie EMA20 restent actifs hors
fenêtre, aucune fermeture n'est forcée à 15:00 et la politique de fin de données reste inchangée.

Contrat préengagé : `docs/evidence/EMA_PULLBACK_V1B_MNQ_VARIANT_PROTOCOL.json`, SHA-256
`c034db1ab2592f0ba4455c0aa0bd5c1c7bc2193f944d9f297819e38c35452f0e`. Module V1B SHA-256
`c61703033504539cda5067798c5b38832f406484e069228c9b6e3eb0533ee717` ; runner commun étendu
SHA-256 `a477d64e4d419aed40b29794f58714d463a8c0fe018b46e6e8004c0cb8dd6293`.

Les sources V1/V1A conservent respectivement leurs SHA-256 `af9d9159...cac9` et
`9f8b88f5...5f59`; leurs rapports restent `4351d82e...b3f6` et `29eef4a5...82de`.
Le protocole de screening `13f3e1b7...864f`, le dataset `EXPOSED_DEVELOPMENT`, les coûts et toutes
les autres règles sont réutilisés sans modification. Une seule exécution V1B est autorisée ; toute
autre fenêtre/session après résultat nécessite une nouvelle décision humaine.

Preuves locales pré-replay : 25 tests V1B, 65 tests variante/parent/runner, 369 tests ciblés
stratégie/filiation/OOS et suite complète de 6 262 tests PASS avec 6 warnings historiques. Ruff,
format Ruff, validation JSON et `git diff --check` passent. Le replay V1B n'a pas été lancé.

La PR #271 a fusionné ce préengagement avant tout replay : head
`8c060ce33a522ef9f2159ea19d69ba31b20607f3`, CI #224/run `36465463373` success, merge
`b7f185d5d0706a7b694c6499f904a218993b6208`, arbre
`a4c33fc2ebcdefe8fad7b97f039aeb4e937a4794`.

`EMA_PULLBACK_V1B_MNQ_VARIANT_PROTOCOL = PASS`.

`EMA_PULLBACK_V1B_MNQ_DEVELOPMENT_REPLAY_EXECUTION = COMPLETED_ONCE`.

## Résultat du replay DEVELOPMENT V1B préengagé

L'unique replay autorisé est le run `ema-pullback-development-3d2bde3b4e3fe085`, achevé le
2026-09-28 à 18:33:06 UTC sur le même RAW propre `EXPOSED_DEVELOPMENT`. Aucun OOS, aucune autre
fenêtre de session et aucun changement des seuils n'ont été utilisés.

Sur les 1 119 signaux qui satisfaisaient V1A, V1B en admet 339 et en rejette 780 par le filtre
d'entrée. Il clôture 325 trades : PnL net `3 493.00 USD`, profit factor
`1.371813295013039544414284954`, drawdown marqué `1 954.87 USD` et 16 pertes consécutives.
Le drawdown et la série de pertes enfreignent toujours les plafonds `750.00 USD` et 8.

S1/S2/S3 contiennent 50/110/165 trades, avec PnL `488.00` / `3 530.80` / `-525.80 USD` et
profit factor `1.506960315811344275919384999` / `2.214192865052236290982619999` /
`0.9048146619454159697028943005`. Deux segments sont profitables, mais S3 enfreint le plancher
de `-200.00 USD`; la stabilité segmentaire reste `FAIL`.

Le verdict mécanique est `NO_GO_VARIANT`. V1 reste `NO_GO_BASELINE` et V1A reste
`NO_GO_VARIANT`; aucune des trois définitions n'est modifiée.

Rapport comparatif assaini :
`docs/evidence/EMA_PULLBACK_V1B_MNQ_DEVELOPMENT_REPLAY_RESULT.json`, SHA-256
`d3b188c8efed50fc418dab25941b9237261bf39cb88a259c371d7e65e4a0e41b`. Il contient uniquement
des métriques agrégées, zéro prix, zéro ligne RAW et `oos_accessed = false`.

Validations post-résultat : 26 tests V1B, 370 tests ciblés stratégie/filiation/OOS et suite complète
de 6 263 tests PASS avec 6 warnings historiques. Aucun test ne relance le RAW privé.

`BLOCKED_HUMAN_GATE — EMA_PULLBACK_V1B_MNQ_NO_GO_NEXT_EXPERIMENT_DECISION_REQUIRED`.
Action humaine unique : arrêter cette piste ou autoriser une nouvelle expérience explicitement
nommée avec exactement une hypothèse préengagée ; aucune autre session n'est autorisée implicitement.

## Préengagement — réplication V1B sur MNQ 03-26

La gate précédente est levée uniquement pour
`EMA_PULLBACK_V1B_MNQ_CROSS_CONTRACT_REPLICATION_03_26`. Il s'agit d'une réplication de V1B sans
aucun changement de stratégie et non d'une V1C. V1, V1A et V1B restent immuables avec leurs verdicts
`NO_GO_BASELINE`, `NO_GO_VARIANT` et `NO_GO_VARIANT`.

Le protocole est figé dans
`docs/evidence/EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_PROTOCOL.json`, SHA-256
`c431c991c290f000bfdd9f39f01372ccfc05c963911e11534184d1ab95b07d37`. Il lie bit-for-bit la
réplication au module V1B SHA-256 `c6170303...717`, au protocole V1B `c034db1a...f0e` et au
screening original `13f3e1b7...864f`.

La fenêtre a été préengagée avant toute lecture de performance : export NinjaTrader du contrat exact
`MNQ 03-26`, dates demandées `2026-01-01` à `2026-03-31` incluses, puis utilisation de toutes les
barres valides réellement exportées dans leur ordre source. Aucun découpage fondé sur le PnL ni
aucun changement ultérieur de fenêtre n'est permis. Les timestamps sont UTC fin de barre ; le
calendrier `CME US Index Futures ETH` et les règles DST `America/Chicago` doivent être attestés.

Le contrat source exige `MNQ 03-26 / Minute / Last / DoNotMerge`, contrat non continu, chaîne
`Apex Trader Funding -> Rithmic -> NinjaTrader`, rôle `EXPOSED_DEVELOPMENT_REPLICATION`, hash,
taille, nombre de lignes, reçu d'export, version NinjaTrader, fuseaux, sémantique temporelle,
calendrier, jours fériés/early closes, transformation et parent. L'archive historique
`MNQ_OHLCV_2024_2025_03-26_SANS_09-26(1).zip` est explicitement interdite car sa filiation est
ambiguë et elle ne constitue pas le nouvel export propre autorisé.

Le mapping préengagé du résultat est fail-closed : échantillon insuffisant conserve
`INSUFFICIENT_SAMPLE`; un échantillon suffisant qui échoue le PnL `200.00 USD` ou le profit factor
`1.15` déclenche `STOP_INCREMENTAL_EMA_PULLBACK_V1_PATH`; si ces deux seuils passent mais qu'un
critère de risque ou de stabilité échoue, le statut devient `MIXED_DEVELOPMENT_EVIDENCE`. Même si
tous les critères passent, l'OOS ne s'ouvre pas automatiquement et une gate humaine reste requise.

Vérification locale du protocole : 31 tests protocole/V1B PASS, 380 tests ciblés
stratégie/filiation/confidentialité PASS et suite complète de 6 268 tests sans échec. Ruff, format,
`py_compile`, JSON et `git diff --check` passent. Aucun RAW MNQ 03-26 n'a été trouvé ou lu, aucune
ligne de marché n'a été publiée et le compteur de replay reste zéro.

La nouvelle racine privée `MNQ 03-26.Last.txt` a été vérifiée indépendamment : SHA-256
`2122722f25dbc865dad154905309b5e76d2190561ffc64acdaa955365ccb9efc`, 3 946 060 octets,
74 308 lignes, première estampille `2026-01-01T01:22:00Z` et dernière estampille
`2026-03-20T13:30:00Z`. La fin au 20 mars correspond à l'expiration du contrat trimestriel et ne
constitue pas une sélection postérieure fondée sur le PnL.

L'attestation finale `FINAL_OPERATOR_ATTESTATION.txt` a été contrôlée octet par octet : 1 844 octets
et SHA-256 `081386347dcf52ba6eff9b66143b9e217881f11f2cd0a9ab0c4439c7df7c65d7`. Elle lie ce RAW exact à
`MNQ 03-26 / Minute / Last / DoNotMerge`, au contrat non continu, au template intégré
`CME US Index Futures ETH` non modifié, à la chaîne Apex Trader Funding -> Rithmic -> NinjaTrader,
aux timestamps UTC de fin de barre, et déclare `NONE` pour transformation, parent et relation avec
l'archive legacy. Elle reste explicitement rétrospective.

Les captures contemporaines d'export, les captures historiques/pré-export, les observations NTFS
post-export et la documentation NinjaTrader conservent chacune leur classe. Leur combinaison est
acceptée par le contrat fail-closed pour cette racine `EXPOSED_DEVELOPMENT_REPLICATION` uniquement.
La lignée canonique et la matrice de preuves assainie vivent dans
`docs/evidence/MNQ_03-26_CLEAN_LINEAGE/`; aucun RAW, prix, identifiant de compte ou capture n'est
versionné. `EMA_PULLBACK_V1B_MNQ_03_26_CLEAN_LINEAGE = PASS`.

La lignée a été intégrée par PR #274 : head
`69a5fecf431ab064b2aa146e753cbfcfae4ac52d`, CI `AGIcore CI #230` verte, merge
`42efdaa5147879f67c322c81203f69e69f7ea41c`.

Le chargeur privé de réplication refuse toute divergence de SHA-256, taille, nombre de lignes ou
bornes temporelles avant d'appeler le moteur. Son module a le SHA-256
`d45bfdc4235f41e812d4ccfe8885c00104130e3d85f350dc878971b84d42a22c`. Le moteur de screening et
le runner partagé acceptent désormais l'identité et le rôle gouverné de réplication sans modifier
les seuils. Leurs SHA-256 sont respectivement `a7d48786...16456` et `b008b42b...b4f9`.

V1, V1A et V1B restent bit-for-bit inchangées : `af9d9159...ac9`, `9f8b88f5...f59` et
`c6170303...717`. Le chargeur réutilise directement la pente V1A, le filtre de session V1B et le
moteur déterministe commun ; aucun paramètre de stratégie n'est redéfini. Les 85 tests ciblés
passent avec des données synthétiques et le RAW privé n'est jamais ouvert par les tests. La suite
locale complète passe : 6 282 tests, 6 avertissements préexistants ; Ruff ciblé, format Ruff,
`py_compile` et `git diff --check` passent également.

Le chargeur a été intégré par PR #275 : head
`b4294d262e41d4edb1c4c56c205f18a36a2a7986`, CI `AGIcore CI #232` verte, merge
`f616033f9dce74a4a0ca567de9c749840daf172f`.

L'unique replay préengagé a été exécuté le 2026-10-01 à 18:49:04 UTC sur le RAW privé vérifié
`2122722f...9efc`. Il a produit 478 signaux qualifiés, 457 trades clôturés, un PnL net de
`-4758.64 USD`, un profit factor de `0.6444307622415035014152113552`, un drawdown maximal de
`4998.09 USD` et 14 pertes consécutives. Les trois segments sont nets négatifs. Aucun OOS n'a été
ouvert, aucun prix ni détail de trade n'est publié et aucune règle ou seuil n'a été modifié.

Le résultat agrégé est figé dans
`docs/evidence/EMA_PULLBACK_V1B_MNQ_03_26_REPLICATION_RESULT.json`, SHA-256
`968f934c46969c3978575aa96b7e98f015958c731c6ed73a543ebe3a9b8372b6`. L'échec matériel de
réplication impose l'issue préengagée `STOP_INCREMENTAL_EMA_PULLBACK_V1_PATH`. Aucune V1C et aucune
ouverture OOS ne sont autorisées. La prochaine action exige une décision humaine sur l'arrêt de
cette voie incrémentale. Les 20 tests ciblés de lignée, runner et résultat passent ; la suite locale
complète passe avec 6 288 tests et 6 avertissements préexistants.

## Décision humaine — V1 terminée, V2 en préformalisation

Le 2026-10-03, le propriétaire a décidé `EMA_PULLBACK_V1_PATH = TERMINATED` et figé
définitivement V1 `NO_GO_BASELINE`, V1A `NO_GO_VARIANT`, V1B `NO_GO_VARIANT`.
La réplication V1B MNQ 03-26 et ses métriques historiques restent inchangées.
Aucune V1C n'est autorisée.
L'ancienne gate `EMA_PULLBACK_V1_PATH_TERMINATION_DECISION_REQUIRED` est acquittée
par cette décision ; elle reste une trace historique et ne constitue plus l'arrêt actif.

Le nouveau programme `EMA_PULLBACK_V2_REGIME_GATED` est `PRE_FORMALIZATION` ; sa charte est
`docs/evidence/EMA_PULLBACK_V2_REGIME_GATED_PRE_FORMALIZATION.md`, SHA-256
`71078853b781a8156bc77ef26a7488840d52f49b602e024f8058eb59bb6a07f5`. L'hypothèse porte sur une
transition de régime ou une impulsion directionnelle précédant le pullback EMA.
Seule l'infrastructure validée est réutilisable ; les règles d'entrée V1 ne sont
pas héritées. Le contrat `REGIME_CONTEXT_V2` devra définir événement impulsion/
retournement, transition momentum et acceptation de tendance, puis prédicats,
warmup, ordre, invalidation, durée de vie, politique de position, sorties et risque.

La première ambiguïté structurante était la composition des événements qualifiants :
impulsion seule, retournement seul, ou deux prédicats distincts. La gate historique
`REGIME_CONTEXT_V2_EVENT_COMPOSITION_REQUIRED` a été acquittée le 2026-10-03.
La charte initiale a été intégrée par PR #277, head
`582e8a9661e72da21e94b7096d303057c66ace91`, CI #236 verte, merge
`f67eaed1d8e3608146f8e81d7c0db45721d6e31d`.
Pas de replay, de sélection de seuil sur les résultats V1, de réutilisation des
contrats MNQ 06-26 ou MNQ 03-26 pour calibrer V2, ni d'ouverture OOS. Un nouveau
dataset DEVELOPMENT avec filiation sera requis après formalisation.

## V2 — composition de deux événements indépendants

Décision humaine du 2026-10-03 :
`REGIME_CONTEXT_V2_EVENT_COMPOSITION = IMPULSE_OR_REVERSAL_DISTINCT`.
`DIRECTIONAL_IMPULSE_EVENT` et `REVERSAL_TRANSITION_EVENT` portent chacun un type,
une direction LONG/SHORT, l'index et l'estampille UTC de leur barre clôturée. Un seul
événement qualifie le contexte ; deux événements de même direction le qualifient
en conservant leurs deux étiquettes ; deux directions opposées donnent
`AMBIGUOUS`, sans qualification et sans entrée. Aucune priorité ni score générique.

Lors de la formalisation initiale, le compositeur pur
`src/agicore/trading/regime_context_v2.py`, SHA-256
`f871ffe4f4cc8bca3a55ca8e558d5ded56d0acc0a182e2628c0f8302cdb5629f`,
vérifie fermeture et métadonnées de même barre avant la composition. Il n'est
raccordé ni aux détecteurs, ni à l'entrée, ni au replay ; leurs prédicats ne sont
pas encore définis. La gate suivante était
`DIRECTIONAL_IMPULSE_EVENT_EMERGING_DIRECTION_REQUIRED` : définir causalement
la direction déjà émergente à partir des barres clôturées. Elle a été acquittée
par la décision du propriétaire du 2026-10-03.
Aucun seuil numérique de magnitude, nouveau dataset ou résultat de performance V2 n'a été fixé.
Tests locaux : 24 tests synthétiques de composition PASS ; 6308 tests PASS avec
`tests/unit/test_mcp.py` exclu. La suite intégrale dans ce sandbox reste non
concluante : le test préexistant `test_root_endpoint` de FastAPI `TestClient`
se bloque même isolé (timeout 30 s). Ruff ciblé, `py_compile` et
`git diff --check` PASS. PR #278 fusionnée après CI #238 verte (suite intégrale
et contrôle des espaces) ; merge `04b0ef527da196af01bf7f3f0dad6b86aa9ff34e`.
Aucune réussite intégrale locale n'est revendiquée.

## V2 — direction émergente structurelle avant l'impulsion

Décision humaine du 2026-10-03 : sur `t-3`, `t-2`, `t-1` clôturées, LONG exige
trois closes strictement croissants et trois lows non décroissants ; SHORT exige
trois closes strictement décroissants et trois highs non croissants. La direction
est connue à `Close[t-1]`. Clôtures égales rejetées ; égalité des lows LONG ou
highs SHORT autorisée. Manque d'une bougie : `INSUFFICIENT_WARMUP`, direction
`NONE`. Incohérence ou barre préalable non clôturée : rejet fail-closed. La
bougie candidate `t` et les barres futures ne sont jamais lues.

Le prédicat pur `src/agicore/trading/directional_impulse_v2.py`, SHA-256
`7cd03b0385a409478134d6855d3f4bf51aef589b91657e753b878029858f95f8`,
contient les quatre sous-prédicats et leur assemblage événementiel, décrits ci-dessous.
La gate suivante était `DIRECTIONAL_IMPULSE_EVENT_RANGE_PREDICATE_REQUIRED` ;
elle a été acquittée par décision du propriétaire du 2026-10-03.
Tests locaux : 29 nouveaux tests synthétiques PASS ; 53 tests V2 ciblés PASS ;
6337 tests PASS hors `tests/unit/test_mcp.py` (son `TestClient` se bloque dans
ce sandbox, comme pour PR #278). Ruff ciblé, `py_compile` et diff-check PASS.
PR #279 fusionnée après CI #240 verte (suite intégrale et contrôle des espaces) ;
merge `3e0f9bed0405964dd81ac90658b2fd5f1aae3948`.

## V2 — range de l'impulsion sur 20 bougies précédentes

Décision humaine du 2026-10-03 : `RANGE_MEASURE = HIGH_LOW`, référence médiane
exacte des ranges de `t-20` à `t-1`, multiplicateur `Decimal("1.50")`.
`range_t >= 1.50 * median(prior_20_ranges)` qualifie le range, avec égalité
admise et sans arrondi préalable. `t` doit être clôturée ; manque d'une des 20
bougies clôturées : `INSUFFICIENT_WARMUP`, qualification fausse ; médiane <= 0 :
`INVALID_REFERENCE_RANGE`, qualification fausse. Une fenêtre de 20 prend la
moyenne exacte de ses deux valeurs centrales. Le calcul n'est pas directionnel,
ne lit aucune barre future et n'intègre jamais `t` à sa référence.

Le même module `src/agicore/trading/directional_impulse_v2.py`, SHA-256
`7cd03b0385a409478134d6855d3f4bf51aef589b91657e753b878029858f95f8`,
ne produisait à cette étape historique aucun événement d'impulsion ou signal.
Le seuil 1.50 a été choisi avant replay, sans résultat V1/V1A/V1B et sans optimisation. La gate
suivante était `DIRECTIONAL_IMPULSE_EVENT_VOLUME_PREDICATE_REQUIRED` ; elle a été
acquittée par décision du propriétaire du 2026-10-03. Mèches/corps et autres
composantes restent ouverts.
Aucun replay, nouvelle sélection de données ni ouverture OOS.
Tests locaux : 19 tests synthétiques de range PASS ; 72 tests V2 ciblés PASS ;
6356 tests PASS hors `tests/unit/test_mcp.py`, bloqué dans ce sandbox lors des
tranches précédentes. Ruff ciblé, `py_compile` et diff-check PASS.
PR #280 fusionnée après CI #242 verte (suite intégrale et contrôle des espaces) ;
merge `064b8b2e0943eb87133bb7989ec4d4dba47a72ad`.

## V2 — volume de l'impulsion sur 20 bougies précédentes

Décision humaine du 2026-10-03 : `VOLUME_MEASURE = BAR_TRADE_VOLUME`, référence
médiane exacte des volumes de transactions des 20 bougies clôturées précédentes,
multiplicateur `Decimal("1.50")`. `Volume[t] >= 1.50 * median(Volume[t-20 ... t-1])`
qualifie le volume, égalité incluse et sans arrondi préalable. La médiane est
la moyenne exacte des valeurs centrales 10 et 11 triées. Le volume est uniquement
celui de barres Last d'une minute ; Bid/Ask, delta, tick count et carnet refusés.
La direction reste exclusivement celle du prérequis émergent, indépendante du volume.

Candidate `t` clôturée obligatoire ; moins de 20 antérieures clôturées :
`INSUFFICIENT_WARMUP` ; volume candidat absent/invalide :
`INVALID_CANDIDATE_VOLUME` ; référence absente/invalide ou médiane <= 0 :
`INVALID_REFERENCE_VOLUME` ; tout volume sélectionné négatif : `INVALID_VOLUME`.
Tous ces statuts donnent `volume_qualified = false`. Le warmup est vérifié
d'abord, puis les négatifs, le défaut candidat et le défaut de référence.
Index/timestamps ou type de volume incohérents sont refusés. Aucun accès
à `t+1`, à une barre plus ancienne que `t-20` ou aux prix par ce sous-prédicat.

Le module pur `src/agicore/trading/directional_impulse_v2.py`, SHA-256
`7cd03b0385a409478134d6855d3f4bf51aef589b91657e753b878029858f95f8`,
expose ce calcul avec un résultat immutable. Les mentions Last/Minute/volume
de transactions sont des contraintes d'entrée et ne remplacent pas les preuves
de filiation d'un nouveau dataset. À cette étape historique aucun événement
n'était émis ; l'assemblage ci-dessous émet seulement un événement de contexte.
Le seuil 1.50 est non optimisé, choisi avant replay ;
aucun résultat V1 ni les contrats MNQ 03-26/06-26 n'est utilisé pour le choisir.

Tests synthétiques : 45 tests de volume PASS ; 117 tests V2 ciblés PASS.
Fichier `tests/unit/trading/test_directional_impulse_volume_v2.py`, SHA-256
`b3af140e9d292e1126c088cf2a368b9048e1dca98e1a219f4d9ed2c7d978cb14`.
Suite locale : 6401 tests PASS, 4 avertissements préexistants, 74.89 s, hors
`tests/unit/test_mcp.py` dont le `TestClient` est bloqué dans ce sandbox lors des
tranches précédentes. Aucune réussite intégrale locale n'est revendiquée.
Ruff ciblé, format Ruff, `py_compile` et diff-check PASS. La fusion exige une
suite intégrale CI verte sur le commit exact ; la PR conserve cette preuve et
le SHA de merge. Les autorisations Git permanentes du propriétaire s'appliquent.

La gate corps/mèches a été acquittée par la décision du propriétaire ci-dessous.
PR #281 fusionnée après CI #244 verte ; merge
`03931edbb2717b8f65a6a1af46680c11bb0416be`.

## V2 — corps et mèches de l'impulsion

Décision humaine du 2026-10-03 : corps >= Decimal("0.60") * range et mèche
terminale <= Decimal("0.20") * range. LONG exige corps haussier et contrôle la
mèche supérieure ; SHORT exige corps baissier et contrôle la mèche inférieure.
Direction exclusivement émergente, aucune limite sur la mèche opposée.
Égalités admises, doji refusé, comparaisons exactes sans arrondi. OHLC malformé
ou non fini : INVALID_OHLC ; range nul après validation : INVALID_CANDIDATE_RANGE.
Qualification fausse pour ces statuts. Candidate clôturée seulement, aucun accès
aux barres antérieures ou futures par ce sous-prédicat.

46 tests synthétiques corps/mèches PASS ; 163 tests V2 ciblés PASS.
6447 tests locaux PASS, 4 avertissements préexistants, hors test_mcp.py bloqué
dans ce sandbox. Ruff, format, compilation et diff-check PASS ; la fusion
exige la CI intégrale verte, dont la PR conserve le résultat et le SHA de merge.
Le composant autonome n’émet aucun événement ou signal. L’assemblage ci-dessous réalise la suite
explicitement autorisée après fusion, sans replay ni nouveau seuil.

## V2 — assemblage déterministe de l'impulsion

PR #282 fusionnée après CI #246 verte, merge
`3997b75d6451b6e030c4f38cb428938da0211fb0`.
Décision explicite du propriétaire : conjonction stricte des quatre composants
figés. L'évaluateur appelle les fonctions existantes sans modification, sur les
mêmes observations OHLC/volume Last/Minute. Direction uniquement sur t-3..t-1,
range/volume sur la candidate et les 20 antérieures, corps/mèches sur t.
Les observations plus anciennes et futures ne sont jamais lues. Les seuils
1.50/1.50/0.60/0.20 restent des baselines pré-replay non optimisées.

Qualification complète seulement : événement immutable de type
DIRECTIONAL_IMPULSE_EVENT, direction émergente LONG/SHORT, index t et timestamp
UTC de t clôturée. Un échec, warmup incomplet ou donnée invalide n'émet aucun
événement. OHLC candidat invalide ou range nul : statut corps/mèches conservé,
range/volume non évalués. Les autres incohérences restent fail-closed.
Le compositeur existant garde les collisions distinctes, sans priorité nouvelle.

41 tests synthétiques d'assemblage PASS ; 204 tests V2 ciblés PASS.
6488 tests locaux PASS, 4 avertissements préexistants, hors test_mcp.py bloqué
dans ce sandbox. Ruff, format, compilation et diff-check PASS. CI intégrale
verte requise avant fusion ; preuves et SHA de merge dans PR.
Aucune entrée, mesure de performance, durée du contexte, replay, OOS ou donnée
réelle. REVERSAL_TRANSITION_EVENT demeure PRE_FORMALIZATION.

La gate direction préalable est acquittée par la décision ci-dessous.

## V2 — direction préalable distincte au retournement

PR #283 fusionnée après CI #248 verte, merge
`e850cc8658d6112a494a566c3fe73c2506dce7e9`.
Décision du propriétaire du 2026-10-03 : cinq bougies clôturées t-5..t-1,
quatre différences de Close exactes, UP si extrémité strictement supérieure
et au moins trois pas positifs ; DOWN si extrémité strictement inférieure et
au moins trois pas négatifs ; sinon NONE. Les flats ne comptent dans aucun
sens. UP rend seulement SHORT éligible ; DOWN rend seulement LONG éligible ;
NONE interdit tout événement de retournement. Le côté éligible n'est pas un
événement complet. Aucun seuil optimisé ni résultat V1 utilisé.

Warmup incomplet ou bougie antérieure non clôturée : INSUFFICIENT_WARMUP,
direction NONE ; Close manquante/non finie : INVALID_PRIOR_DIRECTION_INPUT,
direction NONE. L'historique clôturé est vérifié avant les prix. Métadonnées
incohérentes refusées fail-closed. Seules les cinq Close sont utilisées, la
candidate t et les observations futures/plus anciennes ne sont jamais lues.
Disponible à Close[t-1] seulement sur évaluation valide. Aucune importation ou
modification du détecteur d'impulsion, aucune EMA/MACD/RSI/volume/range/mèche/ATR.

Module distinct lors de la formalisation de la direction préalable :
src/agicore/trading/reversal_transition_v2.py, SHA-256
`689b271c9b0395d18eda779e727b856d296c8bb76b73dd5fa46cdc6235332691`.
Tests synthétiques : 84 nouveaux tests PASS ; 288 tests V2 ciblés PASS.
Fichier tests/unit/trading/test_reversal_prior_direction_v2.py, SHA-256
`6eae5e5d700d0fbf67c93e78624cb6ab9e789c7eb60e71d47ff41b717e3435a0`.
6572 tests locaux PASS, 4 avertissements préexistants, hors test_mcp.py bloqué
dans ce sandbox. Ruff, format, compilation et diff-check PASS. CI intégrale
verte exigée avant fusion ; preuves et SHA de merge conservés dans la PR.
Aucun replay ou accès OOS.

La gate bougie de rejet est acquittée par la décision ci-dessous.

## V2 — bougie de rejet indépendante de sa couleur

PR #284 fusionnée après CI #250 verte, merge
`7ac936d780c17ef431a1539990516393ff7e25c0`.
Décision du propriétaire du 2026-10-03 : réutiliser les cinq bougies clôturées
t-5..t-1 de la direction préalable pour prior_high/prior_low. Candidate t
clôturée. MIN_REJECTION_WICK_RATIO = Decimal("0.40"), baseline pré-replay
non optimisée, sans dérivation V1/V1A/V1B ni ajustement après résultats.

UP => SHORT seulement si High[t] > prior_high, Close[t] < prior_high et
upper_wick >= 0.40 * range. DOWN => LONG seulement si Low[t] < prior_low,
Close[t] > prior_low et lower_wick >= 0.40 * range. Balayage et retour stricts,
mèche inclusive à exactement 40%. Toute différence infinitésimale sous 40%
échoue. Aucune couleur de corps requise, doji admissible si les conditions
qualifient ; aucune borne de Close sur l'extrême opposé. Symétrie LONG/SHORT.

OHLC candidat incohérent, manquant ou non fini : INVALID_OHLC. Range nul après
validation : INVALID_CANDIDATE_RANGE. Statuts de la direction préalable
propagés ; High/Low historiques manquants, non finis ou inversés :
INVALID_PRIOR_EXTREMA. Tous non qualifiés. Candidate absente/non clôturée ou
métadonnées incohérentes : erreur fail-closed. Open historique non requis.
Calcul exact Decimal sans arrondi préalable, même sous précision réduite.

La fonction de direction préalable figée est réutilisée sans modification.
Elle reste connue à Close[t-1] ; le rejet est connu seulement à Close[t].
La candidate n'entre pas dans les références. Aucune observation plus ancienne
que t-5 ou future n'est lue. Aucun MACD/EMA20/volume/ATR/RSI/stochastic/sens du
corps/confirmation t+1 ajouté. Aucun événement complet ni signal d'entrée.

Module lors de la formalisation du rejet :
src/agicore/trading/reversal_transition_v2.py, SHA-256
`6efd4241a2f8a63925e5c9f6e6fdec2197fe6fbf8d4d3026acdc74d4da7e9fdc`.
Tests synthétiques : 114 nouveaux tests PASS ; 402 tests V2 ciblés PASS.
Fichier tests/unit/trading/test_reversal_rejection_bar_v2.py, SHA-256
`cb9877970a575f4af1b5a8424456a39112459c0136f04324d8b38dd19a81d0db`.
6686 tests locaux PASS, 4 avertissements préexistants, hors test_mcp.py bloqué
dans ce sandbox. Ruff, format, compilation et diff-check PASS.
CI intégrale verte exigée avant fusion ; preuves et SHA de merge conservés
dans la PR. Aucun replay, accès OOS, dataset réel ou ajustement MNQ 03-26/06-26.

La gate transition opposée est acquittée par la décision ci-dessous.

## V2 — transition opposée strictement sur t+1

PR #285 fusionnée après CI #252 verte, merge
`31539cdb8b25ed0672d14fe4469fab84068ec112`.
Décision du propriétaire du 2026-10-03 : confirmation sur exactement une
bougie clôturée t+1. SHORT après UP/rejet SHORT : Close[t+1] < Open[t+1] et
Close[t+1] < min(Open[t], Close[t]). LONG après DOWN/rejet LONG : miroir strict,
Close[t+1] > Open[t+1] et Close[t+1] > max(Open[t], Close[t]). Doji et égalité
à la borne échouent. Aucun seuil de range/volume ni cassure Low/High de t.

À Close[t] : rejet qualifié, transition fausse, AWAITING_OPPOSITE_TRANSITION,
sans lecture t+1 même présent dans une source historique. Horloge clôturée
explicite. Fin de données à t signalée par end_of_data=True :
INCOMPLETE_CONFIRMATION. Confirmation absente/non clôturée : même statut.
Close/Open t+1 invalides : INVALID_CONFIRMATION_INPUT. Rejet non qualifié :
statuts imbriqués conservés, t+1 non lu. Métadonnées incohérentes refusées.

Échec sur t+1 clôturée : EXPIRED_NO_TRANSITION ; t+2 ne peut jamais sauver t.
Confirmation valide : CONFIRMED, connue seulement à Close[t+1]. Réévaluation
ultérieure conserve l'index et le timestamp t+1. Références t-5..t-1 et rejet
t réutilisés sans modification. Open/Close t+1 seulement ; aucun indicateur.
Baseline pré-replay non optimisée, sans dérivation V1/V1A/V1B ni ajustement MNQ.

Module lors de la formalisation de la transition opposée :
src/agicore/trading/reversal_transition_v2.py, SHA-256
`9581d9b7d47aef0385f8008a9e219135f3945fd5fe509d00b8cea3db6c843676`.
73 nouveaux tests synthétiques PASS ; 475 tests V2 ciblés PASS.
Fichier tests/unit/trading/test_reversal_opposite_transition_v2.py, SHA-256
`5d39d91b02d1685445559ac8f7864aa14cc7d123ed7b99c95055257879c4632b`.
6759 tests locaux PASS, 4 avertissements préexistants, hors test_mcp.py bloqué
dans ce sandbox. Ruff, format, compilation et diff-check PASS.
CI intégrale verte exigée avant fusion ; preuves et SHA de merge dans la PR.
Aucun replay, accès OOS, dataset réel ou changement de règles V1/risque.

L'assemblage demandé après fusion est réalisé dans la phase ci-dessous.

## V2 — événement de retournement complet à t+1

PR #286 fusionnée après CI #254 verte, merge
`39130e82152002c3c11c7c316f65d8fbcc7fc9d5`.
Assemblage explicitement autorisé : direction préalable qualifiée AND rejet
qualifié AND transition opposée confirmée. Les trois fonctions figées sont
réutilisées sans changement sur les mêmes observations. Aucun composant,
seuil ou règle de marché supplémentaire. Toute qualification incomplète,
invalide, expirée ou en attente donne zéro événement complet.

Source immutable : event_type = REVERSAL_TRANSITION, direction LONG/SHORT
opposée à prior_direction UP/DOWN, rejection_bar_index t et event_bar_index
t+1, rejection_timestamp et event_timestamp UTC séparés. L'événement n'existe
qu'à Close[t+1]. Une réévaluation ultérieure conserve cette disponibilité.
Seuls t-5..t et t+1 autorisée par l'horloge sont lus, jamais t+2/future.

L'adaptateur as_regime_event() conserve direction/index/timestamp de l'événement
dans la famille existante REVERSAL_TRANSITION_EVENT du compositeur inchangé.
Le record source conserve type REVERSAL_TRANSITION et provenance du rejet.
L'OR des deux familles et la collision opposée restent figés ; aucun ancien
événement n'est retimestampé sur une barre ultérieure pour rester actif.

Module src/agicore/trading/reversal_transition_v2.py, SHA-256
`72d11ae348470bcb4a56b89473848524ab4ca23f670e532a557424d3e89d5a28`.
47 nouveaux tests synthétiques d'assemblage PASS ; 522 tests V2 ciblés PASS.
Fichier tests/unit/trading/test_reversal_transition_event_v2.py, SHA-256
`bef2a0ba02a158f06e85246140c6a6c7d6f76e62ea510019a41c60dc6d61875c`.
6806 tests locaux PASS, 4 avertissements préexistants, hors test_mcp.py bloqué
dans ce sandbox. Ruff, format, compilation et diff-check PASS.
CI intégrale verte exigée avant fusion ; preuves et SHA de merge dans la PR.
Aucun replay, accès OOS, lecture de dataset, calibration MNQ ou changement V1/risque.

La gate durée de vie est acquittée par la décision ci-dessous.

## V2 — contexte borné et consommation unique

PR #287 fusionnée après CI #256 verte, merge
`677b5dd2d0ac49aec406fa006a6d487ee593ae3c`.
Décision du propriétaire du 2026-10-03 : MAX_CONTEXT_AGE_CLOSED_BARS = 8,
MAX_CONTEXT_ELAPSED_TIME = 8 minutes, CONTEXT_REUSE = ONE_SHOT,
SAME_DIRECTION_REFRESH = DISABLED. Baselines initiales pré-replay non optimisées,
fixées avant performance V2 ; aucun ajustement sur MNQ 03-26/06-26 ou V1.

Source complète sur e : contexte ACTIVE après Close[e], pullbacks possibles
sur e+1..e+8 inclusivement, jamais sur e. Le timestamp doit rester à <=8 minutes
du timestamp source. Temps >8 minutes expire avant tout pullback, y compris
après une interruption de données/session. Âge >8 expire avant évaluation ;
e+8 sans qualification expire seulement après sa dernière opportunité.
Si temps et âge sont dépassés simultanément, EXPIRED_ELAPSED_TIME prévaut.

Ordre figé par bougie clôturée : expiration, composition des événements
courants, invalidation AMBIGUOUS/opposée, conservation même direction sans
rafraîchissement, puis seulement évaluation formelle d'un pullback éligible.
Opposé : ancien record INVALIDATED_OPPOSITE_EVENT, nouveau contexte de k,
premier pullback k+1. AMBIGUOUS : INVALIDATED_AMBIGUOUS_EVENT sans remplacement.
Même direction ACTIVE : source/âge/étiquettes conservés, pas de pile, notice
SAME_DIRECTION_EVENT_IGNORED_NO_REFRESH. L'invalidation gagne sur le pullback
potentiel de l'ancien contexte sur la même bougie. Les records retirés sont
rendus pour audit, sans mutation des snapshots précédents.

Seul EMA20_PULLBACK_QUALIFIED=true consomme le contexte. Touche/proximité brute
ne suffit pas. Record CONSUMED conserve source_event_types/direction/index/
timestamp et pullback_bar_index/timestamp. Aucun second pullback ni réactivation
après échec de confirmation/entrée ; un nouvel événement crée une nouvelle
source. Les deux familles d'événements et les doubles étiquettes sont admises ;
pour REVERSAL, e correspond à la confirmation t+1 du détecteur figé.

Fin des données : ACTIVE => EXPIRED_END_OF_DATA, sans bougie/pullback/entrée
synthétique. Finaliseur au dernier index/timestamp connu ; aucun état terminal
n'est rouvert. Une série terminée refuse de transmettre son contexte à une
autre série. Horloge UTC index/timestamp strictement croissante et source
clôturée requises ; métadonnées futures/incohérentes refusées fail-closed.

Lors de la formalisation de la durée de vie, le module
src/agicore/trading/regime_context_v2.py avait le SHA-256
`587e2ea9bad4be0778c10ad101e9266fbe76ffe82810e9e1fd934d0f3b8e46de`.
82 nouveaux tests synthétiques PASS ; 604 tests V2 ciblés PASS.
Fichier tests/unit/trading/test_regime_context_lifetime_v2.py, SHA-256
`7370ab769f3dbfc2b67b7f087449c419198e35ba463501774b0951735ef16927`.
6888 tests locaux PASS, 4 avertissements préexistants, hors test_mcp.py bloqué
dans ce sandbox. Ruff, format, compilation et diff-check PASS.
CI intégrale verte exigée avant fusion ; preuves et SHA de merge dans la PR.
Compositeur et détecteurs figés inchangés. Interface du futur prédicat formel
seulement ; aucune règle de prix/High/Low, franchissement EMA20, MACD, ATR,
volume, session, limite quotidienne, stop, take profit ou exécution d'entrée.
Aucun replay, accès OOS, dataset réel ou calibration MNQ.

La gate pullback EMA20 V2 est acquittée par la décision ci-dessous.

## V2 — EMA20 exacte et pullback causal consommé une seule fois

PR #288 fusionnée après CI #258 verte, merge
`22125e90fe990e75d57549f186215315b9b03008`.
Décision du propriétaire du 2026-10-03 : EMA_PERIOD = 20, ALPHA = 2/21,
EMA_RESET_AT_SESSION = FALSE. Seed exact sur Close[0..19] à l'index 19,
puis EMA20[i] = (2*Close[i] + 19*EMA20[i-1])/21. Calcul en Fraction exacte,
conversion exacte des Decimal finis, sans arrondi/float avant comparaison.
Entiers/Fraction admis ; floats binaires refusés. Aucun reset de session/jour,
comblement de gap ou bougie synthétique. Une observation requise absente,
non clôturée ou un Close requis invalide rend l'EMA indisponible sans saut
ni seed ultérieur. Les indices restent ceux des observations réelles.

Pour k clôturée : ema_reference = EMA20[k-1], connue avant k, sans lecture
de k pour calculer cette référence. Premier pullback possible à k=20.
LONG : Close[k-1] > EMA, Open[k] >= EMA, Low[k] <= EMA, Close[k] > EMA.
SHORT : miroir strict/inclusif, avec Close[k-1] < EMA, Open[k] <= EMA,
High[k] >= EMA, Close[k] < EMA. Contact exact et pénétration autorisés ;
proximité sans contact refusée. Closes égaux à EMA refusés. Aucune couleur
de bougie exigée ; doji admis si toute la géométrie EMA est satisfaite.

OHLC incohérents de k : INVALID_OHLC et false. Close requis manquant/non fini :
INVALID_EMA_INPUT et false. Moins de vingt clôtures antérieures :
INSUFFICIENT_EMA_WARMUP et false. Contexte non ACTIVE, source e elle-même,
k hors e+1..e+8 ou temps écoulé >8 minutes : INELIGIBLE_CONTEXT et false.
Le prédicat pur ne crée, ne consomme ni ne prolonge un contexte.

advance_ema20_pullback_v2 délègue l'ordre causal au cycle de vie figé :
expiration, composition/invalidation, même direction sans refresh, puis
évaluation formelle. Qualification true consomme définitivement à Close[k].
Source_event_types/direction/index/timestamp, pullback index/timestamp et
ema_reference exacte conservés dans le record CONSUMED et la décision.
Référence conservée sur les barres ultérieures et dans le record retiré
si nouvel événement ; aucun second pullback ni réactivation après échec
de future confirmation/entrée. Invalidation opposée/ambiguë gagne sur le
pullback de l'ancien contexte, sans évaluation du nouveau sur sa propre barre.
Métadonnées UTC/clôture/index/timestamps cohérents et causaux obligatoires.

Nouveau module src/agicore/trading/ema20_pullback_v2.py, SHA-256
`6eb8db9aa65d88e740e855489ed323a3a863360663188a9de2833c8d28ccf4a2`.
Extension additive de la provenance CONSUMED dans
src/agicore/trading/regime_context_v2.py, SHA-256
`2086f3573ae43a0254fbfd69ae5b3a3acde02fd3c8c3b38d8c412e4c720f13a2`.
Composition et fonctions de durée de vie inchangées, tout comme les deux
détecteurs et les anciens tests V2.
123 nouveaux tests synthétiques PASS ; 727 tests V2 ciblés PASS.
Fichier tests/unit/trading/test_ema20_pullback_v2.py, SHA-256
`c01408d7377db753173c47b1044a491b80cae3d9682549a6f99ec274b2c15bb1`.
7011 tests locaux PASS, 4 avertissements préexistants, hors test_mcp.py bloqué
dans ce sandbox.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée avant
fusion ; preuves et SHA de merge dans la PR. Baseline initiale pré-replay
non optimisée, indépendante des résultats V1/V1A/V1B. Aucun replay, accès OOS,
dataset réel ou ajustement MNQ 03-26/06-26. Aucun MACD, pente/proximité EMA,
ATR, volume, couleur, SMA14/SMA21, filtre de session, stop, target ou entrée.

La gate confirmation/momentum d'entrée est acquittée par la décision ci-dessous.

## V2 — confirmation clôturée et momentum MACD exact

Point de départ vérifié : PR #289 fusionnée après CI #260 verte, merge
`227714be7ec45a67177e6bd273a66f5afdf1a63a`.
Décision du propriétaire du 2026-10-03 :
EMA_PULLBACK_V2_ENTRY_CONFIRMATION_MOMENTUM figée comme baseline initiale
pré-replay non optimisée. Confirmation seulement sur k+1..k+2 inclusivement,
MAX_CONFIRMATION_AGE_CLOSED_BARS=2, MAX_CONFIRMATION_ELAPSED_TIME=2 minutes.
Le pullback qualifié à Close[k] a consommé son contexte et crée une opportunité
distincte AWAITING_CONFIRMATION. k ne peut jamais se confirmer lui-même.

Corps de k capturé une seule fois : min(Open[k], Close[k]) / max(Open[k], Close[k]).
LONG : Close[q]>Open[q] et Close[q]>pullback_body_high.
SHORT : Close[q]<Open[q] et Close[q]<pullback_body_low.
Toutes les frontières sont strictes ; doji et égalité au bord du corps refusés.
Pas de cassure requise de High[k]/Low[k] ni contrainte High/Low supplémentaire
sur q. La géométrie et la couleur autorisée du pullback demeurent inchangées.

MACD_FAST=12, MACD_SLOW=26, MACD_SIGNAL=9, MACD_SESSION_RESET=FALSE.
EMA12[0]=EMA26[0]=Close[0], MACD[0]=SIGNAL[0]=HIST[0]=0.
Récurrences exactes EMA12 += (2/13)*(Close-EMA12),
EMA26 += (2/27)*(Close-EMA26), MACD=EMA12-EMA26,
SIGNAL += (2/10)*(MACD-SIGNAL), HIST=MACD-SIGNAL.
Conversion exacte Decimal fini en Fraction ; aucun arrondi, float,
reset session/jour ou bougie synthétique. Préfixe causal explicite 0..q,
sans consultation des clés/longueur futures. Warmup mécanique 26+9=35
clôtures, incluant q : première éligibilité à q=34, sinon
INSUFFICIENT_MACD_WARMUP et false sans prolongation de fenêtre.

LONG exige simultanément MACD[q]>SIGNAL[q], HIST[q]>0,
HIST[q]>HIST[q-1], MACD[q]>MACD[q-1]. SHORT est le miroir strict.
Toute égalité ou affaiblissement requis donne FAIL.
NO_MACD_CROSS_REQUIRED ; NO_MACD_MAGNITUDE_THRESHOLD.
Un MACD déjà du bon côté du signal peut confirmer si tout le momentum se
renforce ; aucune règle de crossover V1 n'est héritée.

Temps depuis k >2 minutes : EXPIRED_CONFIRMATION_ELAPSED_TIME avant toute
lecture prix/MACD. Exactement deux minutes inclusif. Candidats traités dans
l'ordre sans sauter k+1 ; premier PASS terminal CONFIRMED à Close[q].
Si k+1 passe, aucune lecture de k+2 pour cette opportunité. Si k+1 échoue,
attente maintenue ; si k+2 échoue, EXPIRED_NO_ENTRY_CONFIRMATION après
évaluation. k+3 ne peut ressusciter une opportunité terminale. Données
finies avant une prochaine clôture : aucun signal ou acte synthétique.
Le contexte source reste CONSUMED après tout résultat, sans second pullback
ni réactivation après échec de confirmation ou future entrée.

Close requis invalide, observation absente/non clôturée : INVALID_MACD_INPUT.
Open de q invalide ou candidate indisponible : INVALID_CONFIRMATION_INPUT.
Ces statuts techniques refusent la confirmation sans saut/reset ni délai
supplémentaire. Métadonnées non causales/incohérentes refusées explicitement.
PASS conserve source_regime_event_types/direction/index/timestamp,
pullback index/timestamp/ema_reference et confirmation index/timestamp,
macd/signal/histogram/previous_macd/previous_histogram exacts et immuables.

Nouveau module src/agicore/trading/ema_pullback_entry_confirmation_v2.py,
SHA-256 `d21e767d569609995ebf4ef289eda041619744f2cfa3b357d2b072ee479e70b6`.
Nouveaux tests tests/unit/trading/test_ema_pullback_entry_confirmation_v2.py,
SHA-256 `4781f45d86d4d1d164c99093050573739c1cf72509065409bfbb67890adf5768`.
114 nouveaux tests synthétiques PASS ; 841 tests V2 ciblés PASS.
7125 tests de régression locaux PASS, 4 avertissements préexistants ;
hors test_mcp.py bloqué dans ce sandbox, inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée
avant fusion ; preuves et SHA de merge dans la PR.
Détecteurs, cycle de vie, EMA20/pullback figés et V1/V1A/V1B inchangés.
Aucun dataset réel, replay, OOS ni calibration MNQ 03-26/06-26.
Aucun fill/ordre, stop/target, breakeven/trailing, sizing, objectif quotidien,
limite de trades, filtre session, SMA14/SMA21, RSI/stochastic ou volume ajouté.
Aucune rentabilité V2 démontrée ; programme toujours PRE_FORMALIZATION.

La gate exécution d'entrée est acquittée par la décision ci-dessous.

## V2 — base fill offline à la seule ouverture suivante

Point de départ vérifié : PR #290 fusionnée après CI #262 verte, merge
`3ee742fa10ecc58dfb03c6dcfb99ba153ecb925a`.
Décision du propriétaire du 2026-10-04 : EMA_PULLBACK_V2_ENTRY_EXECUTION
figée comme baseline initiale pré-replay non optimisée, indépendante de V1/V1A/V1B.
Confirmation sur q, décision à Close[q], exécution uniquement à Open[q+1],
ORDER_SEMANTICS=MARKET, MAX_EXECUTION_AGE_CLOSED_BARS=1,
MAX_EXECUTION_ELAPSED_TIME=1 minute. NO_FILL_ON_q ; NO_MAX_ENTRY_GAP_FILTER.
Close[q] crée PENDING_NEXT_BAR_OPEN sans fill. LONG=BUY, SHORT=SELL_SHORT,
étiquettes offline uniquement ; prix de base exact execution_price_before_costs=Open[q+1].

Interface d'ouverture limitée à bar_index, timestamp_utc et Open. L'évaluateur
n'accède ni à High, Low, Close, Volume, ni à is_closed, même avec une OHLCV
complète en mémoire. Index/horloge validés avant toute lecture de l'Open.
Exiger q+1 et 0 < timestamp[q+1]-timestamp[q] <=1 minute, frontière inclusive.
Temps >1 minute : EXPIRED_EXECUTION_GAP avant lecture du prix. Timestamps
non croissants/invalides : INVALID_EXECUTION_CLOCK, aucun fill, état technique
terminal FAILED_INVALID_EXECUTION_CLOCK. Propre barre q répétée avec son
timestamp connu : PENDING conservé, sans lecture Open ni auto-exécution.

q+1 absent ou fin des données : EXPIRED_NO_EXECUTION sans fill synthétique.
Si q+2 ou plus arrive sans q+1, expiration par son seul index sans lire son
timestamp/prix ; aucun report. Open absent/non fini/non positif :
INVALID_EXECUTION_INPUT / FAILED_INVALID_EXECUTION_INPUT, aucun remplacement
par Close, midpoint, EMA20 ou prix antérieur. Conversion exacte Decimal fini
en Fraction ; entiers/Fraction admis, float/chaîne/bool refusés selon V2.
Aucun arrondi préalable. Gap de prix valide même très grand : fill à l'Open,
sans filtre de distance, clamp ou annulation arbitraire.

EntryExecutionBookV2 est le registre immuable d'une seule série offline,
transmis aux appels suivants. register_entry_execution_v2 exige la décision
CONFIRMED et valide sa provenance avant enregistrement. Réenregistrer la même
confirmation ou une copie équivalente conserve l'état canonique, sans remise
à PENDING ni nouveau fill. Provenance changée sous la même identité refusée.
execute_entry_open_v2 n'opère que sur un record enregistré ; None signifie
absence définitive de q+1, pas attente anticipée de son ouverture.
FILLED, expirations et échecs restent terminaux et rendent le même registre
sans lecture marché. Les confirmations distinctes gardent leurs états séparés ;
aucune règle de position, limite de trades ou quantité introduite.

Record immuable : source_regime_event_types/index/timestamp/direction,
pullback index/timestamp/ema_reference, confirmation index=q/timestamp,
execution index=q+1/timestamp/side et prix avant coûts exact. Sémantique MARKET
et BUY/SELL_SHORT conservée, avec le EntryConfirmationRecordV2 complet.
Chaîne événement -> pullback consommé -> confirmation -> exécution préservée,
sans mutation des snapshots précédents ni réactivation du contexte source.

Nouveau module src/agicore/trading/ema_pullback_entry_execution_v2.py,
SHA-256 `87e32388c022b66cb3b5583b9399fc1091f1bc449c3d58e35466b5a6d1224998`.
Nouveaux tests tests/unit/trading/test_ema_pullback_entry_execution_v2.py,
SHA-256 `94ccf50189ade95bcf4002232cd16d18f4698c6cdee57582215619bb5b5f5777`.
119 nouveaux tests synthétiques PASS ; 960 tests V2 ciblés PASS.
7244 tests de régression locaux PASS, 4 avertissements préexistants ;
hors test_mcp.py bloqué dans ce sandbox, inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée
avant fusion ; preuves et SHA de merge dans la PR.
Tous les modules et tests V2 antérieurs, V1/V1A/V1B et résultats figés inchangés.
Aucun data/, dataset réel, replay, OOS ni calibration MNQ 03-26/06-26.
Aucun broker/Apex/Rithmic/NinjaTrader live, slippage/commission/spread,
quantité, stop, take profit, breakeven ou trailing. Ce modèle n'autorise ni
stratégie V2 complète ni paper trading ; Risk Engine, sizing et toutes les
sorties devront être formalisés. Rentabilité V2 toujours non évaluée.

La gate stop initial est acquittée par la décision ci-dessous.

## V2 — stop initial structurel exact connu avant l'entrée

Point de départ vérifié : PR #291 fusionnée après CI #264 verte, merge
`077474d1b6a90415cafd838e31b5c40e5a849d8a`.
Décision du propriétaire du 2026-10-04 : EMA_PULLBACK_V2_INITIAL_STOP
figée comme baseline initiale pré-replay non optimisée, indépendante de V1/V1A/V1B.
Pullback k, confirmation q dans {k+1,k+2}, entrée q+1. Fenêtre structurelle
k..q inclusive : deux ou trois bougies clôturées, aucun prix futur.
TICK_SIZE=Fraction(1,4), STOP_BUFFER_TICKS=1, STOP_BUFFER=0.25 point.
LONG=min Low[k..q]-1 tick ; SHORT=max High[k..q]+1 tick.
known_at=Close[q] ; INITIAL_STOP_RECALCULATION=FORBIDDEN.

L'extrême du pullback, de la barre intermédiaire ou de la confirmation compte.
Exemple LONG [20000,19998,19999] : extrême 19998, stop exact 19997.75.
Aucune lecture avant k ou après q, dont aucun Open/High/Low/Close/Volume q+1.
High/Low requis présents, finis et High>=Low ; sinon
INVALID_STRUCTURAL_STOP_INPUT et initial_stop=NONE. Indice requis absent,
dont barre intermédiaire : INCOMPLETE_STRUCTURAL_STOP_WINDOW et NONE.
Métadonnées cohérentes, causales, UTC et observations clôturées exigées.
Decimal fini converti exactement en Fraction, sans arrondi ni correction
de grille de ticks. High=Low admis ; aucun filtre range/corps/prix positif
sur le stop, ni distance minimale/maximale, ATR, pourcentage ou montant fixe.
Un stop large reste valide ; son acceptation relève du futur Risk Engine/sizing.

InitialStopBookV2 conserve le snapshot immuable de Close[q] pour une seule
série offline. register_initial_stop_v2 retourne le même registre pour une
confirmation équivalente, avant toute relecture du marché. Aucun recalcul,
élargissement, resserrement ou réparation rétroactive d'un snapshot invalide.
Provenance changée sous la même identité refusée ; confirmations distinctes
indépendantes. evaluate_initial_stop_v2 calcule le snapshot initial exact.

Après fill PR #291, bind_initial_stop_to_entry_v2 utilise uniquement les
records immuables de l'exécution : aucun input de bougie supplémentaire.
LONG stop<entry ou SHORT stop>entry : ARMED. LONG entry<=stop ou SHORT
entry>=stop : BREACHED_AT_ENTRY_OPEN, égalité incluse. Le stop ne bouge pas
et FILLED reste FILLED : aucune annulation rétroactive ou sortie choisie.
Exécution pending/expirée/invalide : aucun armement. Stop indisponible : NONE,
sans substitution ni nouvelle politique d'entrée. Lier le même fill est
idempotent ; un autre fill ne remplace pas le lien conservé.

Provenance du stop : source_event_types/index/timestamp/direction,
pullback index=k/timestamp/ema_reference, confirmation index=q/timestamp,
structural_window_first_bar=k/last_bar=q/extreme, buffer_ticks=1/tick_size,
initial_stop_price, stop_known_at_bar_index=q/timestamp[q] et confirmation
complète. Après fill : entry_bar_index=q+1/timestamp, entry_price, stop_state
et exécution complète. Records, niveaux et provenance immuables.

Nouveau module src/agicore/trading/ema_pullback_initial_stop_v2.py,
SHA-256 `533643ea6efa9ba13972b10f86555e7dd5dcf7e10bfa5ea6b76af740d08846b4`.
Nouveaux tests tests/unit/trading/test_ema_pullback_initial_stop_v2.py,
SHA-256 `45366d4613ac1acf1befcfc3a966078bf8ff25a4696da608f143ae6b1463231a`.
134 nouveaux tests synthétiques PASS ; 1094 tests V2 ciblés PASS.
7378 tests de régression locaux PASS, 4 avertissements préexistants ;
hors test_mcp.py bloqué dans ce sandbox, inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée
avant fusion ; preuves et SHA de merge dans la PR.
Tous les modules/tests V2 antérieurs, dont entrée PR #291, V1/V1A/V1B et
résultats figés inchangés. Aucun data/, dataset réel, replay, OOS ni calibration
MNQ 03-26/06-26. Aucun broker, trigger/fill de sortie, take profit, breakeven,
trailing, sizing, quantité, coût ou modification EMA/swing/ATR.
V2 reste PRE_FORMALIZATION ; aucune rentabilité évaluée ni stratégie complète.

La gate déclenchement/fill du stop est acquittée par la décision ci-dessous.

## V2 — stop marché structurel, contacts et gaps exacts

Point de départ vérifié : PR #292 fusionnée après CI intégrale #266 verte,
merge `48a89ae0602a7d80fb54b9918e2511f5e96dc864`.
Décision du propriétaire du 2026-10-04 : EMA_PULLBACK_V2_STRUCTURAL_STOP_TRIGGER_FILL
figée comme baseline initiale pré-replay non optimisée. STOP_ORDER_SEMANTICS=STOP_MARKET,
STOP_TOUCH_IS_TRIGGER=TRUE ; niveau PR #292 immuable, aucun recalcul.
LONG protective_action=SELL ; SHORT BUY_TO_COVER, étiquettes offline sans broker.

BREACHED_AT_ENTRY_OPEN déclenche immédiatement après le fill d'entrée PR #291,
sur e=q+1 : ENTRY_OPEN, base_stop_fill_price=entry_price=Open[e]. Aucun accès
High/Low/Close/Volume e ni prix de stop périmé favorable. L'entrée reste FILLED,
sans annulation/refus/no-trade rétroactif. Exemple LONG stop20000/Open19998.50 :
entrée et sortie de base à 19998.50, jamais sortie artificielle à 20000.

ARMED protège e dès son Open : monitoring_first_bar=e. Open[e] est déjà
retenu par le fill ; aucun second test de gap ni nouvel accès Open requis.
Low[e]<=stop LONG / High[e]>=stop SHORT : fill INTRABAR au stop exact.
Sur r>e, priorité au gap : Open[r]<=stop LONG / >=stop SHORT remplit à cet
Open avant toute lecture de l'extrême. Sinon Low[r]<=stop LONG / High[r]>=stop
SHORT remplit au niveau initial. Toutes les égalités déclenchent ; aucun coût.

Accès limités à index/timestamp et Open + Low LONG / High SHORT lorsque
nécessaires. Jamais Close, Volume, extrême opposé, is_closed, EMA20, MACD ou ATR.
Open fini, puis si gap exclu extrême fini et Low<=Open / High>=Open, sinon
FAILED_INVALID_STOP_OBSERVATION. Decimal/int/Fraction exacts ; pas d'arrondi,
float binaire, substitution ou validation OHLC complète ajoutée. Le test de
gap ne dépend pas de la qualité d'un extrême futur non lu.

Observations réelles e,e+1,e+2... traitées une à une, sans préfixe futur.
Indice sauté, dont e non surveillée : FAILED_INCOMPLETE_STOP_OBSERVATION
avant prix/horloge, sans supposer le stop intact ni fabriquer un fill.
Index/horloge invalide ou relecture d'une observation active déjà traitée :
FAILED_INVALID_STOP_OBSERVATION. Timestamps cohérents UTC et croissants ;
écarts de session de plusieurs heures/jours autorisés sur l'indice suivant.
Aucune expiration de temps/session ; stop encore actif au prochain vrai Open.

StructuralStopExecutionBookV2 est immuable et porté par le caller pour une
seule série offline. register_structural_stop_execution_v2 exige le stop déjà
lié à son fill, puis enregistre ARMED ou directement FILLED_STOP à ENTRY_OPEN.
observe_structural_stop_v2 examine seulement l'observation fournie : gap connu
à Open[r], sinon extrême adverse complet disponible au plus tard à Close[r].
INTRABAR ne fournit aucune heure précise : exact_intrabar_timestamp=None,
trigger_known_at=NO_LATER_THAN_CLOSE[r]. Timestamp de barre conservé comme
métadonnée, pas comme heure inventée de contact.

FILLED_STOP et les deux erreurs sont terminaux : appels répétés sans accès
marché, deuxième fill, reset ou réparation rétroactive. Source de stop/fill
altérée sous la même identité refusée. Provenance complète immuable : événement,
pullback, EMA exacte, confirmation, entrée, stop/extreme/tick/buffer/state_at_entry,
trigger index/timestamp/phase/known_at, base_stop_fill_price et action STOP_MARKET,
avec InitialStopAtEntryV2 et ses records imbriqués. Stop initial et snapshots
antérieurs inchangés, dont l'exécution d'entrée toujours FILLED.

Fin de données avec ARMED : observation=None rend le même registre, aucun fill,
expiry ou clôture synthétique. Politique de fin de données séparée.

Nouveau module src/agicore/trading/ema_pullback_structural_stop_trigger_fill_v2.py,
SHA-256 `1bc60d1fac22d1c6b5a3ed44023051a1bfce8a066ce5617b64b4ea35316f3efd`.
Nouveaux tests tests/unit/trading/test_ema_pullback_structural_stop_trigger_fill_v2.py,
SHA-256 `f0770409c74f777bd2745af615f9096d779ed31629117677081838291784745f`.
160 nouveaux tests synthétiques PASS ; 1254 tests V2 ciblés PASS.
7538 tests de régression locaux PASS, 4 avertissements préexistants ;
hors test_mcp.py bloqué dans ce sandbox, inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée ; SHA
de merge dans la PR. Tous les modules/tests antérieurs, dont PR #291/#292,
V1/V1A/V1B et résultats figés restent inchangés. Aucun data/, dataset réel,
replay, OOS ni calibration MNQ 03-26/06-26. Aucun broker, coûts/slippage,
take profit, sortie EMA20, breakeven, trailing, time/session exit, Risk Engine
ou sizing. Aucune priorité entre sorties ni quantité définie silencieusement.
V2 demeure PRE_FORMALIZATION ; rentabilité non évaluée.

La gate de politique des signaux pendant une position ouverte est acquittée
par la décision ci-dessous.

## V2 — une position par série, suppression avant contexte

Point de départ vérifié : PR #293 fusionnée après CI intégrale #268 verte,
merge `466a64f666f903f1a7966374205a1e3503f37aeb`.
Décision du propriétaire du 2026-10-04 : EMA_PULLBACK_V2_OPEN_POSITION_SIGNAL_POLICY
figée comme baseline initiale pré-replay non optimisée. Une position simultanée
maximum par instance de stratégie/instrument/série. PYRAMIDING, HEDGING,
FLIP_ON_OPPOSITE_SIGNAL, SCALE_IN et SIGNAL_QUEUE_WHILE_OPEN désactivés.

Seul le fill d'entrée canonique PR #291 produit OPEN_LONG/OPEN_SHORT ; un régime,
contexte, pullback, confirmation ou PENDING ne suffit pas. Seul un fill terminal
de sortie formelle produit FLAT ; actuellement FILLED_STOP PR #293. ARMED ou
échec de monitoring sans fill conserve OPEN et bloque toute admission.

Pendant OPEN_LONG ou OPEN_SHORT, tout nouveau régime/opportunité LONG ou SHORT
est SUPPRESSED_POSITION_OPEN avant création de RegimeEventContextV2. Télémétrie
brute de composition maintenue, EMA20/MACD/impulsion/retournement peuvent continuer
séparément, mais aucun lifetime/pullback exécutable ni chaîne complète nouvelle.
Aucune queue, attente, restauration après sortie, couverture, flip, deuxième
position, augmentation de quantité ou recalcul de prix moyen. La source
consommée antérieure reste immuable en audit et ne redevient jamais actionable.

OpenPositionSignalPolicyBookV2 conserve le scope explicite et l'historique
immuable de positions/décisions. apply_position_entry_fill_v2 exige FILLED après
la confirmation connue et un pullback admis/consommé dans ce registre ; une
chaîne supprimée, restaurée ou injectée depuis un autre chemin est refusée.
Le stop lié doit être celui connu à l'Open d'entrée, sans importer son futur
monitoring. Un même fill, y compris après sa sortie, ne crée pas une deuxième
position ; provenance modifiée sous une identité existante refusée.

advance_open_position_signal_policy_v2 résout d'abord le stop existant via la
gate PR #293, actualise la position puis compose/admet les événements de
Close[r]. Stop rempli à Open[r] ou intrabar r : FLAT à Close[r], donc nouveau
régime admissible. Position encore ouverte : signal supprimé. Le nouveau
contexte attend toujours r+1 pour un pullback. Aucun régime passé n'est restauré.

BREACHED_AT_ENTRY_OPEN conserve le véritable fill d'entrée, puis son fill stop
au même Open[e] : OPEN puis FLAT, prix de base et chaîne immuables. Aucun accès
OHLCV e pour cette résolution, annulation rétroactive ou NO_TRADE. Nouveau
régime de Close[e] admissible. Les erreurs de monitoring et fin de données ne
fabriquent ni fill ni état FLAT ; gaps temporels/session n'expirent pas le stop.

Clôture répétée/fill répété : même registre, sans duplicate ou réouverture.
Suppression conservée avec index/timestamp/direction/familles, position_state,
reason POSITION_ALREADY_OPEN et index/direction de l'entrée active. Aucun
mapping OHLC ou barre future consulté pour une nouvelle opportunité pendant
OPEN. Les tests protègent la symétrie LONG/SHORT et la provenance figée.

Nouveau module src/agicore/trading/ema_pullback_open_position_signal_policy_v2.py,
SHA-256 `a76b5a11a0be40e3eb404582483fd9b4c17355279bf9102e34fb671da2326954`.
Nouveaux tests tests/unit/trading/test_ema_pullback_open_position_signal_policy_v2.py,
SHA-256 `6409a956d27efe25f4bf9522ab6b51cbe1d29545c414224137d7e9a31557c119`.
94 nouveaux tests synthétiques PASS ; 1348 tests V2 ciblés PASS.
7632 tests de régression locaux PASS, 4 avertissements préexistants ;
hors test_mcp.py bloqué dans ce sandbox, inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée avant
fusion ; preuves et SHA de merge dans la PR. Périmètre de quatre fichiers ;
tous les modules/tests V2 antérieurs, V1/V1A/V1B et résultats figés inchangés.
Aucun data/, dataset réel, replay, OOS ou ajustement MNQ 03-26/06-26. Aucun
broker, ordre réel, coût, sizing, quantité, take profit, breakeven ou trailing.
V2 demeure PRE_FORMALIZATION ; rentabilité non évaluée.

La gate Risk Engine/position sizing est acquittée par la décision ci-dessous.

## V2 — Risk Engine MNQ et quantité figée à Close[q]

Point de départ vérifié : PR #294 fusionnée après CI intégrale #270 verte,
run `37193299058`, head `a5408b5b489cfa62ccc1d194bf404ed86dec3538`,
merge `5db43eb9ffa096344c4f1fc79fcb5104956bf323`, arbre
`dfae5cc43fba7670092aad248b4614c41c044b4d`.
Décision du propriétaire du 2026-10-04 : EMA_PULLBACK_V2_RISK_ENGINE_POSITION_SIZING
figée comme baseline initiale pré-replay non optimisée. Aucun paramètre dérivé
des résultats V1/V1A/V1B, MNQ 03-26 ou MNQ 06-26.

MNQ seulement : tick Fraction(1,4), valeur point Fraction(2,1), valeur tick
Fraction(1,2), budget structurel prévu Fraction(100,1) USD ; minimum 1,
maximum 2 contrats. Le budget couvre le risque de prix structurel prévu,
sans coûts et sans garantie de perte réalisée maximale à 100 USD.

La décision est connue à Close[q], après confirmation formelle et stop initial
EVALUATED connu à q, avant toute donnée q+1. sizing_reference_price=Close[q]
exclusivement ; aucune lecture de Open/High/Low/Close/Volume de q+1. LONG :
distance=Close[q]-stop, strictement positive. SHORT : distance=stop-Close[q],
strictement positive. Toucher/mauvais côté : INVALID_STRUCTURAL_RISK_DISTANCE.
Close[q] et stop doivent être exactement sur la grille de 0.25 ; sinon
INVALID_MNQ_TICK_GRID sans correction silencieuse. Fraction exact du début à
la fin, conversion Decimal exacte sans float binaire ni arrondi intermédiaire.

risk_per_contract_usd=distance*2 ; raw_quantity=floor(100/risk_per_contract) ;
approved_quantity=min(2,raw_quantity). Quantité inférieure à 1 : REJECT avec
RISK_PER_CONTRACT_EXCEEDS_BUDGET. Sinon APPROVE avec planned_total_risk_usd
=quantity*risk_per_contract <=100. Exactement 50 USD/contrat donne 2 contrats ;
exactement 100 donne 1 ; au-delà de 100, rejet. Les exemples 15/35/55 points
donnent respectivement 2 contrats/60 USD, 1 contrat/70 USD et REJECT.
L'exemple Close[q]=20010/stop LONG=19990 donne 40 USD/contrat et 2 contrats/80 USD.

Fail-closed pour instrument non MNQ, confirmation absente/non qualifiée, stop
absent/non EVALUATED, provenance incohérente, prix absent/non fini, clock de
q invalide, position non FLAT ou état invalide. Aucun contrat fixe de fallback,
stop par défaut, filtre de gap supplémentaire ou adaptation aux performances.
Même risque structurel donne même quantité, quelle que soit la famille du
régime ou l'histoire des décisions. Aucun equity/PnL/streak/martingale,
volatilité, Kelly ou score utilisé.

RiskPositionSizingBookV2 conserve une décision immuable par pullback consommé
et le scope stratégie/série de la politique PR #294. L'autorisation vérifie la
véritable source admise/consommée et l'état connu à Close[q] ; une chaîne
supprimée/stale ne peut créer d'entrée. APPROVE seul crée PENDING PR #291 pour
le seul Open[q+1] avec quantité figée. REJECT ne crée aucun record d'exécution,
rend REJECTED_BY_RISK_ENGINE terminal et ne peut être reconsidéré plus tard.
Les doublons rendent le snapshot canonique avant toute relecture de prix/stop.

execute_risk_approved_entry_open_v2 réutilise PR #291 sans changer ses règles,
et RiskSizedEntryRecordV2 conserve un seul lien fill/quantité/décision. Aucun
redimensionnement au futur Open, même si le gap élargit/réduit/franchit le risque.
BREACHED_AT_ENTRY_OPEN conserve l'entrée FILLED puis le stop au même Open
PR #292/#293, quantité inchangée. Prix réel/distance signée réelle sont seulement
diagnostiques ; ils ne modifient pas le sizing. Un gap adverse après APPROVE
peut dépasser le budget prévu. Idempotence du fill/expiry et refus de provenance
altérée conservés ; aucune exécution sans APPROVE ni résurrection.

La décision conserve instrument/direction, régime/pullback/EMA/confirmation,
known_at=q/timestamp[q], référence Close[q], stop, distance, valeur point,
risque unitaire/budget/quantité brute/approuvée/risque total, décision/raison
et état de position. Les records complets source/confirmation/stop restent
liés immuablement. Un rejet garde les champs déjà validés, quantité autorisée 0
et aucun risque total approuvé.

Nouveau module src/agicore/trading/ema_pullback_risk_position_sizing_v2.py,
SHA-256 `36002943acdd56a4600209c701f80a04f855a5b27450bf55ce85c934686b549a`.
Nouveaux tests tests/unit/trading/test_ema_pullback_risk_position_sizing_v2.py,
SHA-256 `3f6e0a3554aef28b5368c3d93909c0624dbc982cc6e9ac05ea632ed580d7d4e2`.
164 nouveaux tests synthétiques PASS en 1.25s ; 1512 tests V2 ciblés PASS en 4.22s.
7796 tests de régression locaux PASS en 118.26s, 4 avertissements préexistants ;
hors test_mcp.py bloqué dans ce sandbox, inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée avant
fusion ; preuves et SHA de merge dans la PR. Périmètre de quatre fichiers ;
tous les modules/tests V2 antérieurs, V1/V1A/V1B et résultats figés inchangés.
Aucun data/, dataset réel, replay, OOS, calibration MNQ, broker ou ordre réel.
Aucun coût, take profit, breakeven, trailing ou sortie additionnelle.
V2 demeure PRE_FORMALIZATION ; rentabilité non évaluée.

La gate frais/slippage est acquittée par la décision ci-dessous.

## V2 — frais/slippage exacts et comptabilité des fills réels offline

Point de départ vérifié : PR #295 fusionnée après CI intégrale #272 verte,
run `37202575782`, head `e3d2f320ef58c8705cbc370fc71453545e0911ab`,
merge `ee02674b75273a82748c2e77f873fed6b5bd3313`, arbre
`3251f8b93429dff08e350a9bf827551d17f1b895`.
Décision du propriétaire du 2026-10-04 : EMA_PULLBACK_V2_FEES_AND_SLIPPAGE_MODEL
figée comme baseline initiale pré-replay non optimisée. Convention de coûts
V1 volontairement reprise pour comparabilité, sans calibration de performance
V2 ni ajustement d'après les résultats MNQ déjà utilisés.

MNQ : tick Fraction(1,4), point Fraction(2,1), tick value Fraction(1,2).
Frais=Fraction(51,100) USD par contrat et par fill ; slippage adverse=1 tick
par fill. SPREAD_MODEL=ABSORBED_IN_SLIPPAGE ; EXTRA_SPREAD_CHARGE=Fraction(0).
SLIPPAGE_ACCOUNTED_EXACTLY_ONCE et NO_POST_CONFIRMATION_RESIZING vrais.
Aucune nouvelle hypothèse de signal, stop, quantité ou sortie.

Les fills de base execution_price_before_costs/base_stop_fill_price demeurent
immuables. FillCostRecordV2 conserve un prix effectif distinct : BUY ou
BUY_TO_COVER => base+0.25 ; SELL ou SELL_SHORT => base-0.25. Chaque fill réel
paie quantity*0.51 USD ; slippage économique quantity*0.50 USD diagnostique.
Aller-retour : 1.02 USD de frais par contrat, 2.04 USD pour deux contrats.
Prix LONG entry 20000 => 20000.25, stop 19990 => 19989.75 ; SHORT miroir.

PnL LONG=(effective_exit-effective_entry)*2*quantity ; SHORT inverse exact.
net_realized_pnl_usd=gross_price_pnl_usd-entry_fee-exit_fee. Le slippage est
déjà dans les prix effectifs et n'est jamais soustrait une deuxième fois ;
aucun spread additionnel. diagnostic_total_slippage_cost_usd est seulement
une métrique d'audit. Aucun cumul de frais dépendant des appels.

Gap stop PR #293 inchangé : LONG stop structurel 20000/Open suivant 19995
=> base 19995, puis effectif 19994.75, sans retour favorable à l'ancien stop.
BREACHED_AT_ENTRY_OPEN conserve deux fills de base au même Open ; chacun
paie son slippage et ses frais. Net=-Fraction(202,100) par contrat et
-Fraction(404,100) pour deux contrats, symétriquement LONG/SHORT. Aucun
NO_TRADE/annulation/PnL nul fabriqué.

FeesAndSlippageBookV2 partage le scope stratégie/série du registre de risque.
account_entry_fill_v2 exige le RiskSizedEntryRecordV2 effectivement FILLED
et sa source APPROVE canonique. PENDING, REJECT, expiry ou exécution invalide
sans fill ne paient rien et ne créent aucun record. Quantité exclusivement
approved_quantity figée à Close[q], sans redimensionnement ou rejet rétroactif.
Les coûts d'entrée sont immédiatement enregistrés, mais gross/net realized
PnL et exit sont None jusqu'à une sortie formelle réellement remplie.

account_structural_stop_fill_v2 exige un FILLED_STOP canonique, seule sortie
formalisée actuellement. ARMED/erreur de monitoring/absence de sortie ne
créent aucun exit, frais d'exit ou PnL réalisé, notamment en fin de données.
Le modèle de coûts ne lit aucune OHLCV, barre future ou mark price et ne
déclenche pas lui-même le stop. Les niveaux, clocks et triggers restent figés.

TradeCostRecordV2 conserve le record complet risque/entrée (régime, pullback,
EMA, confirmation et quantité) et, si présent, le fill stop complet et les
coûts d'exit. Les métadonnées d'exit doivent correspondre au stop/à l'entrée
originaux. Prix de base/effectifs, ticks, frais, total fees, diagnostic
slippage, PnL gross/net et exit_type sont immuables et traçables. Répéter
l'entrée ou le stop rend le même registre sans second débit ; ancienne
observation ARMED ne peut effacer une sortie déjà comptabilisée. Provenance
altérée et doublons de source refusés.

Le budget prévu de PR #295 demeure 100 USD de risque structurel pré-trade,
sans révision par les coûts. Une perte nette peut le dépasser : à 100 USD
prévus sur 2 contrats, stop sans gap => -104.04 USD nets ; un gap peut la
dépasser davantage. Risque prévu et perte réalisée restent distincts.

Prix, valeurs point/tick, frais, slippage et PnL en Fraction exacts, sans
float ni arrondi intermédiaire. report_usd_cents_v2 utilise HALF_UP au seul
reporting monétaire, avec Decimal à deux décimales et Fraction interne
conservée. Arrondi entier exact indépendant du contexte Decimal, testé
aux demi-centimes signés et sur rationnels périodiques/grands montants.
Aucune nouvelle réparation de grille/condition post-fill ajoutée.

Nouveau module src/agicore/trading/ema_pullback_fees_and_slippage_v2.py,
SHA-256 `612c5397659ded830e43bd8b740442edc6852b389873e2667c37518ce0cfb0b6`.
Nouveaux tests tests/unit/trading/test_ema_pullback_fees_and_slippage_v2.py,
SHA-256 `8e791ea05d8a99e8fce664d63e17c8b38a710e121b2460df040bd9aed962dea1`.
108 nouveaux tests synthétiques PASS en 1.06s ; 1620 tests V2 ciblés PASS en 6.16s.
7904 tests de régression locaux PASS en 147.96s, 4 avertissements préexistants ;
hors test_mcp.py (blocage sandbox préexistant), inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée avant
fusion ; preuves et SHA de merge dans la PR. Périmètre de quatre fichiers ;
modules/tests antérieurs V2, V1/V1A/V1B et résultats figés inchangés. Tests
synthétiques de comptabilité composés avec les vraies gates EMA/confirmation,
Risk Engine, fill de base et stop, sans replay de données de marché.
Aucun data/, dataset réel, OOS, calibration MNQ, broker ou ordre réel. Aucun
take profit, breakeven, trailing, EMA/session exit, daily profit lock,
max daily trades, equity, tarif broker live, bid/ask replay ou slippage dynamique.
V2 demeure PRE_FORMALIZATION ; rentabilité non évaluée.

La gate EMA_PULLBACK_V2_EXIT_POLICY_REQUIRED est acquittée ci-dessous.

## V2 — politique de sortie stop immuable et EMA20 au prochain Open

Point de départ vérifié : PR #296 fusionnée après CI intégrale #274 verte,
run `37224696729`, head `8728c414e4190c7c68b42f988bb7e3cad3f41343`,
merge `8576dc560bd6e99f4f7ab0aab2fec9ae1a58d642`, arbre
`528392afe0cfd193ed1382fa58d502f8f22f2b66`.
Décision du propriétaire du 2026-10-04 : EMA_PULLBACK_V2_EXIT_POLICY figée
comme baseline initiale pré-replay, non optimisée, sans aucun résultat V2.

Exactement deux sorties : IMMUTABLE_STRUCTURAL_STOP (PR #292/#293 inchangées)
et EMA20_POSITION_EXIT. TAKE_PROFIT, BREAKEVEN, TRAILING_STOP, TIME_EXIT et
SESSION_EXIT = NONE. Le stop initial n'est jamais déplacé/recalculé.

L'EMA20 de sortie est evaluate_ema20_v2, même seed exact à 19 par moyenne des
20 closes, même récurrence Fraction(2,21), aucun reset de session ni bougie
synthétique. La décision à Close[r] utilise Close[r] et EMA20[r], tous deux
connus. LONG strictement sous EMA => signal ; SHORT strictement au-dessus
=> signal ; égalité => HOLD. Une EMA indisponible/invalide ne signale pas.
La clôture d'entrée e peut déjà signaler, sans durée minimale de détention,
si son stop n'a pas fermé la position auparavant.

Signal => PENDING_EMA20_EXIT, jamais de fill sur r. Seul Open[r+1] est
exécutable MARKET : SELL LONG, BUY_TO_COVER SHORT. Prix de base exact=Open.
À l'Open, seuls index/timestamp/Open sont lus, sans H/L/C/Volume. Barre absente
=> EXPIRED_NO_EXIT_EXECUTION ; écart >1 minute => EXPIRED_EXIT_GAP ; exactement
une minute admissible. Aucun report du même ordre sur r+2, aucun prix remplacé.
Horloge non causale/Open invalide échouent sans fill EMA inventé.

process_exit_policy_open_v2 vérifie d'abord le gap du stop structurel. S'il
est déclenché, fill stop au même Open, motif STRUCTURAL_STOP et annulation
EMA pending. Sinon un EMA pending admissible remplit au même Open avant
toute lecture du range. Si la position reste ouverte seulement, la phase
process_exit_policy_close_v2 observe l'extrême adverse et résout le stop
intrabar avant l'évaluation de clôture EMA. Un stop intrabar empêche donc
tout signal EMA sur sa barre, sans lecture de l'historique EMA pour cette sortie.

Les fills stop proviennent directement de l'observateur PR #293 inchangé.
Grand gap temporel/session autorisé pour un stop actif entre observations
indexées consécutives ; saut d'indice reste fail-closed selon PR #293.
L'expiration de l'ordre EMA ne désarme pas le stop et ne devient jamais un
fill différé. Une nouvelle clôture peut produire son propre nouveau signal
si la position reste ouverte ; l'ancien record terminal reste expiré.

PositionRecordV2 accepte le fill terminal EMA avec sa provenance complète,
passe à FLAT et retire le stop actif ; un nouveau régime formé au Close de
cette barre peut alors être admis selon PR #294. Aucun ancien contexte
supprimé n'est restauré. BREACHED_AT_ENTRY_OPEN conserve entrée réelle puis
stop au même Open, deux fills et coûts, état final FLAT.

account_ema20_exit_fill_v2 étend PR #296 à la sortie formelle EMA sans modifier
ses constantes/formules. Quantité approuvée figée, frais=0.51 USD/contrat/fill,
slippage adverse=1 tick : SELL base-0.25, BUY_TO_COVER base+0.25. Base et
effectif restent distincts. PnL effectif moins frais, slippage diagnostique
jamais déduit une deuxième fois, aucun extra spread. Une position ne peut
être réalisée deux fois par un stop puis une EMA ou inversement.

Fin de données sans fill réel : OPEN_UNREALIZED, realized PnL=None, stop
non synthétisé, signal pending expiré, aucune liquidation forcée à Close.
Un stop déjà réellement rempli reste terminal. Valorisation unrealized
éventuelle seulement diagnostique. Les records immuables retiennent régime,
pullback, EMA de référence, confirmation, risque, entrée, quantité, stop,
type/index/timestamp du signal, close_at_signal, ema20_at_signal,
index/timestamp d'exécution, motif, prix de base/effectif et coûts.
Idempotence des phases/comptes ; provenance altérée/doublons refusés.

Nouveau runtime src/agicore/trading/ema_pullback_exit_policy_v2.py,
SHA-256 `ddac039586bf4fe0ec5fbe9b55607aecdc42836066d11f0fe5fb257c45a2cac7`.
Nouveaux tests tests/unit/trading/test_ema_pullback_exit_policy_v2.py,
SHA-256 `7e6f5933a2d08a6fc569597f79fd805e05055482d422bbc498dc6b89699946c4`.
Extension de types/lifetime position, SHA-256
`23be07a150feb11a693257d54dfa24f14e7d28b945906813a225b98f0aa39095` ;
extension comptable EMA, SHA-256
`f68ae2feb6eb37e1f1ad5707aae1e8317abc2888deb24478a831711634aee12d`.
91 nouveaux tests synthétiques PASS en 0.70s ; 1711 tests V2 PASS en 4.94s.
7995 tests de régression locaux PASS en 132.91s, 4 avertissements préexistants ;
hors test_mcp.py (blocage sandbox préexistant), inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS. CI intégrale verte exigée sur
le head exact avant fusion ; preuves et SHA de merge conservés dans la PR.
Six fichiers cohérents : runtime/tests, extensions des records position et
comptabilité pour une vraie sortie EMA terminale, charte et checkpoint.
EMA20, stop initial, trigger/fill stop et sizing byte-identiques au parent ;
aucun test antérieur, règle V1/V1A/V1B ou résultat figé modifié.
Aucun data/, dataset réel, replay, OOS, calibration MNQ, broker ou ordre réel.
V2 demeure PRE_FORMALIZATION ; rentabilité non évaluée.

La demande de formalisation du 2026-10-05 est traitée par l'audit ci-dessous.

## V2 — audit des opportunités concurrentes avant le premier fill

Point de départ vérifié : PR #297 fusionnée après CI intégrale #276 verte,
run `37227320193`, head `cf95cdf6dcfce549bd62d91f64c58d7ed0dacfaf`,
merge `a0a6bb931d2e47ce6bd5e5f54a83450e4b51db59`, arbre
`10740a2d36a4cc7c33487114222cfeec921a3423`.
Le 2026-10-05, le propriétaire demande EMA_PULLBACK_V2_REGIME_GATED_BASELINE,
version 1, OFFLINE_DETERMINISTIC, par composition des 12 modules existants.
REAL_DATA_ACCESS, OOS_ACCESS, REPLAY, BROKER_ACCESS, PAPER_TRADING et
PARAMETER_OPTIMIZATION=FORBIDDEN. Aucun changement métier implicite autorisé.
Le critère explicite impose une gate pending si deux opportunités actionnables
concurrentes restent possibles avant l'ouverture d'une position.

Verdict : EMA_PULLBACK_V2_FORMALIZATION=BLOCKED_HUMAN_GATE ;
NEXT=EMA_PULLBACK_V2_PENDING_OPPORTUNITY_POLICY_REQUIRED.
EMA_PULLBACK_V2_REGIME_GATED demeure PRE_FORMALIZATION. Ni
FORMALIZED_PRE_REPLAY, ni DEVELOPMENT_PROTOCOL_REQUIRED ne sont atteints.

Contre-exemple causal synthétique composé avec les vraies gates : impulsion
A à Close[32], pullback A consommé à Close[33], confirmation A attendue.
À Close[34], A échoue sur le prix et reste AWAITING ; une vraie nouvelle
impulsion B crée un contexte ACTIVE, la position étant FLAT. À Close[35],
le pullback B consomme son contexte avant la confirmation finale de A.
A confirme réellement sur 35, stop connu, risque APPROVE/2 contrats,
PENDING_NEXT_BAR_OPEN attendu sur 36 ; B reste AWAITING_CONFIRMATION
avec candidats 36/37. Deux sources distinctes et deux chaînes vivantes.
Le même scénario existe symétriquement en SHORT, sans mock de prédicat
ni record d'événement/pullback/confirmation/risque fabriqué.

Le contexte consommé A est irréversible mais sa confirmation conserve son
snapshot indépendant. La règle same-direction/no-refresh porte seulement
sur ACTIVE. PR #294 bloque les nouveaux événements quand la position est
OPEN, pas lorsqu'elle est FLAT avec une chaîne pending. Les registres
dédupliquent par source ; aucune politique pending de série n'est définie.

B n'est pas de la télémétrie seulement : valeur Open[36]=None dans toutes
les vues de la même observation => exécution A FAILED_INVALID_EXECUTION_INPUT,
aucune position. B échoue sur 36, confirme sur 37, stop/risque APPROVE,
fill réel synthétique sur Open[38]. En variante avec A remplie sur 36,
B est rejetée POSITION_ALREADY_OPEN si A reste ouverte ; si le stop A
ferme intrabar sur 36, B est rejetée INVALID_POSITION_POLICY_INPUT car son
événement 34 précède cette sortie 36. Aucun ancien contexte restauré.

Invariant temporel vérifié séparément : consommation A à kA, première
nouvelle source B au plus tôt kA+1, pullback B au plus tôt kA+2 ;
qA<=kA+2 et qB>=kB+1>=kA+3. Les deux confirmations ne peuvent donc
viser le même Open dans cette séquence causale. Open de A est traité
avant le premier Close candidat de B. L'audit ne revendique aucune collision
simultanée de fills ; le critère humain supplémentaire d'une politique
pour les chaînes concurrentes avant fill reste non satisfait.

Snapshot canonique docs/evidence/EMA_PULLBACK_V2_FROZEN_COMPONENTS_AUDIT_MANIFEST.json,
SHA-256 `82694c53879a145024b288a53649179bb6484b10757882c8955700bfbe1f4ef6`.
12 noms/SHA-256 et 80 constantes publiques issus des modules importés,
id/version/MNQ/1 minute, entry/stop/exit/risk/cost semantics, interdictions
et absences TP/BE/trailing/time/session. Fractions exactes, Decimal en
chaîne et durées en microsecondes ; UTF-8, clés triées, séparateurs compacts,
LF final. Rôle FROZEN_COMPONENT_SNAPSHOT_NOT_APPROVED_STRATEGY ; statut
BLOCKED_HUMAN_GATE, pending_opportunity_policy=UNRESOLVED. Le manifest final
approuvé et le hash futur de protocole restent à établir après la gate.

Nouveaux tests tests/unit/trading/test_ema_pullback_v2_pending_opportunity_audit.py,
SHA-256 `636378c313419224897de94503e8b8209e64023967ad9feaae2e606c80c2a568`.
13 tests PASS en 0.51s : scénarios LONG/SHORT exécutés deux fois depuis
des états neufs, égalité structurelle et des octets canoniques, sources,
provenance, décisions, quantités, stops et fills identiques. Futur indisponible
sans effet, terminal REJECT non réactivé, duplicate evaluation/fill sans
doublon et hash manifest stable. 1724 tests V2 PASS en 6.43s.
8008 régressions locales PASS en 146.12s, 4 avertissements préexistants ;
hors test_mcp.py (blocage sandbox préexistant), inclus dans la CI intégrale.
Ruff, format, compilation et diff-check PASS ; CI intégrale verte exigée
sur le head exact avant publication fusionnée des preuves. Quatre fichiers :
tests d'audit, snapshot JSON, charte et checkpoint. Les 12 modules runtime
sont byte-identiques au parent ; aucun test antérieur ni seuil/règle modifié.
Aucun orchestrateur choisissant A/B, replay, accès data/dataset réel, OOS,
paper trading, optimisation MNQ, broker ou ordre réel. Rentabilité non évaluée.
Les autres scénarios obligatoires end-to-end et fins de données restent
à valider après résolution de cette gate ; tests verts de l'audit != PASS
de formalisation complète.

Décision métier nécessaire : figer le traitement d'un nouvel événement,
contexte ou pullback lorsque la série possède déjà une confirmation ou
une exécution next-Open en attente. Aucune priorité first/latest/LONG/SHORT/
momentum sélectionnée. Reprendre ensuite l'assemblage complet, sans replay.

## EMA_PULLBACK_V2_PENDING_OPPORTUNITY_POLICY — gate définie

Le 2026-10-05, le propriétaire fixe FIRST_CONSUMED_PULLBACK_LOCKS,
MAX_ACTIONABLE_PENDING_OPPORTUNITIES_PER_SERIES=1, sans queue, remplacement,
annulation par événement opposé ni refresh same-direction. Scope : une instance
de stratégie et une série. Aucun scoring ou priorité LONG/SHORT/famille.
La décision est pré-replay, non optimisée et indépendante de V1/V1A/V1B.

La PR #298 a intégré le contre-exemple sur head
7b4263cfd7abc8b6d0ae2e7a64ceec6681d35515, CI #278/run 37367147931 success,
merge 6b8b3513c9850bae1210e32634e37b7f50dde74a,
arbre ec3dda928a6a2566f3a88953d762c614566f1e49.
Les preuves historiques BLOCKED restent conservées ci-dessus ; cette nouvelle
gate résout leur ambiguïté, sans invalider l'audit des composants seuls.

Module ajouté : src/agicore/trading/ema_pullback_pending_opportunity_policy_v2.py.
Tests : tests/unit/trading/test_ema_pullback_pending_opportunity_policy_v2.py.
SHA-256 module : ac5530a32df90076d4266a3495d3d60c9fcb99d90f1c4ec0af5e90413a8a8037.
SHA-256 tests : 367b47771d9df64a9cc9143a93cf78611a67af182bf190d54b7631607196e9f7.
Seuls ces deux fichiers, la charte et ce checkpoint changent. Les douze
modules antérieurs, l'audit PR #298 et son manifest sont inchangés.

IDLE avant un pullback formel CONSUMED. À Close[k], acquisition immédiate
et unique -> AWAITING_CONFIRMATION. Résolution pending avant événements bruts.
k+1 FAIL garde le verrou ; expiration normale ou Risk REJECT le libère
avant l'admission du nouvel événement de cette même Close. APPROVE fige
quantité/source et garde PENDING_ENTRY_EXECUTION jusqu'au prochain Open.
Les événements pendant le verrou sont SUPPRESSED_PENDING_OPPORTUNITY,
avec métadonnées minimales complètes, sans contexte/pullback/confirmation B.
Même direction, direction opposée et composition AMBIGUOUS ne changent A.

FILLED -> transfert atomique au livre de position, zéro opportunité pending.
BREACHED_AT_ENTRY_OPEN -> entrée réelle puis stop réel au même Open,
FLAT avant Close[e], nouvelle source courante admissible. Les expirations
normales d'exécution libèrent ; les erreurs structurelles/non causales et
les états FAILED restent fail-closed avec leurs preuves, sans déverrouillage
silencieux. Aucun ancien signal supprimé ou source terminale restauré.

Le scénario PR #298 est repris avec ses vrais événements et gates : A consomme
à Close[33] ; B est supprimé à Close[34] ; à Close[35], A est approuvé pour
deux MNQ et attend Open[36], sans contexte ni chaîne B. Miroir SHORT identique.
Un fournisseur d'événements différé prouve l'ordre confirmation/stop/risque
avant composition/admission brute. Tous les calculs restent délégués.

64 nouveaux tests PASS en 1.43s. Les scénarios causaux comparés depuis
des états neufs sont identiques structurellement et en octets canoniques.
1788 tests V2 PASS en 6.67s ; 8072 régressions locales PASS en 139.64s,
4 avertissements SQLAlchemy/Python 3.12 préexistants. Hors test_mcp.py
(blocage local préexistant), inclus dans la CI intégrale avant fusion.
Ruff/format PASS ; CI intégrale exigée sur le head exact avant fusion.

Après fusion : EMA_PULLBACK_V2_PENDING_OPPORTUNITY_POLICY=PASS ;
NEXT=EMA_PULLBACK_V2_FORMALIZATION_REQUIRED. Reprendre les scénarios synthétiques
end-to-end et toutes les terminaisons depuis l'audit. PRE_FORMALIZATION reste
le statut V2 ; aucun FORMALIZED_PRE_REPLAY ou DEVELOPMENT_PROTOCOL_REQUIRED
avant cette certification complète. Le manifest d'audit garde le rôle
FROZEN_COMPONENT_SNAPSHOT_NOT_APPROVED_STRATEGY et son SHA-256 inchangé
82694c53879a145024b288a53649179bb6484b10757882c8955700bfbe1f4ef6.
Un nouveau manifest approuvé avec son propre hash suivra seulement un PASS
complet. Aucun replay, accès data/dataset réel, OOS, optimisation, paper,
broker, ordre réel ni mesure de rentabilité.

## V2 — formalisation end-to-end après résolution du verrou pending

EMA_PULLBACK_V2_PENDING_OPPORTUNITY_POLICY intégré par PR #299 : head
ba2f0b40e2e759e505de0ca3a1499b4a85917a85, CI #280 / run 37373397201
success, tous jobs/étapes terminés ; 8076 tests, 5 avertissements en 129.19s.
Merge 92964a2614682f4d16caf467a1429ca51bc67e37, arbre testé
576bacd97774e3cb13d6524800260f11d58bc552 vérifié byte-identique et main propre.
Le blocage PR #298 reste une preuve historique ; la gate pending le résout.

EMA_PULLBACK_V2_FORMALIZATION=PASS ;
EMA_PULLBACK_V2_REGIME_GATED=FORMALIZED_PRE_REPLAY après CI complète verte
sur le head exact de cette phase et fusion. NEXT=
EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL_REQUIRED. Ni protocole réel ni replay
ne sont lancés dans cette phase.

Assemblage ajouté : src/agicore/trading/ema_pullback_regime_gated_baseline_v2.py.
Treize gates importées et composées, douze modules initiaux plus pending,
tous byte-identiques à la base fusionnée. Aucun calcul de prédicat, EMA,
MACD, stop, risque, quantité, coût ou fill dupliqué ; aucun seuil/période/
délai/multiplicateur/priorité modifié. MODE=OFFLINE_DETERMINISTIC,
INPUT_DOMAIN=SYNTHETIC_ONLY ; aucun loader de données, moteur de replay,
broker, ordre réel, paper trading ou dépendance réseau ajouté.

Open : exécution de l'unique source approuvée, bind du stop déjà connu,
breach immédiat, puis stop gap avant sortie EMA pending. Seuls index,
timestamp et Open sont lus. L'extrême adverse OHLC est fourni à la phase
complétée ; la gate de sortie native résout le stop intrabar avant la
position finale et le signal Close/EMA. Aucun horaire intrabar inventé.
Ensuite pending confirmation/stop/risque précède le fournisseur brut et
l'admission contextuelle, conformément à la décision pending. Les règles
de durée de vie/consommation sont exclusivement celles des gates natives.

Le scénario causal PR #298 est devenu impossible : A consomme Close[33],
B est seulement SUPPRESSED_PENDING_OPPORTUNITY à Close[34], A est confirmé
et approuvé à Close[35] avec une seule exécution pending Open[36]. Pas de
contexte B, pas de seconde consommation, pas de queue ; invariants vérifiés
après chaque phase des parcours LONG/SHORT. Une entrée FILLED transfère
atomiquement à la position ; breach conserve ses deux fills et leurs coûts.
Après sortie, seule une nouvelle source peut créer une nouvelle chaîne.

Double événement natif sur une même Close : impossible avec ces gates.
Directions opposées : leurs exigences strictes de couleur du corps sur la
bougie événement se contredisent. Même direction : le rejet t=r-1 balaie
strictement Low/High des cinq précédentes, ce qui contredit les Low non
décroissants / High non croissants de l'émergence impulsive r-3...r-1.
Cette impossibilité est testée sans forger d'événements métier complets.
Les contrats défensifs double même sens et AMBIGUOUS sont testés séparément
sur le compositeur natif ; les suppressions/invalidation demeurent couvertes
par les tests de gates. Aucune nouvelle priorité stratégique implicite.

Fin réelle de données : contexte ACTIVE -> EXPIRED_END_OF_DATA,
confirmation attendue -> TERMINAL_INCOMPLETE_CONFIRMATION,
entrée pending -> EXPIRED_NO_EXECUTION, sortie EMA pending ->
EXPIRED_NO_EXIT_EXECUTION, position encore ouverte -> OPEN_UNREALIZED.
Livres scellés et idempotents ; aucun fill final, liquidation Close,
stop synthétique, restauration de source ou report vers une autre série.
Les erreurs structurelles/non causales restent fail-closed.

Positions finales : native position + native TradeCostRecord, provenance
complète depuis régime/pullback/confirmation/stop/risque/entrée/sortie,
quantité approuvée, fills base/effectifs distincts, frais, gross et net exacts.
Le PnL provient uniquement de la gate de coûts ; slippage une seule fois.
Entrée encore ouverte : frais réels d'entrée, PnL réalisé absent.
BREACHED_AT_ENTRY_OPEN : -2.02 USD par contrat, -4.04 pour deux, sans
annulation de l'entrée ni fill favorable au niveau stale du stop.

Nouveau manifest canonique :
docs/evidence/EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json.
Rôle CANONICAL_PRE_REPLAY_STRATEGY, version 1, MNQ / 1 minute,
13 noms/hashes de sources, 86 constantes exactes exportées, hash de
l'assemblage, sémantiques entry/stop/exit/risk/cost/pending et interdictions.
TAKE_PROFIT/BREAKEVEN/TRAILING_STOP/TIME_EXIT/SESSION_EXIT=NONE.
UTF-8 JSON canonique trié compact + LF ; SHA-256 immuable à référencer
exactement dans le futur protocole DEVELOPMENT :
965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a.
Son approbation dépend de la CI intégrale du head exact et de la fusion ;
ses octets ne changent pas à l'approbation. Le manifest historique conserve
FROZEN_COMPONENT_SNAPSHOT_NOT_APPROVED_STRATEGY et SHA
82694c53879a145024b288a53649179bb6484b10757882c8955700bfbe1f4ef6.

98 tests end-to-end PASS en 7.93s, comprenant 25 scénarios natifs dans
les deux directions, exécutés au moins deux fois depuis des états neufs,
snapshots canoniques complets identiques, ainsi que les contrats défensifs
de composition. Parcours impulsion/reversal, 1/2 contrats/REJECT, stops,
priorités, admissions après sortie, expirations/EOF, symétrie, doublons,
Open sans accès OHLCV futur, mutation future, causalité des étapes et
provenance complète. 1886 tests V2 PASS en 13.91s ; 8170 régressions locales
PASS en 140.92s, quatre avertissements SQLAlchemy/Python 3.12 préexistants.
Seul test_mcp.py reste exclu localement pour son blocage préexistant ; il
est inclus dans la CI intégrale exigée sur le head exact avant fusion.
Ruff/format/compilation PASS, treize composants et manifest d'audit inchangés.
SHA source assemblage : 28470b4275e889b753f3e478439fa7d5e46bf0ff394df23ba10eb8cdc29dbb76.
SHA nouveaux tests : 231c361a4586e543c02499a5b86ec2e5542d89dfe3d79431d926a33ef4cdf2d7.

Aucune donnée réelle ni résultat V2 observé ; aucun accès data/, OOS,
MNQ 03-26/MNQ 06-26, optimisation ou réglage d'après V1/V1A/V1B.
Les valeurs PnL citées sont des assertions sur prix inventés, pas une mesure
de performance. La prochaine gate choisira séparément un nouveau dataset
DEVELOPMENT et préengagera mesures/GO-NO_GO avant toute donnée réelle.

## V2 — protocole DEVELOPMENT préengagé, sans replay

Formalisation précédente intégrée par PR #300 : head
5a57458441357a303b2b14875a2f43a7cc345b6b, CI #282 / run 37376975961
success, 8174 tests et cinq avertissements en 133.29s. Merge
ffa4f13dd01f4870462c4e71aa0f3dd35f77f61a, arbre testé
43560b62785c8ceebf952952cf44af4287063883. Base de cette phase vérifiée propre.

EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL=PASS après CI intégrale verte sur
le head exact et fusion ; NEXT=
EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED. Aucun replay,
aucun dataset canonique ni validation de performance V2 dans cette phase.

Protocole canonique docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json,
UTF-8 compact, tri récursif et LF final ; DEVELOPMENT_PROTOCOL_SHA256 :
68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402.
Document compagnon Markdown et outil tools/ema_pullback_v2_development_protocol.py.
Le digest reste hors du payload hashé, épinglé dans le Markdown et l'outil.
Manifest de stratégie autorisé, immuable et byte-identique à la base :
965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a.
Tous les modules trading restent inchangés. Hash incorrect = FAIL_CLOSED.

Sélection préengagée sur expiration décroissante des contrats MNQ trimestriels
terminés admissibles, 1 Minute / Last / DoNotMerge / CME US Index Futures ETH.
MNQ 06-26 et MNQ 03-26 interdits ; MNQ 09-26 seulement candidat attendu,
filiation NOT_EVALUATED. Aucun RAW lu/acquis, aucune preuve inventée, aucun
résultat/graphique inspecté. Contamination V2 prouvée -> rejet et même règle
sur le suivant. UNKNOWN ne devient jamais admissible par défaut.
Rôle unique EXPOSED_DEVELOPMENT, irréversible au premier futur replay.

Seuils NET après coûts V2 : 100 trades, +200 USD, PF 1.15, marked DD <=750 USD,
loss streak <=8. Trois tiers chronologiques de temps écoulé ; frontières
rationnelles de microsecondes connues avant résultats, attribution par fill
de sortie. Minimum 15 trades chacun, deux segments net strictement positifs,
PF >=0.80 et net >=-200 USD chacun. Aucun trade-count/PnL-based découpage.

Outil pur hors runtime : vérification des deux documents et quatre hashes
de run, sélection de métadonnées déclarées et screening exact Fraction.
PF sans pertes avec gains = POSITIVE_INFINITY sérialisable ; sans gains =0.
Trade net nul remet la loss streak à zéro. Mark requis à chaque Close réel,
realized net réconcilié aux trades clôturés, plus unrealized de la position
ouverte depuis l'entrée effective et son frais déjà payé. Aucun coût de
sortie hypothétique ni liquidation finale. Initial equity=0 ; peak-to-trough
marked drawdown exact, sans arrondi. Aucun prix OHLCV ni indicateur recalculé.

RESULT_SCHEMA complet préengagé : comptes de toutes les étapes/quantités,
LONG/SHORT, types de sortie, coûts distincts, net, statistiques, segments,
marks, provenance et états terminaux. Frais clôturés/entrée ouverte séparés,
slippage diagnostique jamais soustrait une seconde fois. Trades par jour/session
diagnostiques seulement. La fonction de screening retourne un résumé et
ne prétend pas produire un résultat de replay complet.

INSUFFICIENT_SAMPLE prioritaire -> SAMPLE_EXTENSION_REQUIRED, ni GO ni NO_GO.
Échantillon suffisant + tous critères -> GO_TO_INDEPENDENT_VALIDATION ;
sinon NO_GO_BASELINE. Stratégie/seuils inchangés dans tous les cas ; aucune
optimisation automatique. Une variante exige une nouvelle hypothèse explicite
et son propre préengagement avant ses résultats.

Futur run ONCE seulement après protocole PASS, filiation PASS et gate séparée,
identité immutable strategy/protocol/RAW/runner SHA-256 enregistrée avant
exécution. Rerun uniquement pour mêmes inputs/code/output hashes, sans remplacer
le verdict original. Validation indépendante non sélectionnée, scellée jusqu'à GO.

71 tests synthétiques ciblés PASS en 0.68s : frontières inclusives/strictes,
insuffisance prioritaire, stabilité des tiers exacts, PF infini, zéro/reset,
marked equity, open final sans clôture, hashes/rôles refusés, contamination,
couverture/réconciliation et rerun/déterminisme/immutabilité sans I/O.
Régression locale : 8241 PASS, quatre avertissements préexistants en 188.53s.
Seul tests/unit/test_mcp.py exclu localement pour blocage de ports préexistant ;
ses quatre tests restent inclus dans la CI intégrale requise avant fusion.
Ruff, format, compilation et diff-check PASS. Périmètre de cinq fichiers.
Aucun accès données réelles/OOS, broker, paper trading, replay, optimisation,
ni résultat V2. Preuves du head exact et CI intégrale conservées dans la PR.

## V2 — gate de filiation DEVELOPMENT bloquée avant lecture RAW

Protocole intégré par PR #301, merge 547bdf60c5c71d67abbbe490b35c2f36d7d7354a,
arbre 50f31d4ba6b390fcbde801b220dae05529f092fa ; CI #284 / run 37501047898
success, 8245 tests et cinq avertissements en 146.21s. Les bindings recalculés
restent exacts : manifest stratégie 965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a,
protocole 68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402.

EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE=BLOCKED_HUMAN_GATE ;
CANONICAL_DATASET_ID=NONE ; SOURCE_RAW_SHA256=NONE ;
REAL_STRATEGY_REPLAY=NOT_EXECUTED. Aucun RAW acquis/ouvert/hashé.
Le rapport JSON canonique de blocage et son Markdown sont dans docs/evidence/.
DATASET_LINEAGE_MANIFEST_SHA256 :
e4b3936d45c07f341370847f04fc577f2e55f8d2ae9cdfabb7196342ac443081.
Ce hash identifie un audit BLOCKED, jamais un dataset approuvé ni une autorisation.
Le reçu séparé fourni est uniquement un TEMPLATE_NOT_EVIDENCE, champs observés null.

Recherche des fichiers texte suivis et des diffs dans les refs Git locaux
disponibles : quatre références procédurales au candidat et deux commits du
protocole sans replay, aucun usage de performance trouvé dans le scope inspecté.
Preuve partielle seulement : aucun usage externe ne peut être déduit de GitHub.
Les deux attestations humaines explicites sont reçues par déclaration de
l'utilisateur à 2026-10-06T20:17:06+02:00 / 18:17:06Z. Preuve textuelle
EMA_PULLBACK_V2_DEVELOPMENT_DATASET_HUMAN_ATTESTATION.json, SHA-256 :
395b1f96429da11604248d0760fe6fc71e88acfa8c9b55aa7e9d078f0ba6a264.
Les deux champs portent RECEIVED_EXPLICIT et leurs blocages sont retirés ;
les cinq autres blocages demeurent. Aucun reçu d'export n'est créé à partir
de cette déclaration. Le rapport précédent ae8b9a6a...dda8d6 demeure traçable
via previous_lineage_manifest_sha256. PR #302 intégrée par merge
60d86bd437f54a08f4ba7a20070a6cbeaa48ab99, CI #286 / run 37506050324
success : 8245 tests, cinq avertissements, 148.58s.

Preuve Windows/filesystem additionnelle reçue à 2026-10-06T21:55:55+02:00 :
parent déclaré immuable, SHA-256
fa41a98a56956a11ec3b2249eb579a699db7989378d06f971d22fa014cf277ad,
taille 4724667 octets. Windows=Romance Standard Time, base=+01:00,
SupportsDaylightSavingTime=TRUE ; horloge observée 21:47:58+02:00.
LastWriteTime parent=21:36:45+02:00 / 19:36:45Z le même jour sur la même
machine. Approximation filesystem du moment d'export, pas un horodatage
natif NinjaTrader ; conversion par l'offset observé +02:00, jamais +01:00.
Preuve EMA_PULLBACK_V2_DEVELOPMENT_DATASET_PARENT_RAW_TIMEZONE_EVIDENCE.json,
SHA-256 37054e14f402a164b2205e9d25f2fe7e77858f3d945cc7c8e552dd98feaf2f46.
Identité parent USER_DECLARED_NOT_LOCALLY_RECOMPUTED, zéro octet RAW lu.
Aucun fuseau/sémantique des barres ou calendrier de session n'est inféré.
Les cinq blocages restent ouverts ; le modèle de reçu vide est inchangé.
Révisions de manifest précédentes conservées ; attestation inchangée.
PR #303 intégrée par merge 08472f763309ccca9de7e57624960ed3f2607c9f,
CI #288 / run 37510820582 success : 8245 tests, cinq avertissements, 143.80s.

Métadonnées CME consultées sans prix : échéance précédente 18 juin 2026
(Juneteenth le lendemain), échéance candidat 18 septembre 2026 à 08:30 Chicago
/ 13:30 UTC. Le candidat est terminé au 6 octobre. L'OPEN précis de la première
session MNQ après l'échéance précédente n'est pas prouvé dans la table produit
Juneteenth récupérée ; la période canonique reste non fixée avant les prix.
Les rolls usuels CME ne remplacent pas la convention post-expiration demandée.

Autres preuves manquantes : les octets MNQ 09-26.Last.txt et la vérification
locale du SHA/taille parent déclarés,
reçu d'export contemporain complet, paramètres observés et chaîne fournisseur,
version NinjaTrader, timestamps/fuseaux/DST, puis tous les contrôles d'intégrité
RAW. Last / 1 Minute / DoNotMerge / CME US Index Futures ETH restent prescrits ;
aucun Bid/Ask nécessaire. MNQ 06-26 et MNQ 03-26 restent exclus.
Aucune transformation, bougie synthétique, donnée OOS, module stratégique,
trade counting, PnL, optimisation ou replay. Reaction Engine reste rouge.
Validation locale : 17 tests du contrat de filiation sur métadonnées synthétiques
PASS en 0.15s ; sérialisation/hash rejoués deux fois, champs null et absence de
canonisation vérifiés, quatre documents uniquement et diff-check PASS.

NEXT=EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED, reprise de la même
gate avec preuves ; après PASS seulement DEVELOPMENT_REPLAY_IMPLEMENTATION_REQUIRED.
Une transformation nécessaire ouvrirait DATASET_TRANSFORMATION_REQUIRED séparément.

## V2 — nouveau parent complet déclaré, vérification bloquée faute d'upload

Reçu conversationnel du 2026-10-08T22:20:37+02:00 / 20:20:37Z.
UI déclarée : MNQ 09-26, dates demandées 2026-06-01..2026-09-18,
Minute / Last, succès TRUE ; valeur numérique de l'intervalle non fournie.
Nouveau parent MNQ 09-26.Last.txt, taille 5416523 octets, SHA déclaré
6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5.
CreationTime=22:14:07+02:00 / 20:14:07Z ; LastWriteTime=22:14:09+02:00 /
20:14:09Z. Preuves filesystem seulement, jamais horodatage natif NinjaTrader.
ROLE=FULL_PARENT_RAW_PENDING_BYTE_VERIFICATION.
Preuve EMA_PULLBACK_V2_DEVELOPMENT_DATASET_FULL_PARENT_RAW_EXPORT_EVIDENCE.json, SHA-256
a8b2189505c327882d6a4596c38d8d0e9ae80305f6d1b816c68345f4bbd37a64.

Aucun upload de cette taille n'est accessible : le candidat récent
MNQ 09-26.Last(5).txt fait 691856 octets ; le nom exact ancien fait
367982 octets. Inventaire de métadonnées uniquement, aucune acquisition ni
lecture de RAW alternatif. SHA local du nouveau parent, lignes, bornes,
ordre/doublons, OHLC, volume entier, grille 0.25, gaps, couverture de
terminaison et barres post-terminaison sont tous NOT_EVALUATED.

La preuve immuable du parent précédent fa41a98a...277ad / 4724667 octets
reste intégrale ; aucune substitution, transformation ou filiation entre
ces deux exports n'est inventée. La période demandée du parent large ne
remplace pas la fenêtre canonique ; celle-ci reste non résolue. Les
paramètres fournisseur/NT/version/session/fuseau/merge doivent encore
être établis pour ce nouvel export.

EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE=BLOCKED_HUMAN_GATE ;
CANONICAL_DATASET_ID=NONE ; SOURCE_RAW_SHA256=NONE ;
DATASET_LINEAGE_MANIFEST_SHA256=e4b3936d45c07f341370847f04fc577f2e55f8d2ae9cdfabb7196342ac443081.
NEXT=EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED.
Les cinq blocages restent ouverts. Aucun signal V2, trade, PnL, replay,
optimisation, OOS ou broker. Aucun octet utilisateur modifié ; aucun
module métier, stratégie ou protocole modifié. Le modèle de reçu demeure
vide et l'attestation humaine déjà reçue reste valable et inchangée.

PR #304 du volet Windows précédent intégrée par merge
61a081d5e1ed9f4173735e6d54a20f600b8e02ec, arbre abaed930623232baa736e043fa9e0c82af42a8d6 ;
CI #290 / run 37523466761 success : 8245 tests, cinq avertissements, 138.43s.

## V2 — préengagement de transformation temporelle, sans exécution réelle

Mission explicite du 2026-10-09T12:27:28+02:00 / 10:27:28Z.
FULL_PARENT_RAW joint et vérifié en lecture seule : SHA
6e20320e06184673c745c1069753c77151fdccd4505b863210f6d63f3ff5fcd5,
5416523 octets, 101962 lignes, bornes UTC 2026-06-07T22:01:00Z /
2026-09-18T13:31:00Z. Tous les compteurs structurels à zéro. 326 intervalles
avec gap > une minute, jamais remplis ni utilisés comme filtre.

Mission : RAW=NINJATRADER_END_OF_BAR, timezone=UTC ; session canonique
2026-06-18T22:00:00Z ; garder uniquement timestamp >= 2026-06-18T22:01:00Z
ET timestamp <= 2026-09-18T13:30:00Z. Aucun autre prédicat. Partition auditée :
12120 avant, 89841 dans la fenêtre, 1 après. Pas de RAW dérivé construit.
L'ancien rapport de filiation e4b3936d...443081 est un snapshot historique
BLOCKED ; le nouveau protocole porte la preuve d'identité et d'intégrité
courante. L'ancienne preuve parent fa41a98a...277ad reste inchangée.

EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION=PASS_PRECOMMITTED.
Protocole docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION.json,
SHA-256 bb47e6a9b867dd6e35516f5c43e56b9259aa00c526deb4978b050783a1e47f62.
Source tools/ema_pullback_v2_dataset_transformation.py,
SHA-256 3ec9aadf9e4852d1ad4ef10ad6fd3f958d716a9de5df792a744c6926cf26d44c. Manifest stratégie et protocole DEVELOPMENT inchangés.
Implémentation sous tools/, aucun core métier modifié. Validation globale
fail-closed avant sélection ; lignes retenues octet pour octet, fins de
ligne incluses. CLI par défaut vérifie uniquement les documents ; le flag
--execute ne peut être utilisé que dans la gate d'exécution séparée.

REAL_PARENT_TRANSFORMATION=NOT_EXECUTED ; REAL_STRATEGY_REPLAY=NOT_EXECUTED.
DERIVED_RAW_SHA256=NONE ; CANONICAL_DATASET_ID=NONE.
DATASET_LINEAGE reste BLOCKED_HUMAN_GATE pour les autres preuves de
provenance et celles du dérivé futur ; ce préengagement ne canonise rien.
NEXT=EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION_REQUIRED.
Aucun signal V2, trade, PnL, replay, optimisation, OOS ou broker.
Le filtre n'est pas automatiquement exécuté après fusion.

## Exécution unique du filtre temporel DEVELOPMENT V2 — 2026-10-09

Autorisation explicite AGIcoreManager reçue à 10:57:20Z. Commande préengagée
PR #306 invoquée une fois à 2026-10-09T11:01:36.680914Z, terminée
à 2026-10-09T11:01:38.754119Z, code 0 et stderr vide.
EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION = PASS.
REAL_PARENT_TRANSFORMATION = EXECUTED_ONCE ; REAL_STRATEGY_REPLAY = NOT_EXECUTED.

Parent 6e20320e...5fcd5 inchangé : 5 416 523 octets, 101 962 lignes.
Partition : 12 120 avant, 89 841 retenues, 1 après ; lignes modifiées = 0.
Dérivé MNQ_09-26_DEVELOPMENT_CANONICAL_V1.Last.txt : 4 785 270 octets,
89 841 lignes, SHA-256 ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126.
Bornes UTC End-of-Bar : 2026-06-18T22:01:00Z / 2026-09-18T13:30:00Z.
Chaque ligne retenue est byte-identical à la ligne parent, fin de ligne incluse.
Audit indépendant sans import transformation/V2 : tous les compteurs d’erreur
nuls, 71 gaps réels préservés ; classification finale réservée à la filiation.

Reçu canonique docs/evidence/EMA_PULLBACK_V2_DEVELOPMENT_DATASET_TRANSFORMATION_EXECUTION.json,
SHA-256 2b4c6b86da5749545a55b6173916a26be88644b252afb9afcaf6f86deb7ccbf1. Il lie commande et stdout exacts,
horloge d’exécution, hashes figés, comptes avant/après et source/résultat de
l’audit indépendant. Aucun RAW versionné ; aucune modification de data/,
manifest stratégie, protocoles ou source de transformation.

Le nom recommandé du dérivé ne canonise pas le dataset.
CANONICAL_DATASET_ID = NONE ; DATASET_LINEAGE = BLOCKED_HUMAN_GATE.
NEXT = EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED.
Aucun signal V2, trade, PnL, replay, screening, optimisation, OOS ou broker.

## Limites du produit

V1_VALIDATED_OFFLINE_PAPER non atteint. D002 prouve le sink mémoire canonique ; les PR #241/#242
et le nouvel audit prouvent la reconstruction et la Gate 5 du profil offline borné, pas le runtime global complet.
SignalLoopOrchestrator et RuntimeEventBridge restent hors garantie durable initiale (D001).
Aucun ancien événement legacy migré implicitement. Aucun accès data/, secret ou broker.
Le CAS protège la publication des journaux, pas l'exécution concurrente d'un callback externe ;
les sinks obligatoires conservent leur propre contrat d'idempotence. Une ancre conservée hors
de la base reste nécessaire pour détecter le rollback cohérent de toute la base SQLite.
Les entrées, la sortie principale EMA20, le modèle d'exécution bar-based, le stop structurel
initial, l'absence explicite de take-profit, breakeven et trailing stop ainsi que la priorité entre
les deux sorties existantes, l'absence de filtre stratégique de session de V1/V1A, le filtre
d'entrée uniquement de V1B et le refus des nouveaux signaux pendant une position ouverte ainsi que
la taille fixe d'un MNQ sont désormais formalisés.
La comptabilité non réalisée, le modèle versionné de coûts et le protocole sont figés. Les replays
DEVELOPMENT uniques de V1, V1A et V1B sont respectivement `NO_GO_BASELINE`, `NO_GO_VARIANT` et
`NO_GO_VARIANT`. La réplication propre MNQ 03-26 de V1B est également `NO_GO_VARIANT` et échoue
matériellement à reproduire l'edge DEVELOPMENT observé sur MNQ 06-26 ; la voie incrémentale V1 est
terminée par décision humaine. V2 est formalisée offline sur données synthétiques,
sans validation de performance et sans autorisation de replay/paper/broker.
Aucune performance indépendante n'est démontrée et l'OOS reste fermé. Cette
stratégie demeure distincte de EMA19/50 V3 rejetée.

Vérification de cette mise à jour du 8 octobre : 17 tests de filiation
PASS en 0.14s ; assertions documentaires et conversions locales/UTC PASS,
sérialisations déterministes identiques, hashes stratégie/protocole
conformes, ancien parent/attestation/modèle inchangés, quatre documents
uniquement, diff-check PASS. Aucun audit des octets RAW n’est annoncé.

Validation locale de ce préengagement : 139 tests ciblés synthétiques/metadata
PASS en 0.61s (51 nouveaux cas, filiation et protocole DEVELOPMENT inclus),
Ruff check/format PASS, vérification CLI des documents sans RAW PASS,
sérialisation et hashes conformes, périmètre de cinq fichiers et diff-check
PASS. Aucune transformation réelle exécutée. La CI complète est requise
avant fusion du préengagement.
