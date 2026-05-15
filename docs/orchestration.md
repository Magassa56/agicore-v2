# Orchestration multi-agents — AGIcore-v2

> Couche concernée : L4 (Planning / Orchestration). Module clé : `agent_orchestrator.py`.

---

## 1. Framework

Framework custom Python AGIcore-v2 — pas de dépendance externe lourde (LangGraph, CrewAI, etc.) tant que les besoins peuvent être couverts en interne.

---

## 2. Patterns d'orchestration

| Pattern | Quand l'utiliser |
|---|---|
| Supervisor / Worker | Pipeline avec un coordinateur central qui distribue à des workers spécialisés |
| Event-driven | Réactions à des événements L1 (signal marché, message externe, fin de tâche) |
| Message queue | Découplage temporel entre producteurs et consommateurs |

L'orchestrator par défaut est un **supervisor** qui peut consommer un event bus ou une queue selon la config.

---

## 3. Communication inter-agents

Format de message standard (JSON) :

```json
{
  "msg_id": "uuid",
  "task_id": "uuid",
  "from_agent": "trading_agent",
  "to_agent": "risk_manager",
  "type": "intent|task|result|error",
  "payload": { },
  "timestamp_utc": "2026-05-08T10:00:00Z"
}
```

État partagé : Redis (rapide, distribué) ou SQLite (local, simple).

---

## 4. Logging et traçabilité

Chaque décision d'agent doit être loggée avec :

- `decision_id`
- `agent_id`
- `inputs` (résumé hashé)
- `outputs`
- `reasoning` (si LLM)
- `latency_ms`
- `cost_tokens` (si LLM)
- `timestamp_utc`

Stockage : LTM (PostgreSQL) avec index sur `agent_id` et `timestamp_utc`.

---

## 5. LLMs utilisés

| LLM | Rôle | Quand |
|---|---|---|
| Claude API (Anthropic) | Principal — raisonnement, décision, génération | Par défaut |
| GPT (OpenAI) | Fallback | Si Claude indisponible ou pour A/B |

Configuration par agent dans `prompts/<agent>.md` + paramètres runtime (temperature, max_tokens) dans le registre L4.

---

## 6. Outils MCP / connecteurs

- GitHub (lecture/écriture repo, issues, PRs)
- Google Drive (lecture/écriture documents)
- Terminal Python (exécution de code)
- NinjaTrader (via `ninjatrader_connector.py` en L5)

Tout connecteur externe est wrappé dans L5 — jamais d'appel direct depuis L3 ou L4.

---

## 7. Cycle de vie d'une tâche

```
[L3 émet Intention]
       ↓
[L4 reçoit, valide, décompose en Tasks]
       ↓
[L4 assigne aux agents disponibles]
       ↓
[Agents exécutent, émettent Results]
       ↓
[L4 agrège, met à jour L2]
       ↓
[L1 capte le nouvel état → boucle]
```

Chaque transition logue un événement.

---

## 8. Règles de stabilité

- Un agent qui échoue 3 fois consécutivement passe en état `quarantined`, son superviseur est notifié.
- L'orchestrator ne tolère pas les boucles infinies : timeout configurable par tâche, max retries plafonné.
- Toute communication doit être idempotente quand possible (`msg_id` permet la déduplication).
