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

## D003 — Audit de filiation en lecture seule (2026-09-15)

- Autorisation spécifique : récupérer l'archive déjà existante et examiner localement ses octets
  pour en extraire seulement des métadonnées assainies. Aucun nouveau dataset, remplacement,
  téléchargement de marché, accès NinjaTrader/broker, replay de marché ou changement OOS.
- Autorisation Git permanente : commits, branches, push, PR et fusion documentaires sans nouvelle
  confirmation après revue du diff exact, vérifications concernées, diff-check, CI et absence de
  conflits, secrets ou fichiers inattendus. Les anciennes attentes Git de D001/D002 sont historiques.
- Frontières métier conservées : données, OOS, stratégie, Risk Engine et trading réel nécessitent
  leurs preuves et une décision spécifique. Aucun changement de ces domaines dans cette phase.
- Archive : hash vérifié, neuf membres distincts, intégrité ZIP contrôlée ; classification
  EXPOSED_DEVELOPMENT obligatoire, jamais holdout ni preuve de performance indépendante.
- Sources de rapports : 83 enregistrements issus d'une extraction antérieure complète conservée,
  et 145 manifestes locaux supplémentaires lisibles. Les 83 originaux Windows ne sont pas accessibles.
  Aucune déduplication ni assimilation de ces populations. Leurs champs absents restent UNKNOWN.
- Filiation : zéro correspondance directe des hashes de membres avec les input_sha256 des rapports ;
  aucune chaîne source/transformation/parent documentée dans ces enregistrements. Une absence de
  correspondance des octets ne démontre pas l'absence d'une transformation historique.
- Identité : tous les contract_id restent UNKNOWN. Les noms NQ_* restent LEGACY_NQ_UNVERIFIED ;
  les rapports localement étiquetés MNQ ne sont pas validés par leur nom ou leur modèle de coût.
- Registre retrouvé : le candidat séparé porte déjà une classification historique d'exposition ;
  sa mention et son hash déclaré ne le relient pas cryptographiquement au pipeline.
  CANDIDATE_MNQ_NOT_LINKED reste applicable, sans réaffectation OOS ni nouvelle lecture de ses prix.
- Vérifications D003 : hash archive, CRC ZIP, inventaire exact, tailles, lignes, structure et timestamps,
  rapprochements de hashes et schéma privé de douze champs. Aucune nouvelle mesure de performance.
- Verdict : BLOCKED — D003_NQ_MNQ_LINEAGE_REQUIRED ; V1_VALIDATED_OFFLINE_PAPER non atteint.
- Action unique : joindre une preuve d'export/transformation existante, assainie, reliant un membre
  de l'archive par SHA-256 à un input_sha256 de rapport, avec identité de contrat attestée.

## D003-B — Portée locale du blocage et lignées indépendantes (approuvée le 2026-09-19)

1. **Faits conservés** : l'audit intégré par PR #244 reste valide. L'archive et ses neuf membres
   sont EXPOSED_DEVELOPMENT ; aucun lien cryptographique source/transformation/rapport ni contract_id
   attesté n'a été trouvé. Le nom d'un fichier ou une étiquette instrument ne prouve pas l'instrument.
2. **Décision de portée** : D003 reste BLOCKED_PROVENANCE pour la validation de la lignée legacy MNQ,
   mais ne bloque plus globalement AGIcore. Les travaux indépendants peuvent continuer sans modifier
   ni masquer ce verdict historique.
3. **Séparation obligatoire** : NQ et MNQ ont des chaînes de preuve distinctes, de la source aux
   résultats paper. Aucun dataset, hash, backtest, replay, résultat ou validation de risque d'une
   filière ne constitue une preuve pour l'autre. Les résultats peuvent être comparés, jamais fusionnés.
4. **Classification** : utiliser NQ_PROVENANCE_CONFIRMED, NQ_PROVENANCE_PARTIAL,
   MNQ_PROVENANCE_CONFIRMED, MNQ_PROVENANCE_PARTIAL, UNKNOWN_INSTRUMENT ou LEGACY_UNVERIFIED selon
   les preuves disponibles. Les entrées historiques NQ_* restent LEGACY_UNVERIFIED/UNKNOWN_INSTRUMENT
   tant que leur seul indice est le nom ; aucune requalification rétrospective n'est autorisée.
5. **Nouvelle lignée** : si la provenance MNQ historique reste insuffisante, créer une lignée MNQ
   propre avec source, nom original, date d'acquisition, contract_id, intervalle, transformations,
   hashes source/dérivé, parent_dataset_sha256 et rôle. Les rôles de nouveaux datasets sont
   DEVELOPMENT, VALIDATION, OOS_TEST ou PAPER_REFERENCE ; l'archive existante conserve son rôle
   EXPOSED_DEVELOPMENT et ne peut devenir OOS.
6. **Protection OOS** : aucun dataset OOS n'est lu, déplacé, reclassé ou utilisé pour optimisation.
   Le choix et l'ouverture d'un OOS restent une gate métier humaine distincte.
