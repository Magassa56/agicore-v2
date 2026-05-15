# Architecture AGIcore-v2

> Spécification d'architecture concrète. Pour la couche conceptuelle (théorie du World Model), voir `world_model.md`.

---

## 1. Vue d'ensemble

AGIcore-v2 est un système multi-agents organisé en 5 couches verticales (L1 → L5). Chaque couche a une responsabilité unique et communique avec les couches adjacentes via des contrats explicites (messages JSON, événements, ou appels typés).

```
┌──────────────────────────────────────────────┐
│  L5 — Action          (NinjaTrader, APIs)    │
├──────────────────────────────────────────────┤
│  L4 — Planning        (orchestrator)         │
├──────────────────────────────────────────────┤
│  L3 — Intelligence    (Claude, GPT fallback) │
├──────────────────────────────────────────────┤
│  L2 — State / Memory  (Redis, SQLite, PG)    │
├──────────────────────────────────────────────┤
│  L1 — Perception      (collecte data)        │
└──────────────────────────────────────────────┘
```

---

## 2. Responsabilités par couche

### L1 — Perception
- Collecte de données externes : APIs marché, fichiers, événements, signaux, logs, messages d'agents
- Normalisation minimale (parsing, validation de schéma)
- Émission d'événements vers L2 / L4
- État par défaut : `IDLE` (poll-driven ou push-driven selon la source)

### L2 — State / Memory
- Mémoire court terme (STM) : Redis ou SQLite local
- Mémoire long terme (LTM) : PostgreSQL + vector store (Qdrant, Chroma, ou pgvector)
- État système : registre des agents, statut, contexte de session
- Historique des tâches et décisions

### L3 — Intelligence (anciennement Dynamics / Intelligence)
- Raisonnement, analyse, scoring
- Évaluation des risques
- Décision stratégique
- LLMs : Claude API (principal), GPT en fallback
- Pas d'effet de bord direct — émet des intentions vers L4

> Module Python : `src/agicore/l3_intelligence/`

### L4 — Planning / Orchestration
- Reçoit les intentions de L3
- Décompose en tâches exécutables
- Distribue aux workers (agents)
- Gère la queue, les priorités, les dépendances
- Patterns : supervisor / worker, event-driven, message queue

### L5 — Action
- Exécute concrètement : appels NinjaTrader, APIs externes, automation, écriture fichier
- Écrit toujours via un connector typé (jamais d'appel direct dispersé)
- Logue chaque action vers L2

---

## 3. Communication inter-couches

| De → Vers | Mécanisme | Format |
|---|---|---|
| L1 → L2 | Insert direct + event | JSON event |
| L1 → L4 | Event bus | JSON event |
| L3 → L4 | Intention | `Intention(type, payload, priority)` |
| L4 → L5 | Task assignment | `Task(id, agent_id, action, params)` |
| L5 → L2 | Log + state update | structured log |

Convention : tout message inter-couches porte au minimum `task_id`, `agent_id`, `timestamp_utc`.

---

## 4. Organisation des fichiers (cible — World Model uniquement)

```
agicore-v2/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── docs/
├── prompts/
├── skills/
├── src/
│   └── agicore/
│       ├── __init__.py
│       ├── core/                       (utils transverses, config, logging)
│       ├── agents/                     (implémentations concrètes d'agents)
│       ├── l1_perception/
│       ├── l2_memory/
│       ├── l3_intelligence/
│       ├── l4_planning/
│       │   └── agent_orchestrator.py
│       └── l5_action/
│           ├── ninjatrader_connector.py
│           ├── strategy_ema_rsi.py
│           ├── backtesting_engine.py
│           ├── risk_manager.py
│           ├── trade_logger.py
│           └── performance_reporter.py
├── tests/
│   ├── unit/
│   └── integration/
└── logs/
```

**Aucune structure legacy** : pas de `backend/`, `agents/`, `memory/`, `orchestration/`, `trading/` à la racine. Tout vit sous `src/agicore/`.

---

## 5. Règles d'immutabilité

Sans validation explicite de J'ai :
- ne pas modifier la structure des 5 couches
- ne pas déplacer les modules entre couches
- ne pas renommer les dossiers `l1_perception`, `l2_memory`, `l3_intelligence`, `l4_planning`, `l5_action`, `core`, `agents`
- ne pas casser la signature publique de `agent_orchestrator`
- ne pas changer le contrat des messages inter-couches

Toute évolution structurelle passe par une PR avec une note d'architecture (`docs/adr/NNN-titre.md`).
