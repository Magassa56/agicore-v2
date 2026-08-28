# AGIcore Command Center

Ce dossier documente la gouvernance des travaux AGIcore. Il ne constitue ni une autorité transactionnelle ni un orchestrateur runtime.

## Architecture autoritaire

| Composant | Responsabilité |
|---|---|
| ChatGPT Work | Orchestration générale, coordination des travaux, suivi des décisions et interaction humaine |
| Codex | Ingénierie logicielle, analyse du dépôt, implémentation, tests et production des diffs de revue |
| GitHub | Source de vérité du code, versioning, branches, PR, revues, CI et décisions d'intégration |
| AGIcore | Moteur spécialisé persistant : trading, risque, mémoire événementielle, World Model, replay et déterminisme |
| Humain | Autorisation finale des changements sensibles, commits, publications et passages vers paper/live |

ChatGPT Work coordonne les activités générales, mais ne remplace jamais les autorités transactionnelles, les journaux persistants, le Risk Engine ou les contrôles fail-closed d'AGIcore.

## Positionnement produit

La priorité est **AGIcore Trading V1**. AGIcore conserve les capacités métier qui justifient son existence : mémoire événementielle persistante, World Model, Risk Engine, Trading Engine, exécution déterministe, replay, audit, évaluation de politiques, Paper Loop et apprentissage contrôlé.

AGIcore n'est plus présenté comme l'orchestrateur universel des outils et services. Cette spécialisation :

- réduit la complexité d'orchestration interne ;
- évite de dupliquer les capacités générales de ChatGPT Work ;
- concentre AGIcore sur ses avantages métier ;
- améliore persistance, auditabilité et déterminisme ;
- accélère Trading V1 sans intégrer prématurément les travaux en revue.

## Documents

- `ROADMAP.md` : ordre des jalons Trading V1 ;
- `PROJECT_STATUS.md` : statuts Git et état factuel des travaux ;
- `CODEX_WORKFLOW.md` : passage gouverné de l'objectif humain à l'intégration GitHub ;
- `AGENTS.md` à la racine : autorité de gouvernance Codex du dépôt.

## Frontière de sécurité

Cette réorientation est exclusivement documentaire :

- aucune modification du live trading ;
- aucune connexion automatique à NinjaTrader, Alpaca, IBKR ou un autre broker ;
- aucun ordre réel et aucun accès à un compte réel ;
- aucun accès, déplacement, affichage ou changement d'authentification ou de secret ;
- séparation maintenue entre paper trading et live trading ;
- toute activation externe exige une décision humaine et une Gate dédiée.
