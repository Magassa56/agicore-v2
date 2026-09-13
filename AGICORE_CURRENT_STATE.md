# AGIcore current state — checkpoint

Date : 2026-09-13 UTC.
Statut : BLOCKED_HUMAN_GATE — Gate 5 validée pour le profil offline D001 ; contrat de provenance Gate 6 absent.
Branche de vérification : feature/gate5-global-offline-replay-v1.
Base GitHub vérifiée et récupérée : d41103265f3afc5e324a01d45dd66b14bea0d148.

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

## Gate actuelle

BLOCKED_HUMAN_GATE — G6_MNQ_PROVENANCE_CONTRACT. Avant toute lecture de donnée, utilisation OOS
ou intervention NinjaTrader, fournir un contrat traçable pour un jeu de développement permis :
sémantique des timestamps de barres et fuseau/DST ; règle de rollover et identité des contrats ;
sémantique OHLCV/volume ; calendrier de sessions, jours fériés et clôtures anticipées ; hash,
période et frontières garantissant que l'OOS reste réservé. Aucun de ces éléments ne peut être
inféré silencieusement. V1_VALIDATED_OFFLINE_PAPER n'est pas atteint.

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
