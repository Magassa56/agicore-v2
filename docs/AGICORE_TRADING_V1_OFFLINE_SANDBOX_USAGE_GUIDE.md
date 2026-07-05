# AGIcore Trading v1 Offline Sandbox Usage Guide

## Statut

offline/sandbox only

## Rappel de securite

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

## Prerequis locaux

- etre sur main a jour
- environnement Python local
- dependances deja installees
- ne pas configurer de cle API
- ne pas connecter de broker

## Commandes recommandees

- `python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q` : Valide la smoke demo V1 offline.
- `python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo_review.py -q` : Valide la review de la smoke demo V1 offline.
- `python -m pytest tests/unit/ -q` : Lance la suite unitaire complete.

## Exemple d'usage en memoire

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

## Interpretation des resultats

- APPROVE signifie seulement sandbox/offline OK
- score 100 ne prouve pas une rentabilite
- risks [] ne signifie pas absence de risque financier reel
- broker preview est simule uniquement
- read-only decision n'est pas un ordre

## Limites connues

- strategies simples seulement
- donnees synthetiques ou CSV string en memoire seulement
- pas de vraie persistance
- pas de vraie interface utilisateur
- pas de paper broker connecte
- pas de donnees reelles automatisees
- pas de rentabilite validee

## Workflow recommande

- lancer les tests
- lancer smoke demo
- lire rapport
- ne rien connecter au reel
- continuer par les prochaines phases

## Prochaine etape suggeree

AGIcore Trading v1 Offline Local Runbook
