# PR #341 — Autorisation strictement limitée à la CI authentique

Date : 17 novembre 2026  
Dépôt : `Magassa56/agicore-v2`  
PR : #341 — `AGICORE_G2C_V3_ONE_SHOT_EXECUTION_GUARD_IMPLEMENTATION`  
HEAD de livraison vérifié : `eccf82e263ddcf598004a30185cad5a986eea1fa`  
Base `main` protégée : `b86453d880b32245b046e5cb7dfa3bf74862dc7c`

## Périmètre autorisé

Le propriétaire a explicitement autorisé **uniquement** la validation CI de la PR #341. Cette autorisation inclut les deux contrôles de protection authentiques sur le HEAD exact :

- `Full regression suite` : suite de tests complète, petits workers synthétiques existants (notamment 39/57/64/201/401/601 observations), sondes de supervision, tests Manager et SQLite.
- `Restricted portable nonworker tests` : sélection portable authentique de 85 cas.

Le workflow `.github/workflows/agicore-ci.yml` conserve les contrôles de SHA du checkout pour ces deux jobs. Le présent fichier non exécutable est ajouté dans un **nouveau commit sans directive de saut de CI** pour permettre l'exécution habituelle des contrôles obligatoires de cette PR.

## Interdictions et intégrité

**AUCUNE autorisation** de campagne G2C enregistrée à 1 000 ou 5 000 observations, de `workflow_dispatch`, d'installation/activation du futur mécanisme one-shot, de création du vrai claim ref, de modification du ruleset GitHub, d'accès réel DEVELOPMENT/OOS, d'ordre broker ou de fusion de PR.

Le plan canonique V3 reste `4baa39605bd3b05bd177681d0c382e923237541c770af648f35b83f47dcf552c`. Le contrôleur inerte, la simulation du workflow sous `docs/operations/`, les tests, les sources et les preuves historiques de la PR #341 doivent rester inchangés. L'éventuel succès de la CI n'autorise pas la fusion.

**Ce document n'est pas une autorisation cryptographique indépendante d'activation de campagne**, ne contient aucun `run_id` approuvé et ne peut servir de preuve pour déclencher le replay G2C.

Statut au moment du commit : `CI_ONLY_AUTHORIZED`, `G2C_5000=NOT_AUTHORIZED`, `MERGE=NOT_AUTHORIZED`.
