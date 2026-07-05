# AGIcore Trading v1 Offline Local Runbook

## Statut

offline/sandbox local runbook only

## Avertissement securite

- pas de trading reel
- pas de broker reel
- pas d'Alpaca reel
- pas d'ordre reel
- pas d'acces compte reel
- pas de mutation position reelle
- pas de lecture data/
- pas d'ecriture data/
- pas de reseau
- pas de cle API
- pas de preuve de rentabilite
- pas de conseil financier

## 1. Prerequis

- depot local propre
- branche main a jour
- environnement Python local
- dependances installees
- aucune cle API configuree
- aucun broker connecte

## 2. Synchronisation propre

- `git switch main` : se placer sur main avant synchronisation.
- `git fetch origin` : recuperer les references distantes.
- `git pull origin main` : synchroniser main local.
- `git status --short` : verifier que seul data/ non suivi apparait.

Resultat attendu : seulement `?? data/`.

## 3. Tests recommandes

- `python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q` : valide la smoke demo offline V1.
- `python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo_review.py -q` : valide la review de smoke demo offline V1.
- `python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_sandbox_usage_guide.py -q` : valide le guide sandbox offline V1.
- `python -m pytest tests/unit/ -q` : lance la suite unitaire complete.

## 4. Smoke demo en memoire

Utiliser uniquement `PYTHONPATH=src`.

```python
from agicore.trading.agicore_trading_v1_offline_smoke_demo import (
    run_agicore_trading_v1_offline_smoke_demo,
)

result = run_agicore_trading_v1_offline_smoke_demo()
print(result.decision)
print(result.state)
print(result.score.overall_score)
print(result.risks)
print(result.recommendations)
```

## 5. Interpretation

- APPROVE signifie seulement offline/sandbox OK
- score 100 ne prouve pas une rentabilite
- risks [] ne signifie pas absence de risque financier reel
- broker preview est simule uniquement
- read-only decision n'est pas un ordre reel

## 6. Diagnostic

- ModuleNotFoundError : verifier PYTHONPATH=src
- test flaky : relancer le test cible puis tests/unit/
- BOM UTF-8 : corriger l'encodage puis relancer tests/unit/
- git status montre autre chose que data/ : STOP et analyser avant commit
- data/ apparait : normal si non suivi, ne jamais l'ajouter

## 7. Regles Git

- ne jamais faire git add .
- ajouter seulement les fichiers autorises
- verifier git diff --cached --name-only
- commit apres tests verts
- push branche dediee

## 8. Limites connues

- strategies simples seulement
- donnees synthetiques ou CSV string en memoire
- pas de vraie persistance
- pas de vraie interface utilisateur
- pas de paper broker connecte
- pas de donnees reelles automatisees
- pas de rentabilite validee

## 9. Procedure STOP

- arreter si fichier hors perimetre modifie
- arreter si data/ est staged
- arreter si reseau/broker/secret apparait
- arreter si la formulation laisse croire a du trading reel

## Prochaine etape suggeree

AGIcore Trading v1 Offline Final Readiness Review
