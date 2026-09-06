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

Ces capacités sont présentes sur `main` au commit
`903e035a36077f38c054dfd006b8dba4de11614b`, validé par `AGIcore CI #154`.

## Unique prochaine gate pré-paper

**SINK-B3 — EventBus canonique et replay croisé** est la seule prochaine gate
identifiée. Cette roadmap ne l’implémente pas.

La gate devra prouver, sur une branche et dans une PR dédiées :

1. une API canonique dont le bus résout lui-même le manifest de handlers ;
2. l’injection explicite de l’autorité durable dans le runtime ;
3. un ACK L5 lié à l’événement durable `EMISSION_ACCEPTED` exact ;
4. un replay croisé cohérent entre outbox, inbox et journal EventBus ;
5. une progression des handlers distincte de l’acceptation de l’émission ;
6. les reprises après crash et redémarrage SQLite sans duplication ;
7. le refus fail-closed des preuves absentes, conflictuelles ou falsifiées.

Le chemin reste offline et SQLite. EventBus legacy ne devient pas une autorité.
Cette gate n’active aucun broker, compte, ordre, paper trading ou live trading.

Après SINK-B3, la prochaine décision sera prise à partir des preuves intégrées et
de la CI ; aucune gate supplémentaire n’est pré-sélectionnée ici.

## Backlog protégé

BusinessPilot, Biotech/Agritech, Engineering, CAO, infrastructure IA locale, atelier 3D/CNC et robotique restent conservés mais ne détournent pas la priorité Trading V1 sans nouvelle décision humaine.
