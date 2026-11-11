# AGIcore Trading V1 — Gate 1: replay MNQ multi-trades causal (plan technique)

**Statut au 2026-11-11 : PLAN ONLY / NOT IMPLEMENTED / NO STRATEGY VERDICT.**
Issue de suivi : [#328](https://github.com/Magassa56/agicore-v2/issues/328).
Ce document prépare une implementation vérifiable ; sa présence ne constitue ni la validation de Gate 1, ni une autorisation de fusion, ni une démonstration de rentabilité.

## Baseline et autorisation Gate 0

- PR #327 fusionnée par commit de merge `d321b34a4f39ee62e91400eb830c3384e21ec28a`, les 32 commits précédents restent ancestraux.
- CI **push sur le SHA exact** : [AGIcore CI #42990194015](https://github.com/Magassa56/agicore-v2/actions/runs/42990194015), `completed/success`, jobs `Full regression suite` et `Restricted portable nonworker tests` réussis.
- Ruleset `AGICORE-main-protection` actif : PR et deux contrôles requis, méthode merge commit seule. La branche Gate 1 est isolée de `main`.

## Observation de code sur RC1

- `src/agicore/trading/synthetic_confirmation_replay_v2.py:replay_confirmation_native` s'arrête à la **première confirmation** et conserve un état de pullback/EMA incrémental jusqu'à cet arrêt.
- `src/agicore/trading/synthetic_exit_replay_v2.py:replay_exit_native` compose confirmation, stop, risque, entrée et sortie **pour cette seule opportunité**.
- `src/agicore/trading/synthetic_exit_handoff_v2.py:capture_synthetic_exit_v2` porte les prédicats gelés de sortie.
- `src/agicore/manager/mission_cycle_v2.py` gère la mission, les sous-processus et les preuves de reprise. Ses adaptateurs sont des processus Python locaux, **pas des appels aux modèles** Terra/Sol/Astra.

**Ne pas** obtenir un pseudo-multi-trade en rappelant `replay_exit_native` sur un suffixe de RAW après sortie : cela redémarrerait potentiellement l'historique EMA, les contextes et les délais de confirmation, et risquerait de changer le résultat causal de la V2. Le nouveau parcours doit maintenir **une seule horloge/barre courante et le contexte gelé**.

## Contrat de développement proposé (à prouver par tests)

1. Un nouveau **adaptateur de session V2** limité aux barres inventées et à une seule série MNQ ; pas de nouvel orchestrateur, pas de réécriture du Manager.
2. Machine d'état explicite : `FLAT -> PENDING_CONFIRMATION -> PENDING_ENTRY -> OPEN -> FLAT`, avec chemins de refus/expiration et `OPEN_UNREALIZED` à la fin des données. Les noms exacts devront être alignés sur les enums V2 existantes.
3. Appliquer les fonctions gelées d'impulsion/régime, EMA20 et confirmation avec **un seul état incrémental**. Ne jamais consulter au temps `t` un prix, timestamp, indicateur ou état provenant de `t+1`.
4. Une confirmation au **close de q** autorise seulement une évaluation au **Open[q+1]**, jamais au close de q. La V2 conserve les stops structurels, risque/sizing, sortie stop ou EMA20 et priorité structurelle. Aucune règle de take-profit, trailing, breakeven ni filtre horaire n'est ajoutée à la baseline.
5. Pendant `OPEN` : ne pas engager de nouvelle entrée, ni mettre en attente un événement susceptible de produire une entrée rétroactive. Le traitement exact des contextes et des signaux pendant une position doit réutiliser les prédicats gelés et faire l'objet d'une preuve de parité.
6. Une nouvelle occasion n'est admissible **qu'après un retour causal à FLAT**, avec le contexte réellement permis à ce moment, sans scanner en arrière et sans entrer deux fois sur la même barre.
7. Si un risque est rejeté, une entrée expire, une barre manque ou l'horloge est invalide : appliquer le contrat V2 de rejet/expiration, sans « réparer » silencieusement la donnée.
8. Journal append-only canonique : identités `mission/session/position/decision/fill`, index et timestamp, source RAW synthétique SHA-256, état avant/après et événements ; références uniques de sorte qu'un replay ou une reprise ne produisent pas deux entrées/sorties.
9. Producteur et vérificateur sont des processus distincts reconstruisant la même suite de décisions et les mêmes reçus canoniques. Signaler explicitement toute primitive ou prédicat partagé : ce n'est pas une indépendance mathématique complète.
10. Conserver `replay_exit_native` et tous les profils 39 observations de RC1 comme tests de **non-régression**. Ajouter la session multi-trades sans modifier leurs sorties.
11. **Aucune comptabilité financière** dans Gate 1 : pas de calcul de PnL, frais, slippage ou score de stratégie. Ces calculs relèvent d'un gate suivant séparé.

## Matrice de tests Gate 1 — données inventées uniquement

- T01 : deux confirmations/entrées/sorties **successives**, périodes d'exposition disjointes, ordre causal correct.
- T02 : contexte ou confirmation survient en position ouverte ; **zéro seconde entrée** et zéro signal mis en attente artificiellement.
- T03 : stop structurel et signal EMA20 concurrents ; priorité gelée, une seule sortie.
- T04 : refus de risque ; aucune entrée et aucun stop actif lié.
- T05 : entrée expirée ou gap temporel ; aucune création a posteriori.
- T06 : fin des données avec position ouverte ; `OPEN_UNREALIZED`, aucune fermeture inventée.
- T07 : données tronquées avant `Open[q+1]` ; aucune entrée.
- T08 : barres désordonnées, doublons, horodatage invalide ; fail-closed.
- T09 : substitution d'une barre **future** ne modifie aucune décision antérieure.
- T10 : reprise sur état vérifié ; empreinte canonique stable, aucune double écriture/entrée/sortie.
- T11 : reprise sur état `running`, ambigu ou preuve altérée ; refus sécurisé.
- T12 : falsification d'un reçu, identifiant, prix, index ou timestamp ; rejet du vérificateur.
- T13 : tous profils RC1 39 barres identiques bit-à-bit au point de comparaison établi.
- T14 : test d'interdiction d'appeler les primitives de comptabilité dans les missions synthétiques.

## Conditions avant une PR prête à revue

- Implémentation et tests ajoutés **sur cette seule branche**, sans nouvelle architecture et sans toucher aux paramètres V2 gelés.
- Tests ciblés, Ruff, `git diff --check`, suite historique et deux contrôles CI sur le **HEAD exact**.
- Rapport de parité, diff inspecté, limites connues, preuves de déterminisme producteur/vérificateur, et point d'arrêt **avant merge**.
- Si une parité avec la V2 historique ne peut pas être prouvée, retenir `BLOCKED` et ne pas déclarer Gate 1 terminé.

## Hors périmètre

- Aucun accès aux RAW réels 74 308 lignes (MNQ 03-26), aux 89 841 observations DEVELOPMENT (MNQ 09-26), à `data/`, à des données NQ ou à l'OOS réservé.
- Aucun broker, NinjaTrader connecté, compte Apex, ordre réel, paper connecté, source payante ou publication de signaux.
- Aucune optimisation ni mesure de rentabilité avant que Gate 1 soit prouvé et qu'un protocole scientifique distinct soit approuvé.

**Verdict actuel : GATE0 PASS ; GATE1 PLAN_ONLY ; MULTI_TRADES NOT IMPLEMENTED ; TRADING_EDGE UNKNOWN.**
