# AGIcore current state — checkpoint

Date : 2026-09-19 UTC.
Statut : BLOCKED_HUMAN_GATE — CLEAN_LINEAGE_SOURCE_EVIDENCE ; D003 legacy = BLOCKED_PROVENANCE.
Branche de vérification : feature/post-dataset-lineage-checkpoint-v1.
Base GitHub vérifiée et récupérée : 17c747d005e2b6699b04bc19fe70267dfe5a2557.

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

Action unique de la gate CLEAN_LINEAGE_SOURCE_EVIDENCE : fournir le dossier technique assaini
d'un nouvel export MNQ destiné à DEVELOPMENT — source/fournisseur, logiciel/version, date UTC,
contract_id et preuve d'identité hashée, intervalle, timestamp/fuseau/DST, rollover, OHLCV/volume,
sessions/jours fériés, nom/hash source et transformation/parent. Les octets de marché restent privés ;
les valeurs UNKNOWN ne sont pas acceptées. Ne pas ouvrir, déplacer ni reclasser l'OOS.

## Limites du produit

V1_VALIDATED_OFFLINE_PAPER non atteint. D002 prouve le sink mémoire canonique ; les PR #241/#242
et le nouvel audit prouvent la reconstruction et la Gate 5 du profil offline borné, pas le runtime global complet.
SignalLoopOrchestrator et RuntimeEventBridge restent hors garantie durable initiale (D001).
Aucun ancien événement legacy migré implicitement. Aucun accès data/, secret ou broker.
Le CAS protège la publication des journaux, pas l'exécution concurrente d'un callback externe ;
les sinks obligatoires conservent leur propre contrat d'idempotence. Une ancre conservée hors
de la base reste nécessaire pour détecter le rollback cohérent de toute la base SQLite.
La stratégie EMA pullback personnelle (pente, MACD, sortie clôture sous EMA20) reste
à formaliser puis évaluer ; elle est distincte de EMA19/50 V3 rejetée.
