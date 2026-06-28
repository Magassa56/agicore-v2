# AGIcore Definition of Done

Une phase AGIcore est terminee uniquement si tous les criteres ci-dessous sont satisfaits.

## Criteres de livraison

- Objectif clair et relie a la roadmap.
- Fichiers crees ou modifies limites au perimetre autorise.
- Tests cibles passes.
- Tests unitaires passes.
- `git diff --check` OK.
- `git status` propre hors `data/`.
- Documentation ou rapport final inclus.
- Decision finale claire.
- Prochaine etape explicite.

## Criteres de securite

- Aucune cle API.
- Aucun HTTP.
- Aucun websocket.
- Aucun socket.
- Aucune API externe.
- Aucun ordre reel.
- Aucun acces compte reel.
- Aucune mutation de position reelle.
- Aucun broker reel.
- Aucun Alpaca reel.
- Aucun ML externe.
- Aucun LLM externe.
- `data/` non touche.

## Criteres de review

- Les risques connus sont listes.
- Les limites offline et sandbox sont explicites.
- Les tests obligatoires sont cites avec leur resultat.
- Les fichiers hors perimetre sont absents du diff.
- La phase suivante est nommee, mais non executee sans validation.
