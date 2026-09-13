# AGIcore decisions

## D001 — Profil durable post-SINK-B3 (approuvée le 2026-09-12)

Approbation utilisateur : « oui on fait ça », puis instruction de démarrer et poursuivre.
Le texte ci-dessous conserve la proposition initiale pour traçabilité ; son attente est levée.
SignalLoopOrchestrator et RuntimeEventBridge restent hors garantie durable du profil initial.

1. **Faits observés** : main c1316a06 ; CI #159 verte ; PR #238 intégrée.
   MemoryEvent possède ux_events_effect_id unique. MemoryService fournit create_event_idempotent.
   EventBus.accept_idempotent accepte durablement ; ExecutionAgent lie l'ACK au hash d'acceptation.
   EventDeliveryRepository interdit EMISSION_COMPLETED avant les handlers obligatoires.
   IdempotentMemoryDeliveryHandler possède une preuve de reprise après effet avant résultat.
   RuntimeEngine injecte facultativement cette autorité. SignalLoopOrchestrator conserve ses intents
   dans dict/set ; RuntimeEventBridge est un abonné passif. L'inbox L5 reste en mémoire.
2. **Problème** : une reprise complète du runtime et de tous ses effets n'est pas démontrée.
   Le test restart du replay croisé ne recrée pas le service L5 ni son inbox.
3. **Hypothèse unique** : un profil offline explicite avec autorités persistantes, manifeste figé
   et un seul handler mémoire obligatoire permet une preuve bornée de reprise sans double effet.
4. **Modification proposée** : profil offline dédié, SQLite explicite, refus au démarrage si une
   autorité manque ; persistance/reconstruction vérifiée de l'exécution L5, outbox et inbox ;
   remplacement de l'effet mémoire direct non idempotent par un effet stable via l'autorité existante.
   ACK = EMISSION_ACCEPTED durable uniquement ; EMISSION_COMPLETED = tous handlers requis terminés.
   Proposition : SignalLoopOrchestrator et RuntimeEventBridge restent hors garantie durable initiale,
   sans utiliser leurs effets pour déclarer la complétude ; entrées synthétiques déterministes.
   Ce choix limite la validation initiale et exige une décision humaine, pas un renommage de gate.
5. **Tests exécutés** : 159 PASS (contrats, migration, services, repositories, handler, agent,
   intégration runtime, reprise SQLite, multiprocessus). Aucun test nouveau ne démontre encore
   le redémarrage complet ; ce résultat ne doit pas être présenté comme tel.
6. **Acceptation/rejet** : accepter seulement après reconstruction de tous objets dans un nouveau
   processus, crash après effet avant journal, crash avant/après acceptation et ACK, retries,
   conflit de payload, stale worker fencing, un effet mémoire, replay identique et risque inchangé.
   Rejeter toute garantie exactly-once fondée sur le seul retour de emit() ou une inbox en RAM.
7. **Surapprentissage** : aucun PnL ni paramètre de stratégie ; fixtures synthétiques MNQ uniquement.
8. **Ticket Codex** : POST-SINK-B3-DURABLE-OFFLINE-PROFILE-V1. Après D001 approuvée, cartographier
   les autorités L5/inbox/outbox, figer manifeste et schéma de reprise, ajouter un test de crash
   en processus distinct, implémenter la persistance bornée, rejouer les tests ci-dessus,
   produire une PR sensible sans fusion automatique. Aucun Risk Engine modifié.
9. **Verdict initial** : ATTENDRE — BLOCKED_HUMAN_GATE.
   **État actuel** : APPROUVÉE le 2026-09-12 ; attente D001 levée.

**Proposition historique, déjà approuvée** : approuver ce profil offline initial avec SignalLoopOrchestrator et
RuntimeEventBridge hors garantie durable, ou exiger leur inclusion durable avant toute validation V1.
L’approbation D001 ne supprime aucune exigence de reprise complète
des composants effectivement obligatoires du profil retenu.

## D002 — Idempotence de l'effet mémoire direct canonique

1. Faits : le test en processus distinct échoue avant correction : trois événements sans effect_id
   pour une seule issue canonique après crash SQL et deux retries. D001 est désormais approuvée.
2. Problème : ExecutionAgent utilise create_event sous une inbox en RAM ; le commit SQL peut
   précéder la perte du processus et donc la connaissance locale de la réussite.
3. Hypothèse : une identité fondée sur le receipt_hash et un payload canonique stable suffisent
   à dédupliquer ce sink précis, y compris après redémarrage et changement d'identifiant de tâche.
4. Modification : chemin EventBus canonique seulement ; create_event_idempotent existant,
   effect_id execution-memory-<receipt_hash>, schema agicore.execution-memory-effect.v1,
   receipt + outcome, date explicite. Les durées et task_id transitoires restent dans le feedback.
   Conflit mémoire : erreur MEMORY_EFFECT_CONFLICT avant émission et ACK. Chemin legacy inchangé.