7. **Stratégie** : EMA_PULLBACK_V1 est la première stratégie prioritaire, avec validations séparées
   EMA_PULLBACK_V1_NQ et EMA_PULLBACK_V1_MNQ. Les règles ambiguës ne sont jamais complétées
   silencieusement ; une modification métier importante reste une gate humaine.
8. **Tranche suivante** : figer et tester le contrat de manifeste des nouvelles lignées sans acquérir
   de données, lancer de replay, toucher à l'OOS, à la stratégie ou au Risk Engine.
9. **Verdict** : APPROUVÉE. Statut global EXPERIMENTAL ; legacy MNQ BLOCKED_PROVENANCE ;
   V1_VALIDATED_OFFLINE_PAPER non atteint.

## EMA_PULLBACK_V1_MNQ — prédicat pullback initial (approuvé le 2026-09-22)

1. **Décision sans optimisation** : `N = 3`, `X = 8 ticks MNQ = 2,00 points`,
   `wick_cross_ema20 = ALLOWED`, `confirmation_close_correct_side = REQUIRED`.
2. **Fenêtre causale** : seules les trois bougies clôturées `t-3`, `t-2`, `t-1` sont inspectées ;
   la bougie de confirmation `t` n'appartient pas à la fenêtre de pullback.
3. **Distance** : pour chaque bougie, la distance est celle entre la plage fermée `Low..High` et
   l'EMA20 de cette même bougie. Une intersection ou un contact vaut zéro ; la limite huit ticks
   est inclusive. Une seule bougie admissible dans la fenêtre suffit.
4. **Confirmation directionnelle** : LONG impose strictement `Close[t] > EMA20[t]` ; SHORT impose
   strictement `Close[t] < EMA20[t]`. `Close[t] == EMA20[t]` ne confirme aucun côté.
5. **Temporalité** : décision uniquement après clôture de `t`, sans lookahead ; exécution au plus
   tôt sur `t+1`.
6. **Fail-closed** : ce prédicat n'est pas un signal complet. La pente EMA20 et le croisement MACD
   restent obligatoires ; leur définition machine ne peut pas être remplacée par une valeur par
   défaut. Les sorties et filtres de session restent eux aussi à formaliser.
7. **Frontières** : aucune donnée OOS, optimisation, métrique de performance, modification du Risk
   Engine, connexion broker ou opération de trading n'est autorisée par cette décision.
8. **Verdict** : `EMA_PULLBACK_V1_MNQ_PULLBACK_PREDICATE = PASS` ; formalisation globale arrêtée à
   `BLOCKED_HUMAN_GATE — EMA20_SLOPE_FORMULA_REQUIRED`.

## EMA_PULLBACK_V1_MNQ — pente EMA20 initiale (approuvée le 2026-09-23)

1. **Décision sans optimisation** : `K = 3` et
   `ema20_slope_points_per_bar = (EMA20[t] - EMA20[t-3]) / 3`.
2. **Seuil** : `minimum_slope_threshold = 0,0 point/bar`. LONG exige strictement une pente
   supérieure à zéro ; SHORT exige strictement une pente inférieure à zéro. Zéro et égalité au
   seuil sont refusés.
3. **Précision** : toute valeur strictement positive ou négative qualifie son seul côté, même de
   très faible amplitude. Aucun filtre de force de pente n'est ajouté à V1.
4. **Temporalité** : le calcul est effectué après la clôture de `t`, uniquement à partir de
   `EMA20[t]` et `EMA20[t-3]`. Les deux indices doivent matérialiser exactement cet écart causal.
5. **Fail-closed** : warmup inférieur à trois bougies clôturées, mauvais indice, côté implicite ou
   valeur non finie sont refusés ; aucun point futur n'est accepté.
6. **Portée** : le calcul consomme des valeurs EMA20 déjà établies. Il ne définit pas l'amorçage de
   l'EMA20 et ne produit pas seul un signal ou une exécution.
7. **Frontières** : aucune donnée, OOS, optimisation, replay, métrique de performance, modification
   du Risk Engine, connexion broker ou opération de trading n'est autorisée par cette décision.
8. **Verdict** : `EMA_PULLBACK_V1_MNQ_EMA20_SLOPE = PASS` ; formalisation globale arrêtée à
   `BLOCKED_HUMAN_GATE — MACD_CROSS_DEFINITION_REQUIRED`, sans présumer les paramètres MACD.

## EMA_PULLBACK_V1_MNQ — MACD initial et assemblage d'entrée (approuvés le 2026-09-23)

1. **Décision sans optimisation** : MACD `fast = 12`, `slow = 26`, `signal = 9` ; ligne MACD
   `EMA12(Close) - EMA26(Close)` et ligne signal `EMA9(MACD_LINE)`. Les deux moyennes sont des EMA.
2. **Amorçage unique** : réutiliser directement la fonction publique déterministe du replay,
   amorcée au premier close avec `alpha = 2 / (period + 1)`. Aucune autre méthode de seed n'est créée.
