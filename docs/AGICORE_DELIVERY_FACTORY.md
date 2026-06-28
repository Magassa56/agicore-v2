# AGIcore Delivery Factory v1

## Objectif

AGIcore Delivery Factory v1 standardise la livraison des prochaines phases AGIcore sans modifier le runtime Trading.
Cette usine de livraison transforme une roadmap produit en issues GitHub claires, branches dediees, taches Codex repetables, tests CI, pull requests relisibles, validation humaine, merge, puis prochaine phase.

## Chaine cible

1. Roadmap produit maintenue dans `docs/AGICORE_TRADING_ROADMAP.md`.
2. Issue GitHub standardisee creee depuis `.github/ISSUE_TEMPLATE/agicore_phase.yml`.
3. Branche dediee par phase, hors `main`.
4. Tache Codex limitee aux fichiers autorises par l'issue.
5. Tests locaux obligatoires avant push.
6. Push de la branche de phase.
7. Pull request avec checklist de securite.
8. GitHub Actions lance automatiquement les tests unitaires et `git diff --check`.
9. ChatGPT supervise la PR, relit les changements et qualifie la decision.
10. Bama valide les grandes decisions.
11. Merge apres validation humaine.
12. Creation ou activation de la prochaine issue.

## Roles

### Bama

Bama valide les grandes decisions produit, les arbitrages de priorite et les transitions majeures.
Bama ne pilote plus chaque detail a la main quand l'issue, la Definition of Done et les checks CI suffisent a encadrer Codex.

### ChatGPT

ChatGPT supervise la chaine de livraison, prepare ou relit les issues, relit les PR et decide `VALIDE`, `A CORRIGER` ou `RISQUE`.
ChatGPT doit signaler les ecarts de perimetre, les risques de securite, les tests manquants et les phases trop abstraites.

### Codex

Codex implemente les issues dans une branche dediee.
Codex respecte les fichiers autorises, execute les tests demandes, produit un rapport final clair et s'arrete avant commit si la phase le demande.

### GitHub

GitHub conserve la memoire officielle du projet: roadmap, issues, PR, decisions, reviews, checks et historique de merge.

### GitHub Actions

GitHub Actions lance les tests automatiquement sur pull request et push vers `main`.
La CI doit rester simple, offline, sans secret et sans service externe.

## Regles de securite

- Ne pas ajouter de broker reel.
- Ne pas ajouter Alpaca reel.
- Ne pas lire de cle API.
- Ne pas ajouter HTTP, websocket ou socket.
- Ne pas appeler d'API externe.
- Ne pas envoyer d'ordre reel.
- Ne pas acceder a un compte reel.
- Ne pas muter une position reelle.
- Ne pas toucher `data/`.

## Decision attendue par PR

Chaque PR doit conclure par une decision explicite:

- `VALIDE`: phase conforme, tests verts, risques acceptables.
- `A CORRIGER`: changements utiles mais non conformes ou tests incomplets.
- `RISQUE`: risque de securite, derive de perimetre ou impact runtime non valide.
