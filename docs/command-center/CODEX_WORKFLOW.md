# Codex Workflow — Command Center

Ce workflow complète `AGENTS.md`. En cas de conflit, `AGENTS.md` prévaut.

## Boucle standard

1. Lire `ROADMAP.md` et `PROJECT_STATUS.md`.
2. Sélectionner uniquement le prochain jalon autorisé.
3. Transformer le jalon en une tâche bornée avec critères d'acceptation mesurables.
4. Créer/utiliser une branche dédiée.
5. Modifier le minimum de fichiers nécessaires.
6. Exécuter tests ciblés puis tests élargis selon le risque.
7. Produire preuves : commandes, résultats, diff, état Git.
8. Ouvrir une PR courte ; ne jamais fusionner sans décision humaine.
9. Après fusion validée, mettre à jour `PROJECT_STATUS.md` et si nécessaire `ROADMAP.md`.

## Conditions de démarrage d'une tâche

Une tâche est prête seulement si elle contient :

- objectif unique ;
- périmètre explicite ;
- fichiers ou modules probables ;
- critères d'acceptation ;
- tests attendus ;
- risques/sécurité ;
- éléments explicitement hors périmètre.

## Politique de priorité

- P1 Trading peut générer du travail technique actif.
- P2 BusinessPilot et P3 Biotech ne doivent pas modifier le cœur trading dans ce dépôt sans une décision d'architecture explicite.
- Les projets backlog ne génèrent pas de nouvelles grosses features automatiquement.

## Automatisation autorisée sans validation finale

Codex peut :

- analyser le dépôt ;
- proposer un ticket ;
- coder sur une branche ;
- écrire/renforcer des tests ;
- lancer la CI/tests ;
- préparer une PR ;
- documenter les résultats.

Codex doit STOP avant :

- fusion sur `main` ;
- déploiement production ;
- accès broker/compte réel ;
- ordre réel ;
- dépenses ;
- suppression irréversible ;
- modification de secrets ;
- action agricole réelle ou recommandation opérationnelle non validée d'herbicide.

## Critère de fermeture

Une tâche n'est `DONE` que si :

- les critères d'acceptation sont satisfaits ;
- les tests exigés passent ;
- aucun fichier hors périmètre n'est modifié ;
- les risques résiduels sont documentés ;
- la PR est prête à être revue humainement.

## Synchronisation ChatGPT ↔ Codex

ChatGPT agit comme gestionnaire de portefeuille : relit Roadmap, PR, CI et statut, puis formule le prochain travail borné. Codex agit comme ingénieur d'exécution : implémente, teste et prépare la PR. GitHub constitue l'état partagé permanent entre les deux.
