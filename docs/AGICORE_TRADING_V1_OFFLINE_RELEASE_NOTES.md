# AGIcore Trading v1 Offline Release Notes

## Status

offline/sandbox release only

## Decision

APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION

## Included Capabilities

- CSV Replay Input v1
- Synthetic Market Scenario v1
- Strategy Replay Engine v1
- Simulated Broker Stub v1
- Risk Guard Enforcement v1
- Journal Writer v1
- Offline Report Markdown JSON v1
- V1 Candidate
- V1 Candidate Review
- V1 Offline Release Decision

## Explicit Non-Goals

- pas de trading reel
- pas de broker reel
- pas d'Alpaca reel
- pas d'ordre reel
- pas d'acces compte reel
- pas de mutation position reelle
- pas de preuve de rentabilite
- pas de conseil financier
- pas de market data reelle automatisee
- pas de lecture data/

## Testing Evidence

- test release decision : 37 passed
- trading tests : 3795 passed
- unit tests : 4184 passed
- git diff --check : OK

## Known Limitations

- strategies simples seulement
- donnees uniquement synthetiques ou CSV string en memoire
- pas encore de vraie persistance de rapports
- pas encore de vraie interface utilisateur
- pas encore de paper broker connecte
- pas encore de validation sur donnees de marche reelles
- pas encore de mesure de rentabilite robuste

## Usage Guidance

- utiliser uniquement en local/offline
- utiliser uniquement en sandbox
- ne pas connecter a un broker reel
- ne pas utiliser pour prendre des decisions financieres reelles

## Next Suggested Step

AGIcore Trading v1 Offline Smoke Demo