3. **Croisement LONG** : `MACD[t-1] <= SIGNAL[t-1]` et `MACD[t] > SIGNAL[t]`.
   **Croisement SHORT** : `MACD[t-1] >= SIGNAL[t-1]` et `MACD[t] < SIGNAL[t]`.
4. **Égalité et validité** : l'égalité à `t-1` est admise ; l'égalité à `t` est refusée. Le croisement
   est valide uniquement sur la bougie de confirmation clôturée `t` et n'est jamais réutilisé.
5. **Warmup fail-closed** : 35 bougies causales et contiguës sont nécessaires pour EMA26, EMA9 du
   MACD et les deux points du croisement. Sinon `INSUFFICIENT_WARMUP` et `NONE` sont obligatoires.
6. **Assemblage** : un signal non exécutable LONG/SHORT existe seulement si pullback + clôture du bon
   côté + pente EMA20 + croisement MACD qualifient tous le même côté et la même bougie `t`.
7. **Temporalité** : seules les données clôturées jusqu'à `t` sont consommées ; toute valeur de `t+1`
   est ignorée. Un signal formé à `t` ne permet une exécution qu'au plus tôt sur `t+1`.
8. **Portée** : aucun PnL, dataset, OOS, replay de marché, optimisation, Risk Engine, broker ou ordre.
   La sortie de position, les stops, objectifs et filtres de session restent hors de ce sous-contrat.
9. **Verdict** : `EMA_PULLBACK_V1_MNQ_MACD = PASS` et
   `EMA_PULLBACK_V1_MNQ_ENTRY_SIGNAL = PASS` ; prochaine gate métier unique :
   `BLOCKED_HUMAN_GATE — EMA20_POSITION_EXIT_RULE_REQUIRED`.

## EMA_PULLBACK_V1_MNQ — sortie principale EMA20 (approuvée le 2026-09-23)

1. **Décision sans optimisation** : LONG sort uniquement si `Close[t] < EMA20[t]` ; SHORT sort
   uniquement si `Close[t] > EMA20[t]`.
2. **Égalité** : `Close[t] == EMA20[t]` produit `HOLD` quel que soit le côté de la position.
3. **Mèches** : une mèche traversant EMA20 ne suffit jamais. LONG conserve la position si
   `Close[t] >= EMA20[t]` ; SHORT la conserve si `Close[t] <= EMA20[t]`.
4. **Temporalité** : la décision utilise uniquement la bougie clôturée `t`. Toute donnée postérieure
   est ignorée et la mutation de `t+1` ne peut changer le résultat.
5. **Exécution** : aucune exécution n'est permise sur `t`. Le résultat indique seulement que le
   premier indice possible est `t+1`, sans fixer type d'ordre, prix ou fill.
6. **Fail-closed** : la bougie `t` doit être présente exactement une fois ; absence, doublon, côté
   implicite ou indice invalide sont refusés.
7. **Portée** : `stop_loss`, `take_profit`, `trailing_stop`, `breakeven` et priorité entre sorties
   restent explicitement non définis. Aucun OOS, PnL, replay de données ou Risk Engine n'est touché.
8. **Verdict** : `EMA_PULLBACK_V1_MNQ_EMA20_POSITION_EXIT = PASS` ; prochaine gate métier unique :
   `BLOCKED_HUMAN_GATE — NEXT_BAR_EXECUTION_MODEL_REQUIRED`.

## EMA_PULLBACK_V1_MNQ — amendement toucher/proximité t-2 (approuvé le 2026-09-26)

1. **Position obligatoire** : dans la fenêtre ordonnée `t-3`, `t-2`, `t-1`, la « deuxième
   bougie » est exactement `t-2`.
2. **Distance inclusive** : la plage de `t-2` doit toucher/croiser son EMA20 ou s'en approcher à
   `<= 8 ticks MNQ`, soit `<= 2,00 points`. Une extrémité ou une mèche traversante vaut zéro.
3. **Limite** : exactement huit ticks qualifie ; toute distance supérieure, notamment neuf ticks,
   échoue.
4. **Non-substitution** : une condition admissible sur `t-3`, sur `t-1` ou sur la bougie de
   confirmation `t` ne remplace pas la condition obligatoire de `t-2`.
5. **Règles inchangées** : clôture directionnelle stricte en `t`, pente EMA20 et croisement MACD
   restent tous obligatoires ; décision sur bougie clôturée et aucun lookahead.
6. **Portée** : aucune optimisation, donnée OOS, métrique de performance, modification du Risk
   Engine, connexion broker ou opération de trading.
7. **Verdict** : `EMA_PULLBACK_V1_MNQ_T_MINUS_2_TOUCH_OR_PROXIMITY = PASS` ; prochaine gate métier unique :
   `BLOCKED_HUMAN_GATE — NEXT_BAR_EXECUTION_MODEL_REQUIRED`.
