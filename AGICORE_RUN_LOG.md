# AGIcore run log

## 2026-09-12 — Reprise AGIcoreManager / audit SINK-B3

- Lecture AGENTS.md, CLAUDE.md, docs/command-center/PROJECT_STATUS.md et ROADMAP.md.
- Git fetch origin main : FETCH_HEAD c1316a06efabb1ee9688bfd433f9df67c46cc47b.
  origin/main absent dans ce checkout : usage du SHA FETCH_HEAD vérifié, sans supposer une ref.
- GitHub : quatre fichiers de pilotage absents (404) ; aucune PR ouverte ; CI main #159 success.
- Inspection de core/events.py, l4_planning/runtime.py, agents/execution_agent.py,
  l5_action/execution_outbox.py, l2_memory/models/event.py,
  repositories/event_delivery_repository.py et services/idempotent_memory_delivery_handler.py.
- Ancien exécutable pytest inutilisable (interpréteur disparu). Reprise avec Python 3.12 courant
  et les dépendances déjà disponibles via PYTHONPATH ; aucune installation ni secret.
- Commande : PYTHONPATH=src:<environnement-existant>/lib/python3.12/site-packages python -m pytest -q
  tests/unit/core/test_event_delivery_contracts.py
  tests/unit/l2_memory/test_event_delivery_repository.py
  tests/unit/l2_memory/test_idempotent_memory_delivery_handler.py
  tests/unit/l2_memory/test_event_delivery_migration.py
  tests/unit/l2_memory/test_event_delivery_service.py
  tests/unit/agents/test_execution_agent.py tests/integration/test_execution_agent_runtime.py
  tests/integration/test_event_delivery_authority_restart.py
  tests/integration/test_event_delivery_authority_multiprocess.py
  tests/integration/test_idempotent_memory_effect_restart.py
  tests/integration/test_idempotent_memory_effect_multiprocess.py
- Résultat : 159 passed, 4 warnings in 8.23s. Warnings : adaptateur datetime SQLite déprécié.
- Aucun runtime modifié ; quatre documents initialisés. Checkpoint D001 avant intervention humaine.
- Pas de prix, OOS, NQ, broker, compte ni ordre réel utilisés.

## 2026-09-12 — D001 approuvée / correction D002

- Lecture des quatre fichiers de pilotage ; GitHub main inchangé, #239 non fusionnée, CI #160 verte.
- Approbation utilisateur du profil offline initial enregistrée ; aucun nouveau choix de périmètre.
- Branche feature/post-sink-b3-memory-effect-v1 basée sur le SHA distant de #239 :
  5cff6a22bbd39cc3b0d59425bd78350250c53e57.
- Test avant correction : 1 failed, assertion 3 événements au lieu de 1 (2.47s).
- Correction canonique, effet stable sous contrainte SQL existante ; pas de schéma SQL modifié.
- Test après correction : 21 passed (2.56s), puis ajout conflit SQL et régressions :
  29 passed (3.36s). os._exit(73) injecté après commit réel, processus spawn, référence indépendante.
- Ruff : import du nouveau test corrigé automatiquement. Suite complète lancée.
- Suite complète : 5868 passed, 6 warnings in 68.51s ; dépréciations Starlette/httpx/anyio et SQLite.
- Fixture du nouveau test spawn resserrée sur MNQ seul ; limites synthétiques inchangées.
- Périmètre : 3 fichiers code/tests et 4 checkpoints obligatoires, exception documentée à la taille
  de phase par défaut. Aucun module risque modifié. Test de crash avant correction conservé ci-dessus.
- Examen du prérequis suivant : L5ExecutionTransactionStore et L5ExecutionOutcomeInbox publient
  encore leur état en RAM. Leur restauration doit utiliser les validateurs de replay existants,
  sans reconstruire silencieusement une position à zéro. D002 ne prétend pas résoudre ce point.
- Checkpoint : arrêt pour fusion sensible de D002 après publication et CI, conformément au mandat.

## 2026-09-12 — Audit de reprise vérifié et revue D002

- GitHub PR #238 merged=true, merged_at=2026-09-06T07:17:52Z,
  merge 248d762038164cd6a58842382e06207baf0e63d0, ancêtre de HEAD (exit 0).
- Main distant vérifié : c1316a06efabb1ee9688bfd433f9df67c46cc47b.
- PR #239 ouverte/draft, HEAD 5cff6a22bbd39cc3b0d59425bd78350250c53e57,
  CI #160 success (34679678339). Son texte D001 est historique, pas une annulation
  de l'approbation locale et utilisateur. Aucun changement distant effectué.
- Revue Codex indépendante read-only : aucun défaut bloquant D002 identifié.
- 26 tests ciblés agent/runtime/sink restart : PASS en 2.83s.
- Suite complète relancée : 5868 passed, 6 warnings in 57.23s, exit 0.
- Python 3.12.14 ; pytest 9.1.1. Commande reproductible depuis ce checkout :
  PYTHONPATH=src:/workspace/scratch/d5c5e3a5f9fd/agicore-main-22a/.venv/lib/python3.12/site-packages python -m pytest -o addopts='' -q
- Ruff sur les trois fichiers source/tests D002 : All checks passed.
- git diff --check : PASS. Aucun code D002 modifié pendant cette reprise.
- Audit persistance : _publish_state de L5 et inbox n'écrit qu'en RAM.
  Ticket POST-SINK-B3-L5-RECOVERY-V1 préparé dans AGICORE_DECISIONS.md.
- D001 historique clarifiée ; master plan corrige la mention inexacte de PR D002.
- STOP avant commit conformément à la gate utilisateur ; aucune publication/fusion.
  Demande précise : autoriser le commit local du diff D002 et des quatre checkpoints.
  Push/PR/fusion restent distincts. V1_VALIDATED_OFFLINE_PAPER non atteint.


## 2026-09-12 — D002 intégrée, reprise automatique

- Autorisations utilisateur successives : commit, publication/PR draft, puis ready/merge.
- PR #240 head revérifié 242991685f8f23268a9bc7e0456528afed43dddf, CI #161 success.
- Fusion avec garde expected_head_sha, résultat merged=true :
  d52e9212eadac55e9d3d24482fd744ca54839771.
- Main distant relu via GitHub puis git fetch origin main réussi ; FETCH_HEAD identique.
- Worktree dédié créé sur ce SHA : feature/post-sink-b3-l5-recovery-v1.
- Ticket de reconstruction confié à Codex ; parent supervise preuves et checkpoints.
- D002 n'est pas recommencée. D001 reste approuvée. Aucun autre commit autorisé à ce stade.


## 2026-09-13 — Reprise exacte après PR #240

- GitHub main relu : d52e9212eadac55e9d3d24482fd744ca54839771 ; PR #240 merged=true.
- Checkpoint indiquait encore implémentation ; code local présent en deux nouveaux fichiers,
  sans commit : sqlite_l5_recovery.py et test_sqlite_l5_recovery.py.
- Ancien log ciblé retrouvé : 16 passed in 16.94s. D002 non recommencée.
- Suite avant renforcement des preuves mémoire : 5884 passed, 6 warnings in 79.65s.
  Ce résultat ne valide pas le correctif supplémentaire en cours.
