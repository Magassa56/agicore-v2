# AGENTS.md — Cadre de travail gouverné AGIcore

Ce contrat persistant s'applique à toute mission Codex exécutée dans ce dépôt. Il complète `CLAUDE.md`. En cas de doute, protéger les données et demander une décision humaine avant toute action irréversible ou externe.

## A. Mission

Codex contribue à transformer AGIcore en produit local, stable, sécurisé, testable et utile avec le minimum de complexité nécessaire.

## B. Priorités

Toujours travailler dans cet ordre :

1. sécurité et données personnelles ;
2. fonctionnement offline ;
3. exactitude et déterminisme ;
4. stabilité ;
5. valeur utilisateur ;
6. simplicité ;
7. tests ;
8. documentation ;
9. performance ;
10. nouvelles fonctionnalités ;
11. rentabilité.

## C. Interdictions absolues

Ne jamais :

- modifier, lire, supprimer, ajouter ou versionner `data/` ;
- lire ou modifier des secrets ;
- afficher une clé ou un token ;
- connecter un broker réel ;
- passer un ordre réel ;
- accéder à un compte réel ;
- muter une position réelle ;
- activer un réseau sans autorisation explicite ;
- lancer Cloud Run ;
- publier un package ;
- créer ou pousser un tag ;
- fusionner une PR ;
- pousser directement sur `main` ;
- réécrire l'historique Git ;
- supprimer un fichier utilisateur ;
- contourner ou affaiblir un test ;
- masquer une erreur ;
- déclarer une réussite sans preuve.

## D. Règles de phase

- Une seule priorité produit par phase.
- Une seule branche dédiée.
- Modifications cohérentes et limitées.
- Trois à cinq fichiers maximum par défaut.
- Aucun grand refactoring mélangé à une fonctionnalité.
- Réutiliser les modules existants avant d'en créer de nouveaux.
- Ne pas créer de module Python uniquement pour valider une checklist documentaire.
- Les règles de release vivent dans `docs/`, GitHub ou `tools/`, jamais dans le cœur runtime.
- Ajouter un test de non-régression pour chaque bug corrigé lorsque possible.
- STOP avant commit sauf autorisation explicite.
- STOP avant push, PR, fusion, tag, publication ou déploiement selon la mission.

## E. Contrôles obligatoires

Avant modification :

```text
git status --short
git diff --check
```

Après modification :

- exécuter les tests ciblés ;
- exécuter les tests d'intégration concernés ;
- exécuter la suite complète lorsque raisonnable ;
- exécuter `git diff --check` ;
- exécuter `git status --short` ;
- exécuter `git diff --name-only` ;
- vérifier qu'aucun fichier hors périmètre n'est modifié.

Toute erreur doit être corrigée dans le périmètre avant de poursuivre. Une erreur non corrigeable, un fichier suivi modifié sans explication ou une violation de sécurité impose un STOP avec preuves.

## F. Rapport obligatoire

Toujours terminer exactement avec les rubriques suivantes, dans cet ordre :

```text
PHASE       : <nom de la phase>
STATUS      : OK ou BLOCKED
NEXT        : <arrêt ou action soumise à autorisation>

Résultat
État du produit
Modifications
Tests
Sécurité
Valeur utilisateur et rentabilité
Risques restants
Décisions demandées
Prochaine étape recommandée
Git status
```

Chaque réussite annoncée doit être étayée par une commande, un test ou un diff vérifiable.

## G. Politique Git

- `main` reste protégée.
- Utiliser une branche dédiée par phase.
- Créer un commit seulement après validation humaine.
- Garder les PR courtes et limitées à leur objectif.
- Exiger une CI verte.
- Fusionner uniquement après autorisation de l'AGIcore Manager.
- Supprimer les branches fusionnées seulement après vérification.
