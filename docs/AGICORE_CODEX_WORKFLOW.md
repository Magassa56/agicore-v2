# Workflow gouverné AGIcore pour Codex

## Objet

Ce workflow répartit explicitement décision, exécution locale et mémoire Git. Il maintient une barrière humaine avant les actions Git publiées ou irréversibles et conserve une seule priorité principale par mission.

## Les trois niveaux de gouvernance

### 1. GPT-5.6 dans ChatGPT — AGIcore Manager

L'AGIcore Manager :

- priorise la prochaine capacité utilisateur concrète ;
- protège et valide l'architecture ;
- formule ou approuve une phase mesurable ;
- examine le rapport et les preuves fournis par Codex ;
- demande les corrections nécessaires ;
- donne l'autorisation humaine explicite avant commit, push, PR ou fusion selon la barrière annoncée.

Il ne remplace ni les tests locaux ni la CI et ne valide pas une réussite sans preuve.

### 2. Codex CLI GPT-5.6 — Exécution locale

Codex CLI :

- inspecte localement l'état autorisé du dépôt ;
- travaille sur la branche dédiée et dans le budget de fichiers ;
- réalise les modifications prévues ;
- exécute les tests ciblés, les intégrations concernées et la suite complète lorsque raisonnable ;
- corrige ses propres erreurs dans le périmètre de la mission ;
- contrôle le diff et produit le rapport final ;
- s'arrête avant commit tant que l'autorisation humaine n'est pas donnée.

Codex ne choisit pas seul une nouvelle priorité une fois l'objectif terminé.

### 3. GitHub — Mémoire officielle

GitHub conserve la mémoire officielle et auditable du projet :

- commits atomiques et autorisés ;
- pull requests courtes ;
- résultats de CI ;
- commentaires et décisions de revue ;
- historique de fusion.

Une branche locale ou une conversation n'est pas un substitut à cette mémoire officielle. La fusion reste soumise à une CI verte et à l'autorisation de l'AGIcore Manager.

## Cycle standard d'une phase

```text
Phase proposée
→ approbation humaine
→ synchronisation de main
→ création d'une branche dédiée
→ mission /goal
→ analyse
→ modifications
→ tests ciblés
→ suite complète
→ rapport
→ STOP avant commit
→ revue ChatGPT
→ commit autorisé
→ push autorisé
→ PR
→ CI
→ autorisation de fusion
→ fusion
→ synchronisation locale
→ phase suivante
```

Chaque flèche est une transition contrôlée. Une erreur suspend la transition suivante jusqu'à correction ou décision humaine. Le commit, le push, la PR, la fusion, le tag, la publication et le déploiement ne sont jamais implicites.

## Utilisation de `/goal`

Commandes de pilotage :

```text
/goal <objectif>
/goal
/goal pause
/goal resume
/goal clear
```

- `/goal <objectif>` démarre une mission persistante explicite.
- `/goal` affiche l'objectif actif et son état.
- `/goal pause` suspend l'exécution sans changer l'objectif.
- `/goal resume` reprend l'objectif suspendu.
- `/goal clear` efface l'objectif lorsque son abandon ou sa clôture est décidé.

Un goal :

- ne contient qu'un objectif principal ;
- définit une condition de réussite mesurable ;
- possède un budget maximal de fichiers ;
- déclare clairement ses non-objectifs ;
- définit les barrières nécessitant une validation humaine ;
- autorise Codex à corriger ses propres erreurs dans le périmètre ;
- n'autorise pas Codex à choisir seul une nouvelle priorité après achèvement.

Le modèle réutilisable se trouve dans `docs/templates/AGICORE_CODEX_PHASE_TEMPLATE.md`.

## Règles de sécurité permanentes

- Le fonctionnement offline est la règle ; le réseau exige une autorisation explicite.
- `data/`, les rapports personnels et les secrets restent hors lecture, hors modification et hors publication.
- Aucun broker réel, ordre réel, compte réel ou position réelle ne doit être utilisé.
- Aucun tag Trading V1, déploiement Cloud Run, package publié ou action de release n'est déclenché sans mission et autorisation spécifiques.
- Le script `scripts/agicore-preflight.ps1` fournit un contrôle local en lecture seule ; il ne remplace pas la revue du diff.