- Revue statique précédente : outcome étranger et ACK forgé désormais refusés avant persist.
- Revue finale a reproduit un défaut supplémentaire : crash after_effect exit73,
  suppression d'une ligne mémoire synthétique, retry exit0 avec ACK et mémoire vide.
  Correction dans le module de récupération : preuve mémoire exacte en lecture seule requise
  à la reprise et avant publication des effets terminés ; preuve EventBus requise même sans ACK.
- Aucun changement ExecutionAgent/D002, Risk Engine, stratégie, OOS ou NinjaTrader.
- Autorisation du 2026-09-13 : implémentation/tests/checkpoints seulement ; STOP avant commit.

## 2026-09-13 — L5 recovery finalisée localement

- Correction de la lacune reproduite : un effet mémoire marqué terminé ne peut plus être repris
  si la ligne SQL D002 exacte (effect_id, payload_hash, payload, métadonnées, timestamp) manque.
- La preuve EventBus exacte est également requise pour un effet bus terminé, même avant ACK.
- Fixture de reprise durcie : elle n'initialise plus silencieusement une base mémoire absente.
- Tests ciblés finaux : 24 passed in 23.27s. Neuf points de crash, nouveaux processus,
  référence indépendante, position MNQ restaurée, retry sans fill supplémentaire, refus risque +2,
  corruption rehashée, stale writer, faux ACK, outcome étranger et autorités incohérentes.
- Handler idempotent mémoire exécuté jusqu'à livraison/émission COMPLETED ; replay après achèvement OK.
- Suite finale sur le même arbre : 5892 passed, 6 warnings in 77.02s (exit 0).
- Warnings : dépréciations Starlette/httpx/anyio et adaptateur datetime SQLite ; aucune erreur.
- Ruff : All checks passed. py_compile et git diff --check : exit 0.
- SHA-256 code : 4e64a636d02a617629a82fffbd0e7c84070b7f9319f948c00205405f3af07701.
- SHA-256 test : 2de24c8930af6a5695fd4a0cdb4715fdbd3fa8d66a385f167d3134d3e1a7f1b6.
- Revue indépendante : outcome étranger et ACK forgé détectés puis corrigés ; CAS/bootstrap relus.
- Sécurité : fichiers Risk/OOS/stratégie/data/NinjaTrader inchangés ; aucun broker, secret ou ordre réel.
- Arrêt obligatoire avant commit. Gate : L5_RECOVERY_COMMIT_AUTHORIZATION.

## 2026-09-13 — Publication et fusion de L5 recovery

- Commit local autorisé et créé : f3a44868523f92c5ef36ad9df50411aec9bba3d9 ; arbre
  e95abdedc2183b22b97d323135db420e17290854 ; worktree propre.
- Push HTTPS exact refusé avant transfert faute d'identifiant Git local. Aucun secret demandé ou exposé.
- Option B autorisée : six blobs recréés via le connecteur GitHub et comparés un à un aux blobs locaux.
  Arbre distant obtenu : e95abdedc2183b22b97d323135db420e17290854, identique à l'arbre testé.
- Commit distant équivalent : b1e5e37080e88f755353bb6cd1f7b5fcf4d26811, parent
  d52e9212eadac55e9d3d24482fd744ca54839771, même message et exactement six fichiers.
- PR #241 créée en brouillon, 892 ajouts et 51 suppressions ; CI AGIcore #163
  (run 34780120469) success, tests et contrôle whitespace réussis.
- Passage Ready autorisé séparément ; PR ouverte, mergeable=true et mergeable_state=clean.
- Fusion autorisée avec expected_head_sha b1e5e37080e88f755353bb6cd1f7b5fcf4d26811.
  Résultat : merged=true, merge 6c3c6bb5299e0fe8ee6db646e94b79fb4bed45df.
- Main distant et FETCH_HEAD vérifiés sur ce merge ; parents d52e9212 et b1e5e370 ; arbre e95abded
  inchangé. Aucun workflow post-fusion distinct déclenché ; la preuve CI est le run PR #163.
- Aucun changement Risk Engine, D002, stratégie, OOS, data/, NinjaTrader, broker ou ordre réel.
- Worktree documentaire créé depuis le merge sur chore/post-l5-recovery-checkpoint-sync.
  STOP avant commit du checkpoint post-fusion.

## 2026-09-13 — Checkpoint #242 intégré et Gate 5 auditée

- PR #242 passée Ready après vérification : head 0c8e895b6563ab4a790891d2d153738b85d8094e,
  base 6c3c6bb5299e0fe8ee6db646e94b79fb4bed45df, mergeable=true/clean.
- CI AGIcore #165 (run 34781880719) : completed/success sur le head exact.
- Fusion protégée par expected_head_sha : merged=true, merge
  d41103265f3afc5e324a01d45dd66b14bea0d148.
- Main distant et FETCH_HEAD vérifiés : même SHA, arbre
  d352e3daf60cae41bfe1935577f60b3b64fb8785, parents 6c3c6bb5 et 0c8e895b.
- Branche feature/gate5-global-offline-replay-v1 créée depuis ce main ; worktree initial propre.
- Audit Gate 5 : le test intégré couvre tous les composants obligatoires du profil offline D001,
  et non RuntimeEngine, SignalLoopOrchestrator ou RuntimeEventBridge, exclus par la décision D001.
- Relance : `tests/integration/test_sqlite_l5_recovery.py` — 24 passed in 30.01s.
- Suite complète de la branche : 5892 passed, 6 warnings in 114.32s ; aucune erreur.
- Preuves mappées : neuf crashes réels ; processus neufs ; position MNQ restaurée ; un seul
  ordre/fill/effet après retries ; refus +2 ; incohérences fail-closed ; journaux et effet mémoire
  identiques à une exécution indépendante de référence.
- Aucun changement runtime nécessaire. Aucun accès `data/`, OOS, secret, broker, compte,
  NinjaTrader ou ordre réel ; Risk Engine et stratégie inchangés.
- Gate 5 : GATE_5_D001_PROFILE_VERIFIED. Prochaine gate : contrat de provenance D003.

## 2026-09-15 — D003_NQ_MNQ_LINEAGE_READONLY

- Reprise depuis main 111c23657a4614c38c73d6bbbd51605c4fec80af, merge PR #243 ; lecture des quatre
  checkpoints et du cadre de confidentialité. Checkout documentaire isolé et propre avant modification.
- D002, SINK-B3 et Gate 5 conservés sans réexécution. Autorisations Git permanentes appliquées.
- Archive existante récupérée dans le périmètre autorisé : SHA-256 conforme à la déclaration ;
  neuf membres, CRC ZIP valides. Aucun nouveau téléchargement de données de marché.
- Audit local sans émission de valeurs de marché : tailles, nombre de lignes et timestamps vérifiés ;
  aucun en-tête dans les neuf membres. Un pas dominant de 60 secondes est observé, sans en déduire un contrat
  de granularité, de timestamp ou de fuseau. Identité réelle de chaque contrat UNKNOWN.
