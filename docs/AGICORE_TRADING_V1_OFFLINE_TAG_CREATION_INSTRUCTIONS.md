# AGIcore Trading v1 Offline Tag Creation Instructions

## Statut

instructions only, no Git tag created

## Decision prealable requise

- APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW

## Tag propose

- agicore-trading-v1-offline

## Version proposee

- v1.0.0-offline

## Avertissement

- ne pas creer le tag avant validation humaine finale
- ne pas utiliser pour trading reel
- pas de broker reel
- pas d'ordre reel
- pas de preuve de rentabilite
- pas de conseil financier
- aucune lecture data/
- aucune ecriture data/
- aucune cle API
- aucun reseau dans cette phase

## Verifications avant tag

- git switch main ; resultat attendu : main branche active
- git fetch origin ; resultat attendu : remote refs synchronisees
- git pull origin main ; resultat attendu : main a jour
- python -m pytest tests/unit/ -q ; resultat attendu : tests verts
- git status --short ; resultat attendu : seulement ?? data/

## Commandes proposees pour creation manuelle future

- `git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"` ; creer le tag annote manuellement apres validation humaine finale
- `git push origin agicore-trading-v1-offline` ; publier le tag manuellement apres verification locale

## Verifications apres tag

- git tag --list agicore-trading-v1-offline ; resultat attendu : agicore-trading-v1-offline
- git ls-remote --tags origin agicore-trading-v1-offline ; resultat attendu : tag distant present
- git status --short ; resultat attendu : seulement ?? data/

## Decision instructions

APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS

## State attendu

READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS_REVIEW

## STOP

STOP avant commit. Ne pas creer le tag dans cette phase.