5. Tests : test crash réel os._exit(73), retries dans de nouveaux processus, comparaison à une
   exécution indépendante ; conflit SQL réel, aucune émission/ACK ; régressions agent/runtime/handler.
6. Acceptation : un événement et mêmes effect_id/payload_hash après reprise et référence ;
   conflit bloqué ; suite verte ; aucun changement Risk Engine. Fusion sensible humaine requise.
7. Surapprentissage : aucun PnL, uniquement MNQ synthétique, quantité 1, limite fixture 2.
8. Ticket : POST-SINK-B3-MEMORY-EFFECT-V1 ; trois fichiers code/tests plus quatre checkpoints
   obligatoires. Branche feature/post-sink-b3-memory-effect-v1, dépend de la PR documentaire #239.
9. Verdict : TESTER — validation de ce sink uniquement, pas validation V1 complète.

Limite de migration : les anciens événements sans effect_id ne sont pas reclassés ou dédupliqués.
Le futur profil durable doit utiliser une autorité neuve ou une migration explicitement validée.
La persistance de L5/outbox/inbox et la preuve de reprise de toutes les positions restent requises.


## Ticket suivant préparé — POST-SINK-B3-L5-RECOVERY-V1

1. Faits observés : execution_transaction.py initialise _authority en RAM et _publish_state
   ne fait qu'une affectation ; execution_outbox.py conserve _state et _publish_state en RAM.
   Les validateurs replay_execution_transaction_journal, replay_delivery_journal,
   replay_inbox_journal et replay_l5_execution_delivery_journal existent déjà.
2. Problème : perte des positions, résultats en attente et reçus au redémarrage complet.
3. Hypothèse unique : persister atomiquement les transitions L5/outbox et les transitions
   inbox, puis reconstruire avec les validateurs existants permet une reprise vérifiable.
4. Modification proposée : dans la phase dédiée après D002, autorité SQLite explicite,
   journal et ancre versionnés, contrôle CAS avant publication RAM, restauration obligatoire
   depuis journaux ; refuser base incohérente, ancre absente, manifeste différent et toute
   remise à zéro silencieuse. Aucun changement de règle du Risk Engine.
5. Tests : audit statique effectué ; aucun test de restauration complète ajouté ou revendiqué.
6. Acceptation : nouveau processus sans objets conservés ; position MNQ non nulle restaurée ;
   outbox pending et inbox restaurées ; crash avant/après commit, effet mémoire, acceptation
   bus et ACK ; retries sans nouvel ordre/fill/effet ; conflit et stale writer refusés ;
   replay final identique à référence indépendante ; refus d'une base tronquée/corrompue.
7. Surapprentissage : fixtures MNQ synthétiques seulement, aucun ajustement de stratégie/OOS.
8. Ticket Codex : examiner execution_transaction.py, execution_outbox.py, runtime.py et
   les tests d'intégration associés ; réutiliser l'autorité SQLite existante si compatible.
   Livrer diff borné et preuves, sans commit/push/PR automatique. Toute extension profonde
   au-delà du profil D001 devra être présentée avant implémentation.
9. Verdict : ATTENDRE — prérequis D002 prêt à soumettre à la gate de commit explicite.


## État des gates après intégration D002

D002 MERGED par PR #240, d52e9212eadac55e9d3d24482fd744ca54839771.
Précondition du ticket L5-RECOVERY levée. D001 couvre le profil offline explicite.
Les trois autorisations D002 sont consommées pour D002 uniquement ; prochain diff soumis
à revue humaine avant commit. Aucun changement du Risk Engine, OOS, data/ ou broker.

## Résultat intégré — POST-SINK-B3-L5-RECOVERY-V1 (2026-09-13)

1. **Faits observés** : main d52e9212 après fusion PR #240. Le store L5, son outbox et
   les inbox étaient en RAM. Les validateurs de replay existaient déjà. Le premier diff local
   a exposé puis corrigé trois incohérences : outcome étranger, ACK bus forgé et effet mémoire
   déclaré terminé alors que sa preuve SQL avait disparu.
2. **Problème** : un redémarrage complet perdait positions, résultats en attente et reçus ;
   une preuve de reprise limitée à des objets conservés en RAM ne satisfaisait pas D001.
3. **Hypothèse unique** : une autorité SQLite explicitement créée/reprise, avec document canonique,
   ancre, CAS et replay sémantique avant exposition, permet une reconstruction bornée et fail-closed.
4. **Modification proposée** : SQLiteL5RecoveryStore persiste atomiquement journaux L5/outbox/inbox
   avant publication RAM, fige consumers/effets et exige les preuves exactes Memory/EventBus.
   CREATE refuse un fichier existant ; RESUME refuse une base absente ou incohérente.
5. **Tests exécutés** : 24 ciblés PASS en 23.27s ; suite complète 5892 PASS, 6 warnings,
   77.02s ; Ruff, compilation Python et git diff --check PASS.
