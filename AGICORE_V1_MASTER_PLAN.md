# AGIcore Trading V1 — Master plan

## Mandat (mis à jour le 2026-09-19)

NQ et MNQ sont deux filières indépendantes ; aucune preuve ne passe de l'une à l'autre.
La limite MNQ existante reste 1 à 2 contrats maximum en paper simulé. Aucune limite NQ
n'est déduite de celle de MNQ ; elle exige une configuration Risk Engine approuvée séparément.
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
6. Provenance des données de développement et protocole quantitatif figé séparément pour NQ et MNQ ;
   les expériences rejetées restent rejetées. Aucun nouvel OOS sans réservation préalable.
   L'audit D003 du 2026-09-15 reste BLOCKED_PROVENANCE pour la lignée legacy MNQ : aucun lien
   cryptographique source/rapport ni identité réelle de contrat n'est établi. L'archive existante
   reste EXPOSED_DEVELOPMENT et le candidat CANDIDATE_MNQ_NOT_LINKED. Les entrées NQ_* restent
   LEGACY_UNVERIFIED/UNKNOWN_INSTRUMENT lorsqu'un nom est leur seul indice. Depuis D003-B, ce blocage
   est local : une nouvelle lignée MNQ propre et une lignée NQ indépendante peuvent avancer.
   Chaque nouvelle lignée doit fixer timestamps/fuseau/DST, rollover/contrats, OHLCV/volume,
   sessions/jours fériés/clôtures anticipées, hash/période et frontières développement/OOS.
7. Paper local simulé borné, persistant, reproductible ; revue humaine avant intégration sensible.
8. Documentation, preuves de CI/tests/replay et rapport final sans revendication de rentabilité
   non démontrée. V1_READY_FOR_HUMAN_GATE puis V1_VALIDATED_OFFLINE_PAPER seulement sur preuves.

## Continuité

Exécuter automatiquement les tâches non bloquées. Mettre à jour l'état et le journal après
chaque tâche. Autorisation Git permanente du 2026-09-15 : commits, branches, push, PR et fusion
après revue du diff exact, tests concernés, diff-check, CI verte et contrôle des conflits/secrets/périmètre.
Arrêt seulement à une vraie gate métier : données, OOS, stratégie, Risk Engine ou trading réel ;
aucune validation V1 sans preuves complètes. Aucun force-push ni réécriture d'historique.
Les tests de composants verts ne constituent pas une preuve de reprise de tout le runtime.

La stratégie personnelle EMA_PULLBACK_V1 (EMA20, clôture de confirmation, pente EMA,
croisement/confirmation MACD et sorties causales) est distincte de EMA19/50 V3 rejetée.
Ses règles exactes doivent être formalisées avant évaluation. Les validations
EMA_PULLBACK_V1_NQ et EMA_PULLBACK_V1_MNQ restent entièrement séparées ; si leurs paramètres
divergent, elles reçoivent des versions distinctes. Aucun choix ambigu n'est inventé.
