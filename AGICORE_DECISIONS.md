# AGIcore decisions

## D001 — Profil durable post-SINK-B3 (proposition, non approuvée)

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
9. **Verdict** : ATTENDRE — BLOCKED_HUMAN_GATE.

**Décision demandée** : approuver ce profil offline initial avec SignalLoopOrchestrator et
RuntimeEventBridge hors garantie durable, ou exiger leur inclusion durable avant toute validation V1.
Cette proposition n'a pas valeur d'autorisation et ne supprime aucune exigence de reprise complète
des composants effectivement obligatoires du profil retenu.
