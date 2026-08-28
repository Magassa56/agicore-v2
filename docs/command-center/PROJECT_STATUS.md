# AGIcore Project Status

Dernière mise à jour : 2026-08-28

## Vocabulaire autoritaire

| Statut | Signification |
|---|---|
| `MERGED` | Présent dans la branche principale GitHub après fusion explicite |
| `REMOTE_PR` | Présent dans une PR GitHub mais non fusionné |
| `LOCAL_COMMIT_ONLY` | Commit local non publié sur GitHub |
| `UNCOMMITTED_REVIEW` | Diff local non commité en attente de revue humaine |
| `BLOCKED` | Dépendance architecturale, autorisation ou contrat requis avant poursuite |

Un commit local ou un diff de revue n'est jamais décrit comme intégré, publié ou disponible sur `main`.

## État vérifié des travaux

| Travail | Statut | État exact |
|---|---|---|
| PR #232 — Command Center V2 | `REMOTE_PR` | Documentation architecturale portée par une PR ouverte et non fusionnée ; le HEAD courant visible sur GitHub est autoritaire |
| SINK-A — autorité mémoire idempotente | `LOCAL_COMMIT_ONLY` | Commit local `f420d83d259c2cadf33307b1029554a84b3ff0a3`, non publié |
| SINK-B1 V2 — autorité durable EventBus | `UNCOMMITTED_REVIEW` | Rapport PASS local ; diff encore soumis à revue humaine, sans commit |
| Gate 6.3C V2 | `UNCOMMITTED_REVIEW` | Travail local conservé, non commité et non intégré |
| SINK-B2 | `BLOCKED` | Non démarré ; aucune autorisation d'implémentation dans cette phase |

Les éléments `LOCAL_COMMIT_ONLY` et `UNCOMMITTED_REVIEW` ne font pas partie de la branche principale GitHub.

## Priorité active

**AGIcore Trading V1** reste la priorité produit. Après la gouvernance documentaire, la suite recommandée est une reprise contrôlée de Trading V1, phase par phase, avec revue et autorisation séparées.

AGIcore continue comme moteur métier spécialisé et persistant. Il n'est ni arrêté, ni remplacé, ni transformé en orchestrateur universel.

## Frontières d'activation

- La réorientation documentaire n'active aucune capacité paper ou live.
- SINK-A, SINK-B1 V2 et Gate 6.3C V2 doivent suivre leurs propres revues et décisions d'intégration.
- Aucun résultat local ne vaut présence dans GitHub `main`.
- Toute connexion externe, authentification broker, paper trading durable ou live trading exige sa Gate et une décision humaine explicite.