- Disque Windows inaccessible ; extraction antérieure de 83 manifestes retrouvée et analysée,
  sans reconstitution humaine ni prétention de relecture des originaux. 66 run_id distincts ;
  doublons conservés ; neuf champs intégralement UNKNOWN, dont toute la provenance amont.
- 145 manifestes locaux supplémentaires examinés séparément ; zéro correspondance directe avec
  les neuf hashes de membres. Zéro correspondance également dans les 83 enregistrements historiques.
  Les entrées multifichiers restent des listes : aucune association filename/hash inventée.
- Registre historique retrouvé avec le candidat et son hash déclaré ; exposition antérieure consignée.
  Le contrat de session local ne contient pas de liaison par hash aux sources et rapports.
- Manifeste privé : 239 entrées, chacune limitée aux douze champs autorisés ; ordre : 83 historiques,
  145 locales, archive, neuf membres, candidat. Champs de provenance absents UNKNOWN ; l'archive
  n'est pas inventée comme parent_dataset_sha256. Hash du candidat non vérifié donc input_sha256 UNKNOWN.
- Vérifications locales PASS : schéma, absence de valeurs de marché, hash archive, CRC et rapprochements.
  Périmètre Git : quatre checkpoints uniquement ; aucun export, rapport privé, prix, secret ou chemin
  personnel publié. Revue du diff et CI de PR obligatoires avant fusion selon le mandat permanent.
- Verdict D003 : BLOCKED — D003_NQ_MNQ_LINEAGE_REQUIRED. Action unique consignée dans CURRENT_STATE.

## 2026-09-19 — Reprise SRE et séparation des lignées NQ/MNQ

- Deux exemplaires du nouveau mandat AGIcoreManager lus intégralement et comparés : contenus
  octet pour octet identiques, SHA-256 ee96c539fa0971e57c1b9bf9f2a48454666c4ab67416f4592ec29a0c4f4f7f23.
- GitHub vérifié avant modification : main = 61643be37ba70f18286e9be8baefc168eba713f3,
  merge PR #244 ; arbre 1e1ede4b6517b01f1b521ffadbdf7188a3fe1368. Le commentaire final de
  PR #244 confirme CI #169 success sur le head c5654d7d39bf67ecafb2a26c01d86d2ae783b3d3.
- Branche dédiée feature/nq-mnq-independent-lineages-v1 créée depuis ce main ; état initial propre
  et git diff --check PASS. SINK-B3, D002 et Gate 5 ne sont pas recommencés.
- Décision explicite appliquée : NQ et MNQ deviennent deux filières de preuve indépendantes.
  D003 demeure BLOCKED_PROVENANCE pour la lignée legacy MNQ mais ne bloque plus le projet entier.
- Les faits de PR #244 sont immuables : aucun ancien résultat requalifié. Les noms NQ_* restent
  insuffisants pour prouver NQ ; leur classification reste LEGACY_UNVERIFIED/UNKNOWN_INSTRUMENT.
- L'archive connue conserve EXPOSED_DEVELOPMENT ; aucun changement de rôle, aucune lecture OHLCV,
  aucun accès OOS, acquisition de données, replay, modification de stratégie ou du Risk Engine.
- Prochaine tranche autorisée sans gate métier : contrat de manifeste et validation technique des
  nouvelles lignées. La formalisation des règles ambiguës EMA_PULLBACK_V1 restera une gate stratégie.

## 2026-09-19 — DATASET_LINEAGE_MANIFEST_V1

- Reprise depuis main a2a64fd921a0f288796788c3837bbab7c6df63f6, merge PR #245 ; arbre
  385264bd09aa9e18a91f9330f4638c00d51dd89a. Nouvelle branche dédiée et état initial propre.
- Audit du code : de nombreux manifestes de résultats existent, mais aucun contrat central ne lie
  source, instrument, preuve du contrat, transformation, parent, rôle et règles d'exposition OOS.
- Ajout d'un contrat immutable et canonique de métadonnées. Il ne lit ni fichier, ni ligne OHLCV,
  et ne transforme pas une assertion instrument en preuve. Les champs requis UNKNOWN sont refusés.
- Séparation fail-closed : un même hash source ne peut être NQ et MNQ ; parents et lignées croisés,
  réutilisation d'un dataset enregistré comme source brute de l'autre instrument, doublons,
  parents absents, cycles et manifests préparés forgés sont refusés.
- Protection OOS : rôle OOS_TEST limité à UNEXPOSED + SEALED + frontière explicite ; mélange d'une
  même source entre OOS et rôle non-OOS refusé. Archive historique inchangée EXPOSED_DEVELOPMENT.
- Revue intermédiaire : reproduction puis fermeture d'un contournement où le hash d'un dataset MNQ
  enregistré pouvait être redéclaré comme source brute NQ sans passer par le contrôle parent.
- Tests ciblés : 17 passed in 0.10s. Suite complète : 5909 passed, 6 warnings in 110.62s.
  Warnings connus : dépréciations Starlette/httpx/anyio et adaptateur datetime SQLite.
- Ruff : All checks passed. py_compile et git diff --check : PASS.
- Aucun dataset acquis/ouvert, aucun OOS lu/reclassé, aucun replay, prix, stratégie, Risk Engine,
  NinjaTrader, broker, compte ou ordre réel utilisé ou modifié.
- Prochaine gate métier après intégration : CLEAN_LINEAGE_SOURCE_EVIDENCE ; obtenir une preuve
  technique assainie et vérifiable pour renseigner un premier manifeste NQ ou MNQ sans UNKNOWN.

## 2026-09-19 — Intégration DATASET_LINEAGE_MANIFEST_V1

- Publication par objets GitHub, le push HTTPS ayant déjà été vérifié indisponible sans identifiant
  local dans cette session. Les cinq blobs distants correspondent exactement aux blobs locaux ;
  arbre publié/testé
  7944221d3b263c44282bbbe0351c35c520a24483.
- Commit distant 93b7fc22ea86b8f7befe3ab015f51339ec90f9b4, parent
  a2a64fd921a0f288796788c3837bbab7c6df63f6 ; PR #246 créée en brouillon puis passée Ready.
- CI AGIcore #173 (run 35436126126) completed/success sur le head exact :
  5909 passed, 6 warnings in 132.04s ; contrôle git diff --check PASS.
- Revue pré-fusion : mergeable=true, base et head inchangés, exactement cinq fichiers attendus.
  Fusion protégée par expected_head_sha ; merge 17c747d005e2b6699b04bc19fe70267dfe5a2557.
- Main récupéré et vérifié : arbre 7944221d3b263c44282bbbe0351c35c520a24483,
  identique à l'arbre local testé et à la PR ; parents a2a64fd9 et 93b7fc22.
- Aucun dataset, OOS, prix, stratégie, Risk Engine, NinjaTrader, broker, compte ou ordre réel touché.
- Arrêt à une vraie gate métier : BLOCKED_HUMAN_GATE — CLEAN_LINEAGE_SOURCE_EVIDENCE.

## 2026-09-22 — EMA_PULLBACK_V1_MNQ_PULLBACK_PREDICATE

