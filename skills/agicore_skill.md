# Skill — AGIcore-v2 (référence interne du repo)

> Version légère du skill, vivant dans le repo. Pour la version installable Claude/Cowork (avec frontmatter), voir `outputs/agicore-master-context/SKILL.md`.

---

## Triggers (mots-clés d'activation)

Activer ce contexte uniquement quand l'utilisateur mentionne explicitement :

- `AGIcore`
- `agicore-v2`
- `Magassa56`
- `World Model`
- `NinjaTrader`
- `agent_orchestrator`
- `ninjatrader_connector`

> Volontairement étroit. Les triggers larges (`code`, `agent`, `cloud`) sont exclus pour éviter le déclenchement intempestif.

---

## Mission

Activer le mode orchestration AGIcore-v2 : adopter l'identité système définie dans `CLAUDE.md`, charger les documents spécialisés au besoin, respecter les règles absolues.

---

## Références (à charger à la demande)

| Document | Contenu |
|---|---|
| `CLAUDE.md` | Identité, règles, autorisations, format réponse |
| `docs/architecture.md` | World Model 5 couches — implémentation |
| `docs/world_model.md` | Fondations conceptuelles |
| `docs/trading.md` | NinjaTrader, stratégies, risk |
| `docs/orchestration.md` | Patterns, communication, LLMs |
| `docs/cloud.md` | AWS, GCP, CI/CD, coûts |
| `docs/cnc.md` | 3D, G-code, machines |
| `docs/memory.md` | STM / LTM, contrats |
| `prompts/trading_agent.md` | Prompt agent trading |
| `prompts/orchestrator_agent.md` | Prompt orchestrator |
| `prompts/audit_agent.md` | Prompt agent audit |
| `prompts/coding_agent.md` | Prompt agent coding |

---

## Règles critiques (rappel rapide)

- Respecter strictement l'architecture World Model (5 couches, pas de modification sans validation)
- Branches : `feature/*` pour le dev. `main` reste stable.
- Tests pytest obligatoires sur chaque module
- Aucun secret hardcodé
- Push sur `main`, déploiement cloud, suppression de fichier → demander confirmation
- Toute décision importante d'agent → loggée en LTM

---

## Format de réponse

```
Layer concerné          : Lx
Modules concernés       : ...
Actions effectuées      : ...
Tests exécutés          : ...
Fichiers créés/modifiés : ...
Risques éventuels       : ...
Prochaine étape suggérée : ...
```
