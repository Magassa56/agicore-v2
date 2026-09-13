# AGIcore Trading V1 — Master plan

## Mandat (2026-09-12)

MNQ uniquement ; NQ interdit ; 1 à 2 contrats maximum en paper simulé.
OOS immuable. Aucun compte réel, Apex réel, broker ou connexion NinjaTrader réelle.
Risk Engine obligatoire ; aucune modification de risque pour améliorer un résultat.
GitHub est la source de vérité. Lire ce fichier, AGICORE_CURRENT_STATE.md,
AGICORE_DECISIONS.md et AGICORE_RUN_LOG.md à chaque reprise, puis vérifier GitHub/CI.

## Gates ordonnées

1. Fondations SINK-A/B1/B2/B3 et Gate 6.3C : intégrées, tests ciblés vérifiés.
2. Audit post-SINK-B3 : réalisé ; composition durable bout en bout non démontrée.
3. Décision humaine sur le profil runtime obligatoire : D001 approuvée le 2026-09-12.
4. Implémentation de la composition approuvée, identité persistante, reprise complète,
   ACK après acceptation durable et achèvement séparé. Injection de crash à chaque frontière.
   Première correction : effet mémoire direct canonique idempotent (D002), fusionnée via PR #240.
   Reconstruction L5/outbox/inbox intégrée le 2026-09-13 par PR #241, merge
   6c3c6bb5299e0fe8ee6db646e94b79fb4bed45df ; CI #163 success. Ce résultat vaut pour le profil
   offline borné approuvé par D001 et ne démontre pas encore la reprise du runtime global complet.
5. Replay offline MNQ synthétique avec risque inchangé, rejets, conflits, doublons,
   dépassements de quantité et reprise sans double effet. Comparaison indépendante des journaux.
   Gate 5 vérifiée le 2026-09-13 pour tous les composants obligatoires du profil offline D001 :
   test relancé sur main d41103265, 24 passed in 30.01s. Les neuf crashes, retries, refus +2,
   incohérences et comparaison indépendante sont couverts. RuntimeEngine, SignalLoopOrchestrator
   et RuntimeEventBridge restent hors garantie conformément à D001 ; aucune extension implicite.
6. Provenance des données de développement et protocole quantitatif figé ; les expériences
   rejetées restent rejetées. Aucun nouvel OOS sans réservation préalable.
   BLOCKED_HUMAN_GATE : D003 doit fixer timestamps/fuseau/DST, rollover/contrats, OHLCV/volume,
   sessions/jours fériés/clôtures anticipées, hash/période et frontières développement/OOS.
7. Paper local simulé borné, persistant, reproductible ; revue humaine avant intégration sensible.
8. Documentation, preuves de CI/tests/replay et rapport final sans revendication de rentabilité
   non démontrée. V1_READY_FOR_HUMAN_GATE puis V1_VALIDATED_OFFLINE_PAPER seulement sur preuves.

## Continuité

Exécuter automatiquement les tâches non bloquées. Mettre à jour l'état et le journal après
chaque tâche. Aucun passage automatique d'une gate architecturale ou fusion sensible.
Les tests de composants verts ne constituent pas une preuve de reprise de tout le runtime.

La stratégie personnelle EMA pullback (pente, croisement MACD, sortie à clôture sous EMA20)
est distincte de EMA19/50 V3 rejetée. Formalisation exacte requise avant évaluation.