- Reprise depuis `origin/main` au merge 3e155113ac53e225629f3f7693a50cac8bea2957 de la PR #250 ;
  branche dédiée `feature/ema-pullback-v1-mnq-predicate`, état initial propre et diff-check PASS.
- Décision métier figée sans optimisation : fenêtre `t-3..t-1`, distance maximale inclusive de
  huit ticks MNQ (2,00 points), mèche traversante autorisée, confirmation LONG strictement au-dessus
  de l'EMA20 et SHORT strictement en dessous ; égalité refusée.
- Nouveau sous-prédicat déterministe, à base de `Decimal`, qui exige exactement trois indices
  causaux et exclut explicitement la bougie de confirmation de la recherche du pullback.
- Ce sous-prédicat n'émet pas de signal de trading. Pente EMA20 et croisement MACD restent
  obligatoires mais non implémentés tant que leurs règles machine ne sont pas autorisées.
- Tests synthétiques : 14 passed in 0.24s. Régressions stratégie : 56 passed in 0.41s.
- Suite complète : 5926 passed, 6 warnings in 255.75s. Ruff ciblé, Ruff format, `py_compile` et
  `git diff --check` PASS.
- Aucun accès dataset/OOS, replay, PnL, optimisation, Risk Engine, broker, compte ou ordre réel.
- Verdict : `EMA_PULLBACK_V1_MNQ_PULLBACK_PREDICATE = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — EMA20_SLOPE_FORMULA_REQUIRED`.

## 2026-09-23 — EMA_PULLBACK_V1_MNQ_EMA20_SLOPE

- Reprise depuis `origin/main` au merge bc9508ddd05b3537438c7fa9fe48ba55902af5ec de la PR #251 ;
  branche dédiée `feature/ema-pullback-v1-mnq-slope`, état initial propre.
- Décision métier figée sans optimisation : `K = 3`, pente
  `(EMA20[t] - EMA20[t-3]) / 3`, seuil `0,0 point/bar`, LONG strictement positif, SHORT strictement
  négatif, zéro et égalité refusés.
- Nouveau sous-prédicat `Decimal` limité aux bougies clôturées `t` et exactement `t-3`. Warmup
  insuffisant et tout indice non causal échouent explicitement.
- Douze nouveaux cas synthétiques couvrent LONG, SHORT, zéro, égalité, valeurs très faibles des deux
  signes, warmup et causalité ; fichier ciblé : 26 passed in 0.08s. Régressions stratégie :
  68 passed in 0.12s.
- Suite complète : 5938 passed, 6 warnings in 86.03s. Ruff ciblé, format Ruff, `py_compile`, les
  4 gardes de confidentialité, `git diff --check` et le scan anti-fuite des ajouts PASS ; aucun
  binaire ou ligne de marché dans le diff.
- Aucun accès dataset/OOS, replay, PnL, optimisation, Risk Engine, broker, compte ou ordre réel.
- Verdict : `EMA_PULLBACK_V1_MNQ_EMA20_SLOPE = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — MACD_CROSS_DEFINITION_REQUIRED`.

## 2026-09-23 — EMA_PULLBACK_V1_MNQ_MACD_AND_ENTRY_SIGNAL

- Reprise depuis `origin/main` au merge 8c90ba79fb0492676cbb321c7c5ee41a46ca8f8b de la PR #252 ;
  branche dédiée `feature/ema-pullback-v1-mnq-macd`, état initial propre.
- Décision métier figée sans optimisation : MACD `12/26/9`, EMA pour les deux lignes, formule
  `EMA12(Close) - EMA26(Close)`, signal `EMA9(MACD_LINE)` et même amorçage déterministe que le
  replay public (`first close`, `alpha = 2/(period+1)`).
- Croisements exacts : égalité admise à `t-1`, inégalité stricte exigée à `t`, validité limitée à
  la bougie de confirmation courante. Un croisement antérieur ne qualifie pas `t`.
- Warmup fail-closed : moins de 35 barres clôturées causales donne `INSUFFICIENT_WARMUP` et `NONE`.
  Les historiques non contigus sont refusés et les valeurs postérieures à `t` sont ignorées.
- Assemblage ajouté : pullback/clôture + pente EMA20 + MACD doivent qualifier le même côté sur le
  même `t`. Le résultat reste un signal non exécutable ; aucun ordre ou prix d'exécution n'est créé.
- Quinze nouveaux cas portent le fichier ciblé à 41 tests PASS en 0,07 s. Les 90 tests stratégie/
  replay ciblés passent en 0,23 s. Suite complète : 5 953 passed, 6 warnings in 85.88s.
- Ruff ciblé et format Ruff, `py_compile`, les 4 gardes de confidentialité et `git diff --check`
  passent. Le diff contient exactement cinq fichiers texte, aucun RAW, binaire ou ligne de marché.
- Aucun accès dataset/OOS, PnL, optimisation, replay de données, Risk Engine, broker, compte ou ordre.
- Verdict : `EMA_PULLBACK_V1_MNQ_MACD = PASS` et `EMA_PULLBACK_V1_MNQ_ENTRY_SIGNAL = PASS` ;
  prochaine gate métier unique : `BLOCKED_HUMAN_GATE — EMA20_POSITION_EXIT_RULE_REQUIRED`.

## 2026-09-23 — EMA_PULLBACK_V1_MNQ_EMA20_POSITION_EXIT

- Reprise depuis `origin/main` au merge b4573f3b7525dff4e1af33541e5ccec6e1c662f0 de la PR #253 ;
  branche dédiée `feature/ema-pullback-v1-mnq-ema20-exit`, état initial propre.
- Décision métier figée sans optimisation : sortie LONG strictement sous EMA20, sortie SHORT
  strictement au-dessus, égalité `HOLD` et décision uniquement après clôture de `t`.
- Les mèches traversantes seules ne déclenchent rien. L'évaluateur sélectionne exactement `t`, ignore
  toute valeur future, n'émet aucun ordre/prix et expose seulement le premier indice admissible `t+1`.
- Neuf nouveaux cas portent le fichier ciblé à 50 tests PASS en 0,14 s. Les 99 tests stratégie/replay
  ciblés passent en 0,20 s. Suite complète : 5 962 passed, 6 warnings in 85.10s.
- Aucun accès dataset/OOS, PnL, optimisation, replay de données, Risk Engine, broker, compte ou ordre.
- Verdict : `EMA_PULLBACK_V1_MNQ_EMA20_POSITION_EXIT = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — NEXT_BAR_EXECUTION_MODEL_REQUIRED`.

## 2026-09-26 — EMA_PULLBACK_V1_MNQ_T_MINUS_2_TOUCH_OR_PROXIMITY

- Reprise depuis `origin/main` au merge 0880da6fb2dd916ba53ed1caf069f66342130f67 de la PR #254 ;
  branche dédiée `feature/ema-pullback-v1-mnq-t-minus-2-touch`, état initial propre et diff-check PASS.
