# World Model — fondations conceptuelles

> Pour l'implémentation concrète, voir `architecture.md`. Ce document explique *pourquoi* AGIcore-v2 est structuré ainsi.

---

## 1. Pourquoi un World Model ?

Un World Model est une représentation interne, partagée et persistante, de l'environnement dans lequel le système opère. Pour un orchestrateur multi-agents, c'est la condition pour que :

- les agents prennent des décisions cohérentes entre eux
- les actions soient justifiables a posteriori
- l'état système soit reconstructible (replay, audit, debug)
- la planification puisse simuler des trajectoires avant action

Sans World Model partagé, on retombe sur un assemblage d'agents stateless qui se contredisent.

---

## 2. Les 5 couches : pourquoi cette découpe

| Layer | Question fondamentale |
|---|---|
| L1 — Perception | *Que se passe-t-il dans le monde ?* |
| L2 — State / Memory | *Que sait-on, qu'a-t-on retenu ?* |
| L3 — Dynamics / Intelligence | *Que va-t-il se passer / que faut-il faire ?* |
| L4 — Planning | *Comment l'exécuter, par qui, dans quel ordre ?* |
| L5 — Action | *Faire — et observer le résultat (qui retourne en L1)* |

La boucle complète est **L5 → L1** : chaque action produit de nouvelles observations, qui réalimentent la perception. C'est la fermeture du cycle qui rend le système "vivant".

---

## 3. Invariants

Quel que soit le domaine (trading, CNC, apps), les invariants suivants tiennent :

1. **Une décision n'est valide que si elle s'appuie sur un état L2 connu.**
   Pas de raisonnement à partir de rien.

2. **Une action L5 ne s'exécute jamais sans plan L4.**
   Même une action triviale passe par le planner — c'est ce qui garantit la traçabilité.

3. **Toute action produit un événement L1.**
   Le retour est observable, donc apprenable.

4. **L3 ne touche pas au monde.**
   L3 produit des intentions, pas des effets. Cette séparation est essentielle pour pouvoir simuler / dry-run / backtest.

---

## 4. Conséquences pratiques

- Un agent de trading ne peut pas appeler NinjaTrader directement : il émet une intention, L4 la valide, L5 l'exécute.
- Un agent de coding ne peut pas écrire un fichier sans passer par un connector enregistré dans L5.
- La couche mémoire (L2) est la seule source de vérité partagée — pas de variables globales.

---

## 5. Ce que le World Model n'est pas

- Pas un knowledge graph ontologique généraliste — juste un état opérationnel.
- Pas un cerveau unique — chaque agent a son contexte, mais tous partagent L2.
- Pas une simulation complète du monde — un modèle suffisant pour planifier et auditer.
