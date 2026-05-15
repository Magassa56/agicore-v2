# AGENTS.md — Pipeline d'exécution AGIcore-v2

> Contrat opératoire pour tout agent (humain ou IA) travaillant sur ce repo.
> S'applique en complément de `CLAUDE.md` (identité système).

---

## Rules

1. **Travailler sur la feature branch courante uniquement** — jamais sur `main`.
2. **Ne pas pousser sur `main`** — push uniquement sur `feature/*`.
3. **Stop après chaque phase** — attendre la validation explicite (`bootstrap OK`, `migration OK`, etc.) avant d'enchaîner.
4. **Si une erreur survient → corriger avant de continuer.** Pas de phase suivante tant qu'une phase n'est pas verte.
5. **Aucun changement d'architecture sans validation J'ai.** L'architecture World Model est immuable.
6. **Aucun secret hardcodé.** `.env` uniquement, jamais committé.
7. **Tous les chemins doivent être portables** (`$env:USERPROFILE`, `$env:APPDATA`, ou relatifs). Pas de `C:\Users\<nom>\...`.

---

## Phases

| # | Phase | Sortie attendue | Stop ? |
|---|---|---|---|
| 1 | **BOOTSTRAP** | venv créé, deps installées, `import agicore` fonctionne | Oui — attendre `bootstrap OK` |
| 2 | **MIGRATION** | Schéma DB initialisé sans erreur runtime | Oui — attendre `migration OK` |
| 3 | **GIT STATE CHECK** | Sortie de `git log --oneline -5` | Oui — vérification visuelle |
| 4 | **LOGGING LAYER** | structlog configuré, logs JSON, niveaux info/debug/error, plus aucun `print` | Oui — attendre validation |
| 5 | **MEMORY L2** | SQLite STM + SQLAlchemy LTM, schémas `events` / `tasks` / `agent_state` | Oui — attendre validation |
| 6 | **ORCHESTRATOR L4 (minimal)** | reçoit une tâche, route vers logging/memory/bootstrap, retourne un résultat exécutable | Oui — attendre validation |
| 7 | **TESTS** | pytest passe sur : bootstrap, migration, logging, memory STM insert/retrieve, orchestrator routing | Oui — feu vert final |

---

## Output format

Après chaque phase, l'agent produit un rapport au format :

```
PHASE       : <numéro et nom>
STATUS      : OK | FAIL
ARTIFACTS   : <fichiers créés ou modifiés>
COMMANDS    : <commandes clés exécutées>
EVIDENCE    : <extrait de sortie qui prouve le succès>
NEXT        : STOP — attendre validation
```

En cas de FAIL :

```
PHASE       : <numéro>
STATUS      : FAIL
ERROR       : <message d'erreur exact>
ROOT_CAUSE  : <analyse>
FIX         : <correction proposée ou appliquée>
RETRY       : <commande pour réessayer>
```

---

## Stop conditions

L'agent **doit s'arrêter** dans les cas suivants :

- Fin d'une phase (succès ou échec).
- Détection d'un changement d'architecture non documenté.
- Tentative de push sur `main`.
- Working tree dirty avant une opération git.
- Erreur d'import du package `agicore` après bootstrap.
- Tests rouges après implémentation d'une phase.
- Toute action listée dans `CLAUDE.md` § 8 comme "Confirmation explicite requise" (push main, déploiement, suppression de fichiers, modification `.env`/secrets, dépenses cloud).

L'agent **ne reprend** que sur instruction explicite de J'ai.

---

## Format de réponse pour les phases

Aligné avec le format obligatoire de `CLAUDE.md` § 9 :

```
Layer concerné          : Lx (ou "transverse")
Modules concernés       : ...
Actions effectuées      : ...
Tests exécutés          : ...
Fichiers créés/modifiés : ...
Risques éventuels       : ...
Prochaine étape suggérée : STOP — attendre <signal>
```

---

*Dernière mise à jour : 2026-05-08*