- Décision métier figée sans optimisation : dans `t-3`, `t-2`, `t-1`, seule la deuxième bougie
  `t-2` peut satisfaire le pullback ; sa plage doit toucher/croiser son EMA20 ou rester à une
  distance maximale inclusive de huit ticks MNQ (2,00 points).
- Exactement huit ticks qualifie et neuf ticks échoue. Une condition satisfaite sur `t-3` ou `t-1`
  ne se substitue pas à `t-2`.
- Quatre nouveaux cas portent le fichier ciblé à 54 tests PASS en 0,18 s. Les 103 tests stratégie/
  replay ciblés passent en 0,30 s. Suite complète : 5 966 passed, 6 warnings in 106.30s.
- Ruff ciblé, format Ruff et `py_compile` PASS. Aucun accès dataset/OOS, PnL, optimisation, replay
  de données, Risk Engine, broker, compte ou ordre.
- Verdict : `EMA_PULLBACK_V1_MNQ_T_MINUS_2_TOUCH_OR_PROXIMITY = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — NEXT_BAR_EXECUTION_MODEL_REQUIRED`.

## 2026-09-26 — EMA_PULLBACK_V1_MNQ_NEXT_BAR_EXECUTION

- Reprise depuis `origin/main` au merge eadd4f3df578c8fec252e91fe6850a7d8d882886 de la PR #255 ;
  branche dédiée `feature/ema-pullback-v1-mnq-next-bar-execution`, état initial propre.
- Décision métier figée sans optimisation : signal/décision à `Close[t]`, ordre simulé `MARKET`,
  fill exclusivement à `Open[t+1]` pour les entrées et les sorties principales EMA20.
- Si `t+1` manque, le résultat est `EXPIRED_NO_EXECUTION`, sans prix inventé, sans ouverture de
  position et sans fermeture artificielle. Same-bar, `Close[t]`, dernier prix connu et barre future
  arbitraire sont interdits ; les mutations postérieures à `t+1` sont sans effet.
- Le contrat fail-closed refuse décision non qualifiée, indice de décision incohérent et doublon de
  `t+1`. Le modèle est explicitement bar-based, sans slippage, spread Bid/Ask, latence ou réalisme tick.
- Douze nouveaux cas portent le fichier synthétique à 66 tests PASS en 0,26 s. Les 115 tests
  stratégie/replay ciblés passent en 0,30 s. Suite complète : 5 978 passed, 6 warnings in 108.56s.
- Ruff ciblé, format Ruff, `py_compile` et `git diff --check` PASS. Aucun accès dataset/OOS, PnL,
  optimisation, replay de données, Risk Engine, broker, compte ou ordre réel.
- Verdict : `EMA_PULLBACK_V1_MNQ_NEXT_BAR_EXECUTION = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — INITIAL_STOP_LOSS_RULE_REQUIRED`.

## 2026-09-26 — EMA_PULLBACK_V1_MNQ_INITIAL_STRUCTURAL_STOP

- Reprise depuis `origin/main` au merge f9cc8c835b538d7df1ad0a660cabb7da619f13db de la PR #256 ;
  branche dédiée `feature/ema-pullback-v1-mnq-structural-stop`, état initial propre.
- Décision métier figée sans optimisation : LONG `Low[t-2] - 0,25 point`, SHORT
  `High[t-2] + 0,25 point`, calcul à `Close[t]` depuis des barres clôturées et niveau immuable.
- L'entrée à `Open[t+1]` est refusée si le stop n'est pas strictement sous le prix pour LONG ou
  strictement au-dessus pour SHORT. Aucune position n'est ouverte avec un stop incohérent.
- Déclenchement bar-based inclusif par `Low[k]`/`High[k]`. Un gap strict est rempli à `Open[k]` ;
  sinon le fill simulé utilise le stop. Aucun slippage, déplacement automatique ou stop dynamique.
- Dix-neuf nouveaux cas portent le fichier synthétique à 85 tests PASS en 0,25 s. Les 131 tests
  stratégie/replay ciblés passent en 0,47 s. Suite complète : 5 997 passed, 6 warnings in 129.21s.
- Ruff ciblé, format Ruff, `py_compile`, gardes de confidentialité, scan anti-fuite et
  `git diff --check` PASS. Aucun accès dataset/OOS, PnL, optimisation, Risk Engine, broker ou ordre.
- Verdict : `EMA_PULLBACK_V1_MNQ_INITIAL_STRUCTURAL_STOP = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — TAKE_PROFIT_RULE_REQUIRED`.

## 2026-09-26 — EMA_PULLBACK_V1_MNQ_TAKE_PROFIT_NONE

- Reprise depuis `origin/main` au merge 2a9b334dbeb881f5b233534cd97863e646fe56f7 de la PR #257 ;
  branche dédiée `feature/ema-pullback-v1-mnq-no-take-profit`, état initial propre.
- Décision métier figée sans optimisation : `TAKE_PROFIT = NONE`, activation fausse et prix nul.
  Aucune cible monétaire, ticks, points ou multiple de risque n'est créée.
- Une observation de prix favorable ou de PnL latent ne produit jamais une sortie ; le contrat
  retourne systématiquement `HOLD`, sans ordre et sans fermeture de position.
- Neuf nouveaux cas portent le fichier synthétique à 94 tests PASS en 0,23 s. Les 140 tests
  stratégie/replay ciblés passent en 0,49 s. Suite complète : 6 006 passed, 6 warnings in 77.13s.
- Ruff ciblé, format Ruff et `git diff --check` PASS. Aucun accès dataset/OOS, optimisation,
  Risk Engine, broker, compte ou ordre réel ; aucun breakeven ou trailing stop ajouté.
- Verdict : `EMA_PULLBACK_V1_MNQ_TAKE_PROFIT_NONE = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — EXIT_PRIORITY_RULE_REQUIRED`.

## 2026-09-26 — EMA_PULLBACK_V1_MNQ_EXIT_PRIORITY

- Reprise depuis `origin/main` au merge 8b410b9c00b0e3ff84822b068f54732d5f1886cf de la PR #258 ;
  branche dédiée `feature/ema-pullback-v1-mnq-exit-priority`, état initial propre.
- Décision métier figée sans optimisation : `STRUCTURAL_STOP_FIRST`, puis `EMA20_EXIT`, pour une
  sortie EMA20 en attente et un stop structurel évalués au même `Open[k]`.
- Si le stop est déclenché inclusivement à l'ouverture, il remplit à `Open[k]` et annule la sortie
  EMA20. Sinon la sortie EMA20 remplit à cette ouverture et annule le stop.
- Le résultat fail-closed garantit un seul motif, un seul fill et une seule fermeture de position ;
  il refuse doubles exécutions, doubles fermetures, incohérences de côté et mauvaise barre.
- Quatorze nouveaux cas portent le fichier synthétique à 108 tests PASS en 0,23 s. Les 154 tests
  stratégie/replay ciblés passent en 0,34 s. Suite complète : 6 020 passed, 6 warnings in 82.13s.
- Ruff ciblé et `py_compile` PASS. Aucun accès dataset/OOS, PnL, optimisation, Risk Engine, broker,
  compte ou ordre réel ; aucun breakeven ou trailing stop ajouté.
