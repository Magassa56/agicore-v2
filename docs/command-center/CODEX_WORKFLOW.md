# Workflow gouverné — ChatGPT Work, Codex, GitHub et AGIcore

Ce workflow complète `AGENTS.md`. En cas de conflit, `AGENTS.md` prévaut.

## Responsabilités

| Acteur | Responsabilité opérationnelle |
|---|---|
| Humain | Fixe l'objectif, les limites et les autorisations sensibles ; décide des commits, publications et activations paper/live |
| ChatGPT Work | Coordonne le plan général, les dépendances, les décisions et la supervision humaine |
| Codex | Inspecte le dépôt, implémente dans le périmètre, exécute les validations et produit les diffs |
| GitHub | Conserve le code et l'historique, porte branches, PR, revues, CI et intégrations |
| AGIcore | Exécute seulement les capacités métier déterministes, persistantes, intégrées et autorisées |

ChatGPT Work ne remplace ni les transactions locales d'AGIcore, ni ses autorités persistantes, ni ses contrôles de risque.

## Cycle d'intégration

1. L'humain fixe l'objectif et les limites.
2. ChatGPT Work coordonne et maintient le plan.
3. Codex inspecte, implémente et valide.
4. Codex produit un diff de revue vérifiable.
5. Une revue humaine évalue le diff et les preuves.
6. Le commit local est autorisé séparément.
7. Le changement est publié dans une PR dédiée.
8. La CI et la revue GitHub vérifient le changement publié.
9. La fusion est explicitement autorisée.
10. AGIcore exécute uniquement les capacités intégrées et autorisées.

Chaque étape conserve son statut propre. Un diff, un commit local, une PR et une fusion ne sont jamais interchangeables.

## Conditions de démarrage d'une tâche Codex

Une tâche est prête seulement si elle définit :

- un objectif unique et un périmètre explicite ;
- les fichiers ou modules probables ;
- des critères d'acceptation et tests mesurables ;
- les risques, frontières de sécurité et éléments hors périmètre ;
- l'autorité humaine nécessaire pour toute action externe ou irréversible.

## Autorisations et arrêts

Codex peut, dans le périmètre autorisé : analyser, modifier, tester et produire un diff. Il doit s'arrêter avant toute action qui requiert une autorisation distincte, notamment :

- stage ou commit non autorisé ;
- push, création ou modification de PR non autorisés ;
- fusion sur `main` ou déploiement ;
- modification d'authentification ou de secrets ;
- accès broker, compte réel ou ordre réel ;
- activation paper/live sans Gate dédiée ;
- dépense ou suppression irréversible.

## Critère de fermeture

Une tâche n'est terminée que lorsque ses critères sont prouvés, les validations exigées passent, le périmètre Git est exact et les risques résiduels sont documentés. La disponibilité sur `main` exige en plus publication, CI, revue et fusion explicite.
