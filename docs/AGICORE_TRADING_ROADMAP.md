# AGIcore Trading Roadmap v1

## Principe directeur

La roadmap AGIcore Trading v1 doit rapprocher le projet d'un usage concret, testable et offline.
Ne pas ajouter de nouvelle gate abstraite si elle ne rapproche pas AGIcore d'un usage concret.

## Phases produit concretes

1. Delivery Factory v1
   Standardiser roadmap, issues, branches, taches Codex, tests CI, PR, validation et prochaine phase.

2. Controlled Offline Runner Minimal Implementation
   Construire le plus petit runner offline controle, non connecte a un broker, avec une entree synthetique et une sortie observable.

3. Synthetic Market Scenario
   Definir un scenario de marche synthetique deterministe pour tester le runner sans donnees externes.

4. Simulated Broker Stub
   Ajouter un stub broker simule strictement offline, read-only par defaut, sans ordre reel et sans acces compte.

5. Risk Guard Enforcement
   Appliquer les gardes de risque offline: blocage ordre, blocage mutation position, limites de perte simulees et stop conditions.

6. Journal Writer
   Ecrire un journal offline des observations, decisions simulees, gardes declenches et resultats.

7. Offline Report Markdown/JSON
   Produire un rapport local Markdown et JSON, reproductible, sans service externe.

8. CSV Replay Input
   Accepter un input replay CSV controle et documente, sans obligation d'utiliser `data/`.

9. Strategy Replay Engine
   Rejouer une strategie contre les scenarios synthetiques ou CSV autorises, en observation et simulation offline uniquement.

10. AGIcore Trading v1 Candidate
    Assembler les composants offline valides dans un candidat v1 pret pour revue humaine.

## Definition d'une bonne phase

Une bonne phase cree un artefact utilisable, testable et proche du produit.
Une mauvaise phase ajoute une couche de validation abstraite sans livrer de capacite concrete.

## Contraintes permanentes

- Offline par defaut.
- Sandbox par defaut.
- Aucun secret.
- Aucun broker reel.
- Aucun ordre reel.
- Aucun acces compte reel.
- Aucun transport reseau dans les phases offline.
- Tests locaux et CI obligatoires.