- Verdict : `EMA_PULLBACK_V1_MNQ_EXIT_PRIORITY = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — BREAKEVEN_RULE_REQUIRED`.

## 2026-09-26 — EMA_PULLBACK_V1_MNQ_BREAKEVEN_NONE

- Reprise depuis `origin/main` au merge c38482176044224fdc82a2f2fcc8d252bd38e126 de la PR #259 ;
  branche dédiée `feature/ema-pullback-v1-mnq-no-breakeven`, état initial propre.
- Décision métier figée sans optimisation : `BREAKEVEN = NONE`, aucun déplacement vers l'entrée,
  aucun trigger et aucun prix de breakeven. Le stop structurel initial reste la même instance
  immuable pendant toute la position.
- Prix favorable, ticks, multiples 1R/2R/N, PnL monétaire et durée en position restent sans effet.
  Un dépassement de l'entrée puis un retracement conserve le stop initial pour LONG et SHORT.
- Le contrat fail-closed refuse toute activation cachée. Les seules sorties restent
  `STRUCTURAL_STOP`, puis `EMA20_EXIT`, avec `STRUCTURAL_STOP_FIRST`.
- Seize nouveaux cas portent le fichier synthétique à 124 tests PASS en 0,25 s. Les 170 tests
  stratégie/replay ciblés passent en 0,39 s. Suite complète : 6 036 passed, 6 warnings in 84.05s.
- Ruff ciblé, format Ruff et `py_compile` PASS. Aucun accès dataset/OOS, optimisation, Risk Engine,
  broker, compte ou ordre réel ; aucun trailing stop ajouté.
- Verdict : `EMA_PULLBACK_V1_MNQ_BREAKEVEN_NONE = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — TRAILING_STOP_RULE_REQUIRED`.

## 2026-09-27 — EMA_PULLBACK_V1_MNQ_TRAILING_STOP_NONE

- Reprise depuis `origin/main` au merge 957b1926612d00f8b48c7b5cb4acb983e0cb1205 de la PR #260 ;
  branche dédiée `feature/ema-pullback-v1-mnq-no-trailing-stop`, état initial propre.
- Décision métier figée sans optimisation : `TRAILING_STOP = NONE`; activation, distance, step,
  fréquence et référence nulles. Le stop structurel initial reste strictement immuable.
- Nouveaux High/Low, prix favorable, ticks, multiples `R`, PnL, EMA20 et durée restent sans effet.
  Le contrat impose la même instance de stop et refuse une copie égale ou une configuration cachée.
- Les seules sorties restent `STRUCTURAL_STOP`, puis `EMA20_EXIT`, avec
  `STRUCTURAL_STOP_FIRST`; take-profit, breakeven et trailing stop sont tous explicitement absents.
- Vingt-quatre nouveaux cas portent le fichier synthétique à 148 tests PASS en 0,12 s. Les 152
  tests contrat/confidentialité passent en 0,27 s et les 194 régressions stratégie/replay en 0,51 s.
  Suite complète : 6 060 passed, 6 warnings in 77.15s.
- Ruff ciblé, format Ruff et `py_compile` PASS. Aucun accès dataset/OOS, optimisation, Risk Engine,
  broker, compte ou ordre réel.
- Verdict : `EMA_PULLBACK_V1_MNQ_TRAILING_STOP_NONE = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — SESSION_FILTER_RULE_REQUIRED`.

## 2026-09-27 — EMA_PULLBACK_V1_MNQ_SESSION_FILTER_NONE

- Reprise depuis `origin/main` au merge cb26964639130a7f4a1e00a331c4c920dbbec699 de la PR #261 ;
  branche dédiée `feature/ema-pullback-v1-mnq-no-session-filter`, état initial propre.
- Décision métier figée sans optimisation : `SESSION_FILTER = NONE`, aucun jour, horaire, fuseau
  ou DST propre à la stratégie. L'évaluateur n'accepte aucune donnée temporelle.
- Le calendrier source reste obligatoire : seules les barres clôturées et valides du template
  exact `CME US Index Futures ETH` sont admises. Aucun filtre stratégique ne peut le contourner.
- Toute barre source admissible laisse les entrées éligibles ; `STRUCTURAL_STOP` et `EMA20_EXIT`
  restent actifs sur chacune d'elles. Toute suppression cachée est refusée fail-closed.
- Vingt-neuf nouveaux cas portent le fichier synthétique à 177 tests PASS en 0,45 s. Les 181 tests
  contrat/confidentialité passent en 0,17 s et les 223 régressions stratégie/replay en 0,38 s.
  Suite complète : 6 089 passed, 6 warnings in 78.59s.
- Ruff ciblé, format Ruff et `py_compile` PASS. Aucun accès dataset/OOS, optimisation, Risk Engine,
  broker, compte ou ordre réel.
- Verdict : `EMA_PULLBACK_V1_MNQ_SESSION_FILTER_NONE = PASS` ; prochaine gate métier unique :
  `BLOCKED_HUMAN_GATE — OPEN_POSITION_SIGNAL_POLICY_REQUIRED`.

## 2026-09-27 — EMA_PULLBACK_V1_MNQ_OPEN_POSITION_SIGNAL_POLICY

- Reprise depuis `origin/main` au merge ab0baf5d8852fa463b2450a697521d751ffbc95c de la
  PR #262 ; branche dédiée `feature/ema-pullback-v1-mnq-open-position-signals`, base propre.
- Décision métier sans optimisation : `IGNORE_ALL_NEW_SIGNALS_UNTIL_FLAT`. Même sens ou opposé,
  chaque nouveau signal pendant une position ouverte est supprimé ; ni pyramiding, ni inversion,
  ni file d'attente, ni entrée différée.
- La sortie EMA20 encore en attente à `Close[t]` ne rend pas la position `FLAT`. Le retour à plat
  exige un fill ; un ancien signal ignoré ne peut être rejoué après ce fill. Le stop structurel
  et la sortie EMA20 conservent leurs modalités et leur priorité existantes.
- Vingt-neuf nouveaux cas portent le fichier synthétique à 206 tests PASS. Les 213 tests
  stratégie/replay ciblés passent. Aucun accès dataset/OOS, PnL, optimisation, Risk Engine,
  broker, compte ou ordre réel. Suite complète : 6 118 passed, 6 warnings in 79.84s.
  Ruff ciblé, format Ruff, `py_compile`, `git diff --check` PASS ; CI à vérifier sur la PR.
- Verdict : `EMA_PULLBACK_V1_MNQ_OPEN_POSITION_SIGNAL_POLICY = PASS` ; prochaine gate métier
  unique : `BLOCKED_HUMAN_GATE — POSITION_SIZE_RULE_REQUIRED`.

## 2026-09-27 — EMA_PULLBACK_V1_MNQ_FIXED_POSITION_SIZE_ONE_MNQ

- Reprise depuis `origin/main` au merge bda3a848af32f7909540ecafa3eb35c05c799b12 de la
  PR #263 ; branche dédiée `feature/ema-pullback-v1-mnq-fixed-position-size`, base propre.
