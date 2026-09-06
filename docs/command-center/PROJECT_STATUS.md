# AGIcore Project Status

Dernière vérification : 2026-09-06

Source de vérité vérifiée : branche GitHub `main` au commit
`248d762038164cd6a58842382e06207baf0e63d0`. La CI `AGIcore CI #157` de ce
commit est terminée avec la conclusion `success`.

## Vocabulaire autoritaire

| Statut | Signification |
|---|---|
| `MERGED` | Présent dans la branche principale GitHub après fusion explicite |
| `REMOTE_PR` | Présent dans une PR GitHub mais non fusionné |
| `LOCAL_COMMIT_ONLY` | Commit local non publié sur GitHub |
| `UNCOMMITTED_REVIEW` | Diff local non commité en attente de revue humaine |
| `BLOCKED` | Dépendance architecturale, autorisation ou contrat requis avant poursuite |
| `PLANNED` | Prochaine gate identifiée, absente de `main` et non implémentée par cette mise à jour |

Un commit local ou un diff de revue n'est jamais décrit comme intégré, publié ou disponible sur `main`.

## État vérifié des travaux

| Travail | Statut | État exact |
|---|---|---|
| PR #232 et #233 — Command Center V2 et statut post-fusion | `MERGED` | Gouvernance documentaire présente sur `main` |
| SINK-A et SINK-B1 — autorités mémoire et EventBus SQLite | `MERGED` | PR #234 fusionnée le 2026-09-02 ; merge `f64e9536c77f2c545f1a9d44ca05d5eb2006c7c6` |
| SINK-B2 — handler mémoire idempotent | `MERGED` | PR #235 fusionnée le 2026-09-02 ; merge `22a0b36e348e8dfe7803680f97bec6381505751b` |
| Gate 6.3C V2 — exécution L5 déterministe | `MERGED` | PR #236 fusionnée le 2026-09-03 ; merge `aca8192b40c109bc5a840d68eb7f53e255fab3d8` |
| Controlled Simulation Review Precheck | `MERGED` | PR #117 fusionnée le 2026-09-03 ; merge `bd5ee140b3a8c9c0aa58414a230d247b76260833` |
| Observability Verification | `MERGED` | PR #78 fusionnée le 2026-09-03 ; merge `903e035a36077f38c054dfd006b8dba4de11614b` |
| SINK-B3 — EventBus canonique et replay croisé | `MERGED` | PR #238 fusionnée le 2026-09-06 ; merge `248d762038164cd6a58842382e06207baf0e63d0` |
| Audit post-SINK-B3 des écarts pré-paper | `PLANNED` | Unique prochaine phase ; sélectionner une seule gate à partir des preuves intégrées sans l’implémenter dans ce ticket documentaire |

Les anciennes mentions locales de SINK-A, SINK-B1, SINK-B2, SINK-B3 et Gate
6.3C sont supprimées : ces capacités sont désormais présentes sur `main`.

## Priorité active

**AGIcore Trading V1** reste la priorité produit. La seule prochaine phase est
l’**audit post-SINK-B3 des écarts pré-paper**. Cet audit doit déterminer si une
dernière gate d’intégration est nécessaire ou si les expériences MNQ offline
peuvent reprendre ; il n’implémente aucune des deux options.

AGIcore continue comme moteur métier spécialisé et persistant. Il n'est ni arrêté, ni remplacé, ni transformé en orchestrateur universel.

## Frontières d'activation

- La réorientation documentaire n'active aucune capacité paper ou live.
- Toute nouvelle gate issue de l’audit doit suivre sa propre branche, ses tests, sa revue et sa décision d’intégration.
- Un résultat local futur ne vaudra pas présence dans GitHub `main`.
- Toute connexion externe, authentification broker, paper trading durable ou live trading exige sa Gate et une décision humaine explicite.
