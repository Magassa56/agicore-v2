# AGIcore current state — checkpoint

Date : 2026-09-12 UTC.
Statut : BLOCKED_HUMAN_GATE — décision architecturale D001.
Branche de reprise : feature/v1-master-state-sink-audit.
Base GitHub vérifiée : c1316a06efabb1ee9688bfd433f9df67c46cc47b.
CI main : AGIcore CI #159, success, run 34019130531.
PR ouvertes au contrôle initial : aucune.

## Accompli

- Recherche des quatre fichiers : absents du main et du worktree ; initialisation explicite.
- SINK-B3 déjà intégré par PR #238, précédé de #234, #235 et #236.
- 159 tests ciblés et d'intégration passent ; 4 avertissements SQLite de dépréciation.
- Contrat effect_id / unicité mémoire / acceptance / completion / fencing / replay présent.
- Audit : RuntimeEngine exige une injection explicite de l'autorité ; par défaut elle est absente.
- ExecutionAgent conserve un effet mémoire direct create_event sous apply_effect ; l'inbox
  documente une idempotence en processus uniquement, non persistée au redémarrage.
- Le test de replay croisé redémarre l'autorité SQLite mais conserve le service L5 et son inbox
  en mémoire. Il ne démontre donc pas un redémarrage complet du processus.

## Prochain point exact

Faire décider D001 dans AGICORE_DECISIONS.md : profil offline avec handlers durables explicitement
obligatoires, SignalLoopOrchestrator et RuntimeEventBridge exclus de la garantie durable initiale,
ou inclusion obligatoire nécessitant leur persistance. Ne pas implémenter ce choix implicitement.
Après décision : ouvrir la branche du ticket D001, figer le manifeste, écrire la preuve de crash
complète avant la correction. Ne pas toucher au Risk Engine ni aux données OOS.

## Limites

V1 non validée offline/paper. Aucun test de stratégie ni prix consulté pendant cet audit.
Les rapports antérieurs de provenance et stratégies ne sont pas une validation runtime.
Les quatre fichiers de cette phase sont documentaires ; aucun code runtime modifié.