- Décision sans optimisation : taille fixe d'un contrat ; LONG `+1 MNQ`, SHORT `-1 MNQ`,
  `abs(position) <= 1`. La position n'est créée qu'après le fill causal exact à `Open[t+1]`.
- Pourcentage de risque, volatilité, distance du stop, PnL, martingale et anti-martingale ne sont
  ni des entrées ni des modes actifs. Le contrat fail-closed refuse chaque activation cachée.
- Les signaux pendant une position ouverte laissent la taille inchangée ; aucun second contrat,
  pyramiding ou inversion. Un fill V1 de sortie vérifié remet la position à zéro.
- Vingt-huit nouveaux cas portent le fichier synthétique à 234 tests PASS ; les 241 tests
  stratégie/replay ciblés et les 256 tests contrat/filiation/OOS passent. Suite complète :
  6 146 passed, 6 warnings in 76.91s. Ruff ciblé, format Ruff, `py_compile` et diff-check PASS ;
  CI à vérifier sur la PR.
- Aucun accès dataset/OOS, PnL, optimisation, Risk Engine, broker, compte ou ordre réel.
- Verdict : `EMA_PULLBACK_V1_MNQ_FIXED_POSITION_SIZE_ONE_MNQ = PASS` ; prochaine gate métier
  unique : `BLOCKED_HUMAN_GATE — END_OF_DATA_POSITION_POLICY_REQUIRED`.

## 2026-09-27 — EMA_PULLBACK_V1_MNQ_END_OF_DATA_KEEP_OPEN_UNREALIZED

- Reprise depuis `origin/main` au merge 0ca23d0a534640cb3ce78a0a9ffabbbd4a764655 de la
  PR #264 ; branche dédiée `feature/ema-pullback-v1-mnq-end-of-data`, base propre.
- Convention comptable sans optimisation : une position restante conserve
  `OPEN_AT_END_OF_DATA`; aucun forced exit, synthetic fill, prix de sortie ou trade fermé.
- Le PnL réalisé, l'equity réalisée et le nombre de trades fermés restent inchangés. Seul le
  dernier Close source valide produit une marque informative et un PnL latent séparé en points MNQ.
- L'état à plat rapporte zéro latent. Le contrat refuse état partiel, marque antérieure au fill,
  réalisation/fill caché, cotation reconstruite et toute entrée de barre future.
- Vingt-trois nouveaux cas portent le fichier synthétique à 257 tests PASS ; 264 régressions
  stratégie/replay ciblées et 279 tests contrat/filiation/OOS passent. Suite complète :
  6 169 passed, 6 warnings in 77.56s. Ruff ciblé, format Ruff, `py_compile` et diff-check PASS.
- Aucun accès dataset/OOS, optimisation, Risk Engine, broker, compte ou ordre réel.
- Verdict : `EMA_PULLBACK_V1_MNQ_END_OF_DATA_KEEP_OPEN_UNREALIZED = PASS` ; prochaine gate
  unique : `BLOCKED_HUMAN_GATE — FEES_AND_SLIPPAGE_MODEL_REQUIRED`.

## 2026-09-27 — EMA_PULLBACK_V1_MNQ_FEES_AND_SLIPPAGE_MODEL

- Reprise depuis `origin/main` au merge 3cfcc83a062abce86fb4ddc562abcca722ab625c de la PR #265 ;
  branche dédiée `feature/ema-pullback-v1-mnq-cost-model`, base et worktree propres.
- Baseline datée : commission Apex/Rithmic `0.51 USD` par fill et MNQ ; un tick défavorable pour
  l'entrée, la sortie EMA20 et le stop structurel ; spread absorbé sans second débit.
- Spécification CME : `2.00 USD` par point MNQ, `0.50 USD` par tick. Comptabilité `Decimal`, grille
  `0.25`, montants USD `ROUND_HALF_UP` à deux décimales.
- Les prix bar-based restent les prix de base auditables. Le prix comptable embarque le slippage ;
  le PnL net retire ensuite les commissions uniquement.
- Stop normal depuis son niveau, gap-through depuis l'Open. Rejet, signal ignoré, expiration et
  marque EOD ne paient rien ; la marque ouverte utilise toutefois l'entrée déjà slippée.
- Vingt-huit nouveaux cas portent le fichier synthétique à 285 tests PASS ; 292 régressions
  stratégie/replay et 307 tests contrat/filiation/OOS passent. Suite complète : 6 197 passed,
  6 warnings in 74.95s. Ruff ciblé, format Ruff, `py_compile` et diff-check PASS.
- Aucun dataset/OOS, replay historique, optimisation, Risk Engine, broker, compte ou ordre réel.
- Verdict : `EMA_PULLBACK_V1_MNQ_FEES_AND_SLIPPAGE_MODEL = PASS` et formalisation V1 `PASS` ;
  prochaine gate : `BLOCKED_HUMAN_GATE — BASELINE_DEVELOPMENT_REPLAY_PROTOCOL_REQUIRED`.

## 2026-09-27 — EMA_PULLBACK_V1_MNQ_DEVELOPMENT_SCREENING

- Le protocole a été fusionné avant résultats par PR #267 : head
  `cfb4b2c10884a5a88960df99565de0e2106bed90`, CI #216/run `36340320865` success, merge
  `e26748e56e0805ed020c57a74c7c17e15ae8ef5e`.
- Protocole canonique SHA-256
  `13f3e1b71ce27a848a16a9598c37d76e9298a49331531fc7602118ec788c864f`, lié au seul RAW propre
  `EXPOSED_DEVELOPMENT` SHA-256
  `3bd8c078d40143ccb1977562e47afadfd173f9c123e3a062ba28dbcb7721ba1a`.
- Runner figé avant résultat au commit `e56f57f72f64f41dc84a5a6a0569b38cded60bf1`, module
  SHA-256 `26711662c3ea2d3df7e92dafe4cee3b972862eeefb642e6147123d5a912b3765`.
  Avant replay : 14 tests runner, 336 tests ciblés et 6 226 tests complets PASS, 6 warnings.
- Le RAW vérifié contient 52 431 barres, 2 791 485 octets, six champs par ligne, sans timestamp
  dupliqué/non croissant, valeur hors grille ni OHLCV incohérent. Aucun prix ou ligne n'est publié.
- Une première invocation shell a échoué sur `ModuleNotFoundError` avant import, lecture du RAW ou
  appel du runner. L'unique exécution effective est le run
  `ema-pullback-development-8bfe99a3f4beec32`, achevé à `2026-09-27T18:34:15.444381Z`.
- Résultat total : 1 372 trades clôturés ; PnL net `4 138.56 USD` ; profit factor
  `1.166145174693789066734111356` ; drawdown marqué `2 501.21 USD` ; 23 pertes consécutives.
- S1/S2/S3 : 257/464/651 trades ; PnL `197.86` / `4 276.72` / `-336.02 USD` ; profit factor
  `1.050196870369994520103103245` / `1.550261445981554677206851120` /
  `0.9745351810395393567181439677`. S3 enfreint le plancher de `-200.00 USD`.
