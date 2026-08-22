# AGIcore Project Status

Dernière mise à jour : 2026-08-22

## P1 — AGIcore Trading

**Statut : EN COURS — priorité absolue**

État récent vérifié sur GitHub :

- PR #224 : modèle détaillé des coûts d'exécution.
- PR #225 : propagation du modèle de coûts aux études breakout.
- PR #226 : comparaison déterministe de scénarios de coûts.
- PR #227 : contrat de contexte d'exécution risk-gated et journal/replay.
- PR #228 : contrat déterministe d'autorisation de risque.
- PR #229 : consommation unique des autorisations de risque.
- PR #230 : transaction agrégée L5 déterministe.
- PR #231 : chemin canonique L5 soumis au contrôle de risque obligatoire.

La PR #231 rapporte 5 564 tests réussis sur la suite complète. Elle ne démontre pas la rentabilité et n'autorise ni paper trading supervisé ni trading réel.

### Prochain objectif

Identifier et fermer les gates pré-paper restantes : persistance durable, reprise après crash, idempotence inter-processus et migration contrôlée des familles d'exécution encore hors chemin canonique.

## P2 — BusinessPilot

**Statut : À DÉMARRER**

V1 cible :
- `businesspilot.pages.dev` ;
- offre Starter 30 € ;
- Automation 9,99 € ;
- Business Pro 19,90 € ;
- capture lead + Google Sheets ;
- automatisations simples avant extension réseaux sociaux.

## P3 — AGIcore Biotech / Agritech

**Statut : À DÉMARRER**

Architecture retenue :

SARRA-Py → cultures maïs/mil/sorgho → météo/sol → WeedSim → HerbicideSim → AGIcore Scenario Optimizer.

DSSAT sert de moteur secondaire de validation. APSIM reste prévu plus tard pour des simulations complexes et multi-années.

### Premier jalon

Installer SARRA-Py et reproduire une simulation de référence avant d'ajouter WeedSim ou HerbicideSim.

## Backlog protégé

AGIcore Engineering, bibliothèque CAO, infrastructure IA locale, atelier 3D/CNC et robotique restent conservés mais non actifs tant qu'un jalon prioritaire n'est pas franchi.
