# AGIcore Trading V1 — Gate 1: replay MNQ multi-trades causal (plan technique)

**Statut : intégration synthétique native versionnée en cours de vérification / aucun verdict de stratégie.**
Issue de suivi : [#328](https://github.com/Magassa56/agicore-v2/issues/328).
Ce document prépare une implementation vérifiable ; sa présence ne constitue ni la validation de Gate 1, ni une autorisation de fusion, ni une démonstration de rentabilité.

## Mission native versionnée : frontière actualisée

La décision AGIcoreManager autorise désormais les appels comptables **internes** du moteur V2 uniquement pour la nouvelle mission synthétique `native_g1`. Les missions RC1 existantes conservent l'interdiction de comptabilité. Le nouveau contrat `agicore:mission:native-g1:v1`, les schémas de bundle et de reçus et les profils sont distincts de RC1.

Le producteur et le vérificateur exécutent séparément `evaluate_synthetic_scenario_v2`, sans modifier ses fichiers gelés. Chacun construit une projection non financière : provenance des observations, événements, suppressions, positions, quantité approuvée, indices et types d'entrée/sortie. Aucun résultat comptable, somme de frais, valeur de PnL ou métrique de performance n'est sérialisé. Le vérificateur partage le moteur V2 natif et le générateur inventé, mais reconstruit lui-même la projection et compare les reçus.

La mission est limitée à deux profils inventés de 64 observations, long ou short. Elle n'accepte ni fichier externe ni observation réelle. Exemple depuis un environnement installé, en choisissant un répertoire absolu **nouveau** :

```bash
python -m agicore.manager.mission_cycle_v2 --output-dir /tmp/agicore-g1-example --observations 64 --stage native_g1 --profile native-g1-long-v1
python -m agicore.manager.mission_cycle_v2 --output-dir /tmp/agicore-g1-example --resume
```

Le Manager conserve son scellement des sources. Les nouveaux fichiers et adaptations changent l'empreinte des missions créées sous cette révision : une ancienne mission RC1 ne peut pas être supposée reprenable sous un arbre différent. Pour vérifier ou reproduire ses reçus, utiliser son commit historique et l'environnement correspondant ; ne pas réécrire ses preuves. Les nouvelles missions RC1 restent sur leur contrat `agicore:mission:v2`, sans comptabilité.

La reprise ne redémarre qu'un rôle non commencé après vérification des reçus scellés. Une interruption pendant une tâche d'état ambigu échoue de manière fermée ; aucune reprise au milieu d'un replay n'est annoncée. Les deux processus utilisent le même moteur natif : la vérification n'est donc pas une implémentation mathématiquement indépendante de la stratégie. L'entrée entière est validée avant le replay ; une observation future invalide fait échouer la mission complète, sans publier de décision partielle.

## Historique : raccordement direct sans comptabilité bloqué

Au moment du blocage initial, le cœur V2 possédait déjà des positions successives et le parcours multi-trades du Manager était absent. L'initialisation de `begin_regime_gated_baseline_v2` appelle `begin_exit_policy_v2`, qui construit obligatoirement un `FeesAndSlippageBookV2`. Elle se heurte donc à la frontière sans comptabilité de RC1 avant même la première observation.

Le test `tests/integration/test_gate1_frozen_accounting_boundary.py` bloque cette construction avant tout calcul financier et vérifie que l'initialisation native échoue sous ce garde. Les fonctions ultérieures de la baseline appellent également les fonctions comptables d'entrée et de sortie. Il n'existe pas de paramètre de sortie sans comptabilité dans leurs interfaces actuelles.

Les empreintes du manifeste figé incluent le code de la baseline et des politiques. Les modifier en place changerait cette identité et ferait échouer le contrôle historique `test_manifest_is_new_canonical_snapshot_of_every_frozen_component`. Le présent changement ne modifie ni ces modules ni leurs preuves.

Un essai local sur deux positions inventées a pu composer les portes V2 avec une boucle de coordination distincte, mais cette boucle dupliquerait la séquence Open/Close native. Elle n'est pas livrée : le mandat interdit de reconstruire cette capacité. Aucune compatibilité multi-trades Manager n'est déclarée sur cette base.

La décision ultérieure a autorisé la frontière interne versionnée décrite ci-dessus ; elle ne modifie pas le constat ni la protection RC1.

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

## Contrat de développement initial — historique

Les points suivants conservent la proposition initiale pour traçabilité. La décision versionnée en début de document prévaut, notamment sur l'interdiction générale du point 11 : elle reste applicable à RC1, mais les appels internes natifs sont autorisés pour `native_g1`.

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
- T14 : interdiction des primitives comptables dans RC1 ; pour `native_g1`, contrôle des appels internes autorisés et absence de résultat financier dans les projections.

## Conditions avant une PR prête à revue

- Implémentation et tests ajoutés **sur cette seule branche**, sans nouvelle architecture et sans toucher aux paramètres V2 gelés.
- Tests ciblés, Ruff, `git diff --check`, suite historique et deux contrôles CI sur le **HEAD exact**.
- Rapport de parité, diff inspecté, limites connues, preuves de déterminisme producteur/vérificateur, et point d'arrêt **avant merge**.
- Si une parité avec la V2 historique ne peut pas être prouvée, retenir `BLOCKED` et ne pas déclarer Gate 1 terminé.

## Hors périmètre

- Aucun accès aux RAW réels 74 308 lignes (MNQ 03-26), aux 89 841 observations DEVELOPMENT (MNQ 09-26), à `data/`, à des données NQ ou à l'OOS réservé.
- Aucun broker, NinjaTrader connecté, compte Apex, ordre réel, paper connecté, source payante ou publication de signaux.
- Aucune optimisation ni mesure de rentabilité avant que Gate 1 soit prouvé et qu'un protocole scientifique distinct soit approuvé.

**Verdict :** le statut d'intégration et la CI sont à lire sur la PR #329 et son HEAD exact. Aucun résultat synthétique ne démontre un avantage de trading ou une rentabilité.