- Verdict mécanique : `NO_GO_BASELINE`. Échecs : drawdown, pertes consécutives, stabilité
  segmentaire. Aucun ajustement de seuil, OOS, optimisation, Risk Engine, broker ou ordre réel.
- Rapport assaini SHA-256
  `4351d82e2b965b75843b0e24545358c80e2dc544a0549d085ceb8e93f4ceb3f6`, zéro prix/RAW exposé.
- Gate suivante :
  `BLOCKED_HUMAN_GATE — EMA_PULLBACK_V1_MNQ_NO_GO_VARIANT_DECISION_REQUIRED`.

## 2026-09-28 — EMA_PULLBACK_V1A_MNQ_EMA20_MIN_SLOPE_1_TICK

- Reprise sans recommencer V1 : worktree propre, commit local préexistant `d9e650a`, arbre
  `566cf2ebf82acbd55ea614f3ac920d673e82e1e7`, PR #269 ouverte et CI en attente.
- Delta unique préengagé : formule de pente V1 inchangée sur `K = 3`, LONG `>= +0.25` et SHORT
  `<= -0.25` point/bar, comparaisons inclusives et aucun arrondi. Toutes les autres règles V1,
  les coûts, l'exécution, le dataset et les seuils de screening restent identiques.
- Contrat variante SHA-256
  `1dc90028d9de807a28218075c09b7d9b32d2eb8cc86b41a84814107a898f77df`. Avant replay :
  10 tests V1A, 39 tests variante/protocole/runner, 350 tests ciblés et 6 236 tests complets PASS ;
  Ruff, format, `py_compile`, JSON, anti-fuite et diff-check PASS.
- Préengagement fusionné avant résultat par PR #269 : head
  `ed3a751246e1cda03b99017d481acc4de4f9b1c1`, CI #220/run `36343021654` success, merge
  `92e6a5d3de8dd8bd13c2014d52f6ba63a3209d5b`.
- Un seul replay effectif V1A : `ema-pullback-development-f76f2d17c5ea7ab8`, achevé le
  2026-09-28T16:57:52.116620Z sur le même RAW propre SHA-256 `3bd8c078...ba1a`. Aucun OOS,
  aucune autre pente et aucun changement de seuil.
- V1A : 1 119 signaux qualifiés, 1 049 trades clôturés, PnL net `3 918.52 USD`, profit factor
  `1.183757573483896381609799103`, drawdown marqué `2 167.82 USD`, 19 pertes consécutives,
  200 sorties stop et 849 sorties EMA20.
- S1/S2/S3 : 189/342/518 trades ; PnL `-458.28` / `3 879.16` / `497.64 USD` ; profit factor
  `0.8672721690927310746702656989` / `1.607936861175452838645574421` /
  `1.043307840386536660760471892`. S1 enfreint le plancher `-200.00 USD`.
- Verdict mécanique : `NO_GO_VARIANT`. Échecs : drawdown, pertes consécutives et stabilité
  segmentaire. La baseline reste `NO_GO_BASELINE`; OOS et validation indépendante restent fermés.
- Rapport comparatif assaini SHA-256
  `29eef4a574fc46aab07a5ab60fc0c09fe111c3e72acc6d91ae3e5f04450582de`. Validations
  post-résultat : 11 tests V1A, 40 tests variante/protocole/runner, 351 tests ciblés et
  6 237 tests complets PASS avec 6 warnings historiques. Aucun test ne relance le RAW privé.
- Gate suivante :
  `BLOCKED_HUMAN_GATE — EMA_PULLBACK_V1A_MNQ_NO_GO_NEXT_EXPERIMENT_DECISION_REQUIRED`.

## 2026-09-28 — EMA_PULLBACK_V1B_MNQ_V1A_US_RTH_ENTRY_ONLY

- V1B est l'unique expérience autorisée après les verdicts immuables `NO_GO_BASELINE` de V1 et
  `NO_GO_VARIANT` de V1A. Son delta unique est le filtre des nouvelles entrées du lundi au vendredi,
  de 08:30 inclus à 15:00 exclu en `America/Chicago`, avec règles DST IANA.
- Le filtre porte uniquement sur la décision d'entrée à `Close[t]`. Le stop structurel et la sortie
  EMA20 restent actifs hors fenêtre ; aucune fermeture n'est forcée à 15:00. Toutes les autres
  règles, le RAW `EXPOSED_DEVELOPMENT` et le protocole de screening restent ceux de V1A.
- Contrat variante SHA-256
  `c034db1ab2592f0ba4455c0aa0bd5c1c7bc2193f944d9f297819e38c35452f0e` ; module V1B SHA-256
  `c61703033504539cda5067798c5b38832f406484e069228c9b6e3eb0533ee717` ; runner partagé SHA-256
  `a477d64e4d419aed40b29794f58714d463a8c0fe018b46e6e8004c0cb8dd6293`.
- Avant replay : 25 tests V1B, 65 tests variante/parents/runner, 369 tests stratégie/filiation/OOS
  et 6 262 tests complets PASS avec 6 warnings historiques. Ruff, format, `py_compile`, JSON et
  diff-check PASS.
- Préengagement fusionné avant résultat par PR #271 : head
  `8c060ce33a522ef9f2159ea19d69ba31b20607f3`, CI #224/run `36465463373` success, merge
  `b7f185d5d0706a7b694c6499f904a218993b6208`, arbre
  `a4c33fc2ebcdefe8fad7b97f039aeb4e937a4794`.
- Un seul replay effectif V1B : `ema-pullback-development-3d2bde3b4e3fe085`, achevé le
  2026-09-28T18:33:06.286656Z sur le même RAW propre SHA-256 `3bd8c078...ba1a`. Aucun OOS,
  aucune autre session et aucun changement de seuil.
- V1B : 339 signaux qualifiés, 780 refusés par la session, 325 trades clôturés, PnL net
  `3 493.00 USD`, profit factor `1.371813295013039544414284954`, drawdown marqué
  `1 954.87 USD`, 16 pertes consécutives, 59 sorties stop et 266 sorties EMA20.
- S1/S2/S3 : 50/110/165 trades ; PnL `488.00` / `3 530.80` / `-525.80 USD` ; profit factor
  `1.506960315811344275919384999` / `2.214192865052236290982619999` /
  `0.9048146619454159697028943005`. S3 enfreint le plancher `-200.00 USD`.
- Verdict mécanique : `NO_GO_VARIANT`. Échecs : drawdown, pertes consécutives et stabilité
  segmentaire. V1 et V1A restent inchangées ; OOS et validation indépendante restent fermés.
- Rapport comparatif assaini SHA-256
  `d3b188c8efed50fc418dab25941b9237261bf39cb88a259c371d7e65e4a0e41b`. Il ne contient ni prix
  ni ligne RAW. Validations post-résultat : 26 tests V1B, 370 tests stratégie/filiation/OOS et
  6 263 tests complets PASS avec 6 warnings historiques. Aucun test ne relance le RAW privé.
- Gate suivante :
  `BLOCKED_HUMAN_GATE — EMA_PULLBACK_V1B_MNQ_NO_GO_NEXT_EXPERIMENT_DECISION_REQUIRED`.
