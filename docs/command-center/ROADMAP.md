# AGIcore Trading V1 — Roadmap

Dernière vérification : 2026-09-06

## Priorité produit

La priorité active est **AGIcore Trading V1**. La roadmap décrit un ordre de preuves et d'autorisations, pas une promesse calendaire.

1. **Stabilité déterministe et persistante** — Fermer les autorités transactionnelles, l'idempotence durable, le replay causal et la reprise après crash.
2. **Exécution offline** — Prouver les chemins canoniques sans réseau, broker, compte ou données réelles.
3. **Paper trading durable** — Activer uniquement après fermeture et revue des Gates pré-paper, avec état persistant et reprise vérifiable.
4. **Observation et apprentissage contrôlés** — Mesurer le Paper Loop et encadrer toute évolution de politique par des preuves rejouables.
5. **Validation quantitative et risque** — Évaluer robustesse, coûts, limites, scénarios adverses et absence de dérive des contrôles de risque.
6. **Live trading futur** — Reste hors périmètre jusqu'à une phase explicitement autorisée, une Gate dédiée et une décision humaine.

Aucune date de passage en live n'est annoncée.

## Capacités AGIcore à consolider

- mémoire événementielle persistante ;
- World Model ;
- Risk Engine et Trading Engine ;
- exécution déterministe ;
- replay et audit ;
- évaluations de politiques ;
- Paper Loop et apprentissage contrôlé.

## Fondations pré-paper intégrées

- autorités mémoire et EventBus SQLite : PR #234 ;
- handler mémoire idempotent avec reprise : PR #235 ;
- Gate 6.3C et exécution L5 déterministe : PR #236 ;
- Controlled Simulation Review Precheck : PR #117 ;
- Observability Verification : PR #78.
- EventBus canonique, ACK durable et replay croisé : PR #238.

Ces capacités sont présentes sur `main` au commit
`248d762038164cd6a58842382e06207baf0e63d0`, validé par `AGIcore CI #157`.

## Unique prochaine phase

L’**audit post-SINK-B3 des écarts pré-paper** est la seule prochaine phase.
Cette roadmap ne préjuge pas de son résultat et n’implémente aucune nouvelle
capacité.

L’audit devra vérifier :

1. si le bootstrap runtime compose réellement les autorités intégrées sans
   configuration implicite ;
2. si une reprise bout en bout manque encore au-delà des preuves par composant ;
3. si les contrôles pré-paper existants couvrent déjà ce dernier écart ;
4. si AGIcore peut revenir aux expériences MNQ offline avec une hypothèse unique
   et un OOS immuable ;
5. quelle unique prochaine gate ou expérience est justifiée par les preuves.

Le chemin reste offline et SQLite. EventBus legacy ne devient pas une autorité.
L’audit n’active aucun broker, compte, ordre, paper trading ou live trading.

Une seule suite sera retenue après l’audit. Aucune gate supplémentaire n’est
pré-sélectionnée ici.

## Backlog protégé

BusinessPilot, Biotech/Agritech, Engineering, CAO, infrastructure IA locale, atelier 3D/CNC et robotique restent conservés mais ne détournent pas la priorité Trading V1 sans nouvelle décision humaine.