6. **Critères d'acceptation** : neuf crashes réels en nouveaux processus ; position MNQ non nulle,
   outbox/inbox/effets/ACK restaurés ; retry sans nouveau fill ; dépassement +2 refusé par le risque ;
   replay identique à une référence ; corruptions, faux ACK, autorités absentes/étrangères,
   outcome étranger et stale writer refusés ; handler obligatoire COMPLETED séparément.
7. **Risques de surapprentissage** : aucun PnL, paramètre ou signal ; uniquement MNQ synthétique,
   quantité 1 et test de refus +2. OOS et stratégie personnelle non lus et non modifiés.
8. **Ticket Codex** : implémentation et revue terminées sur
   feature/post-sink-b3-l5-recovery-v1. Deux nouveaux fichiers code/tests et quatre checkpoints
   intégrés par PR #241 ; head b1e5e37080e88f755353bb6cd1f7b5fcf4d26811, CI #163 success,
   merge 6c3c6bb5299e0fe8ee6db646e94b79fb4bed45df.
9. **Verdict** : L5_RECOVERY_MERGED_AND_VERIFIED — profil offline borné accepté ;
   V1_VALIDATED_OFFLINE_PAPER non atteint.

Limites conservées : profil offline borné de D001, pas bootstrap RuntimeEngine global ; le CAS
borne la publication mais les sinks doivent rester idempotents ; rollback cohérent de toute la
base détectable seulement avec L5RecoveryAnchor conservée indépendamment.

## Gate historique après intégration L5 recovery — consommée

Les autorisations commit, publication par connecteur, passage Ready et fusion de la PR #241
ont été données séparément puis consommées. La synchronisation documentaire a ensuite été
intégrée par PR #242. L'ancien arrêt avant commit est clos ; la Gate 5 est auditée ci-dessous.

## Résultat audité — GATE-5-OFFLINE-REPLAY-D001 (2026-09-13)

1. **Faits observés** : PR #242 et CI #165 sont intégrées par le merge
   d41103265f3afc5e324a01d45dd66b14bea0d148. Le test de PR #241 compose déjà les autorités
   L5/outbox/inbox, ExecutionService, ExecutionAgent, mémoire SQLite et EventBus du profil D001.
2. **Problème audité** : les checkpoints distinguaient la tranche L5 testée d'une Gate 5 dite
   « globale », sans établir si une preuve supplémentaire était réellement requise dans D001.
3. **Hypothèse unique** : les critères Gate 5 sont satisfaits si chaque composant obligatoire D001
   est recréé après crash, si les retries sont sans double effet et si les journaux égalent une référence.
4. **Modification** : aucune modification runtime. Audit des assertions intégrées et mise à jour
   documentaire uniquement ; RuntimeEngine, SignalLoopOrchestrator et RuntimeEventBridge restent exclus.
5. **Tests** : `tests/integration/test_sqlite_l5_recovery.py` relancé sur d41103265 :
   24 passed in 30.01s. Suite complète de la branche : 5892 passed, 6 warnings in 114.32s.
   La suite de l'arbre de PR #241 était déjà 5892 passed, 6 warnings in 77.02s.
6. **Acceptation** : neuf crashes `os._exit(73)` en processus neufs ; position MNQ = 1 restaurée ;
   retry du même intent avec un seul ordre/fill/effet ; refus MNQ +2 ; autorités, manifeste,
   corruption, stale writer, outcome et ACK incohérents refusés ; document L5 et effet mémoire
   égaux à une exécution indépendante de référence.
7. **Surapprentissage** : aucune donnée de marché, stratégie, métrique ou OOS ; fixtures MNQ synthétiques.
8. **Portée** : PASS pour le profil offline borné D001 uniquement. Ce verdict ne certifie ni le
   RuntimeEngine global, ni les composants explicitement exclus par D001, ni une performance de stratégie.
9. **Verdict** : GATE_5_D001_PROFILE_VERIFIED. V1_VALIDATED_OFFLINE_PAPER non atteint.

## D003 — Contrat de provenance MNQ avant protocole quantitatif

1. **Faits observés** : aucun document suivi ne fige la sémantique des timestamps exportés,
   le rollover, le volume et le calendrier de séances/jours fériés du futur jeu de développement.
2. **Problème** : sans ces métadonnées et sans hash/frontières, causalité, reproductibilité et
   séparation OOS ne peuvent pas être prouvées sans hypothèse implicite.
3. **Décision requise** : fournir ou approuver un contrat traçable précisant : timestamp de barre
   et fuseau/DST ; contrat/rollover ; OHLCV/volume ; sessions, jours fériés et clôtures anticipées ;
   hash, période et frontières du jeu de développement permis et de l'OOS réservé.
4. **Périmètre actuel** : aucune lecture de `data/`, aucun accès OOS, aucune intervention NinjaTrader,
   aucun changement Risk Engine ou stratégie. Ces interdictions restent actives.
5. **Verdict** : BLOCKED_HUMAN_GATE — G6_MNQ_PROVENANCE_CONTRACT.
