# Memory contract — AGIcore-v2

> Couche concernée : L2 (State / Memory). Toutes les autres couches lisent/écrivent ici.

---

## 1. Deux niveaux de mémoire

| Niveau | Acronyme | Durée | Usage |
|---|---|---|---|
| Court terme | STM | session / runtime | état des tâches en cours, contexte actif, locks |
| Long terme | LTM | persistant | historique, décisions, connaissances apprises |

---

## 2. STM — court terme

### Technologies recommandées
- **Redis** : prod, multi-process, latence basse
- **SQLite** : dev local, fichier unique, pas de daemon

### Contenu typique
- état runtime des agents (`agent_status:<agent_id>`)
- tâches en cours (`task:<task_id>`)
- contexte de session LLM (derniers échanges)
- locks et sémaphores

### TTL
Toute clé STM a un TTL explicite. Pas de clé immortelle dans STM — si c'est important au point de durer, ça appartient à LTM.

---

## 3. LTM — long terme

### Technologies recommandées
- **PostgreSQL** : structuré, relationnel, transactionnel
- **Vector store** (Qdrant, Chroma, ou pgvector) : recherche sémantique sur historique d'échanges et de décisions

### Contenu typique
- historique complet des trades (`trades` table)
- historique des décisions d'agents (`agent_decisions` table)
- corpus de connaissance vectorisé (embeddings d'extraits, de réflexions, de leçons apprises)
- snapshots périodiques de l'état système

### Schéma minimal (PostgreSQL)

```sql
CREATE TABLE agent_decisions (
    decision_id UUID PRIMARY KEY,
    agent_id    TEXT NOT NULL,
    task_id     UUID,
    inputs_hash TEXT,
    outputs     JSONB,
    reasoning   TEXT,
    cost_tokens INTEGER,
    latency_ms  INTEGER,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_decisions_agent_time ON agent_decisions(agent_id, created_at DESC);
```

---

## 4. Règle d'or

> **Toute décision importante d'agent doit être stockée en LTM.**

Critères de "importante" :
- impact financier (trade, dépense cloud)
- changement d'état système (déploiement, migration, modif config prod)
- sortie partagée (PR, message externe, fichier publié)
- conclusion d'analyse exploitée par une autre couche

---

## 5. Lecture / écriture

- L1 écrit en STM (état brut entrant) et déclenche un upsert LTM si l'événement est durable.
- L2 est passive : elle expose des accesseurs typés, pas de logique métier.
- L3 lit STM + LTM, n'écrit qu'un résumé de décision.
- L4 écrit l'état des tâches en STM, archive les résultats en LTM.
- L5 écrit le résultat de chaque action en LTM (audit trail).

Pas d'accès direct aux backends — toujours via les accesseurs `MemoryStore.get / put / search`.

---

## 6. Cohérence et latence

- STM est la source de vérité pour l'état "live"
- LTM est la source de vérité pour l'audit
- Synchronisation STM → LTM : asynchrone, via un worker dédié, avec retry si échec
- En cas de divergence, LTM gagne pour l'historique, STM est resynchronisée depuis LTM

---

## 7. Confidentialité et taille

- Pas de PII dans LTM sans chiffrement applicatif
- Compression / archivage des décisions de plus de 90 jours dans S3 (cold storage)
- Quota STM par agent : limite stricte pour éviter qu'un agent fou sature Redis
