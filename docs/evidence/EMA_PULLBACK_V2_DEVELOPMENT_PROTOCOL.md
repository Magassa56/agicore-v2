# EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL — préengagement version 1

Date de préengagement : 2026-10-06 UTC. Phase exclusivement documentaire
et screening synthétique, sans replay. Aucun résultat V2 n'a été consulté.

## Identité immuable

| Élément | Valeur autorisée |
| --- | --- |
| Stratégie | `EMA_PULLBACK_V2_REGIME_GATED_BASELINE` |
| Formalization version | `1` |
| Mode | `OFFLINE_DETERMINISTIC` |
| STRATEGY_MANIFEST_SHA256 | `965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a` |
| DEVELOPMENT_PROTOCOL_SHA256 | `68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402` |

Le fichier canonique est `EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json` :
UTF-8, clés triées récursivement, JSON compact, aucun NaN/Infinity JSON,
un LF final. Le digest porte sur les octets exacts du fichier. Il reste
hors du payload hashé pour éviter une auto-référence circulaire. Il est
publié ici et épinglé dans `tools/ema_pullback_v2_development_protocol.py`.
Un hash annoncé erroné ou une mutation des octets du protocole/manifest
est une erreur `FAIL_CLOSED`, jamais un verdict statistique.

Les composants, paramètres, coûts, délais, sizing, prix de fill et priorités
de la stratégie restent ceux du manifest autorisé. L'outil ne contient
aucun indicateur, signal V2, moteur de replay ou loader de prix. Il consomme
uniquement des métadonnées déclarées et des records comptables. Son résumé
de screening ne remplace pas le `RESULT_SCHEMA` complet du futur replay.

## Sélection DEVELOPMENT préengagée

Exiger MNQ, contrat trimestriel individuel terminé, `1 Minute`, `Last`,
`DoNotMerge`, `CME US Index Futures ETH`. L'ensemble admissible exclut tout
contrat utilisé pour une évaluation V1/V2, toute performance V2 déjà inspectée
et toute lignée dont la propreté ne peut être établie. Trier par expiration
décroissante et retenir le plus récent admissible, sans graphique ni résultat.

`MNQ 06-26` et `MNQ 03-26` sont explicitement interdits. `MNQ 09-26` est
le premier candidat attendu, **pas un DEVELOPMENT canonique**. Aucun fichier,
hash RAW ou contrat canonique n'est sélectionné pendant cette phase. Une
preuve d'inspection antérieure produit `REJECT_DATASET_CONTAMINATED`, puis
la même règle s'applique au suivant. Un fait inconnu n'est jamais réputé vrai.

Le rôle exclusif est `EXPOSED_DEVELOPMENT`. Dès le premier replay, l'exposition
est définitive. Aucun label OOS, validation, holdout ou preuve de production.

## Filiation à établir dans la prochaine gate

Le JSON définit `REQUIRED_LINEAGE_FIELDS` et les contrôles requis : instrument,
contrat et expiration attestés, intervalle/type/merge/session, chaîne fournisseur,
version NinjaTrader, fichier source, SHA-256, taille, nombre de lignes, premiers/
derniers timestamps, date d'export/téléchargement, fuseau/DST et sémantique des
timestamps. Conserver aussi les attestations d'usage et d'absence d'inspection.

Avant replay, vérifier ordre strict, doublons, lignes malformées, OHLC finis
et valides, volume non négatif, grille MNQ et structure minute. Documenter
les gaps réels et le calendrier de sessions ; ne pas ajouter de bougies.
Aucune correction silencieuse. Toute transformation doit être explicite,
déterministe, hashée, conserver le RAW/parent et enregistrer commande,
paramètres, hashes entrée/sortie/code, comptes de lignes et modifications.
Ces vérifications de RAW ne sont **pas exécutées dans cette PR**.

## Seuils de screening

Tous les critères de résultat utilisent le **net après les coûts V2 figés**.
Les seuils principaux reprennent V1 pour conserver une comparaison indépendante
des résultats V2. Aucune observation ne permet de modifier ces seuils.

| Critère global | Frontière inclusive |
| --- | --- |
| Trades clôturés | `>= 100` |
| PnL net réalisé | `>= +200.00 USD` |
| Profit factor net | `>= 1.15` |
| Maximum marked-equity drawdown | `<= 750.00 USD` |
| Pertes consécutives | `<= 8` |

Diviser l'intervalle entre premier et dernier timestamp source en exactement
trois tiers de **temps écoulé**, avant de lire les résultats. S1/S2 sont
semi-ouverts ; S3 inclut le timestamp final. Les frontières restent des
fractions exactes de microsecondes, sans arrondi. Chaque trade clôturé appartient
au segment de son **fill de sortie** ; il emporte ses deux fills et coûts.
Ni réorganisation, ni segmentation par trades/PnL, ni liquidation aux frontières.

| Critère par segment | Frontière |
| --- | --- |
| Labels | `DEVELOPMENT_S1`, `DEVELOPMENT_S2`, `DEVELOPMENT_S3` |
| Trades clôturés | `>= 15` chacun |
| Segments profitables | `>= 2 sur 3` |
| Définition profitable | `net_realized_pnl > 0` strictement |
| Profit factor net | `>= 0.80` chacun |
| PnL net réalisé | `>= -200.00 USD` chacun |

## Comptabilité et métriques

Calculs en `Fraction`, sans float ni arrondi intermédiaire. Les valeurs exactes
sont conservées ; `ROUND_HALF_UP` aux cents est réservé au reporting monétaire.
Le PF est la somme des gains nets divisée par la valeur absolue des pertes
nettes. Sans pertes et avec gains : `POSITIVE_INFINITY`, supérieur à tout
minimum fini. Sans gains ni pertes : zéro. Un trade net nul ou positif remet
la série de pertes à zéro. Moyenne/médiane exactes et win rate sont nulles
si aucun trade n'est clôturé.

Un mark est obligatoire à **chaque bougie réelle clôturée**, indices consécutifs
et timestamps conformes, sans bougie synthétique. Equity initiale zéro ;
equity marquée = somme des PnL nets clôturés + PnL non réalisé de la position
ouverte. Pour cette dernière, marquer au Close brut depuis l'entrée effective
et déduire le frais d'entrée déjà payé ; ne pas inventer frais/slippage de sortie.
À la fermeture, ces coûts rejoignent une seule fois le PnL net réalisé du trade.
Drawdown = maximum du pic courant moins l'equity marquée, baseline zéro incluse.
Une position finale ouverte reste `OPEN_UNREALIZED`, avec un PnL réalisé du
trade **absent (`null`)**, sans fill de liquidation.

Le `RESULT_SCHEMA` embarqué dans le JSON exige les événements impulse/reversal,
contextes admis/ambigus/expirés, pullbacks, suppressions pending/position,
confirmations, décisions de risque, quantités 1/2 des entrées remplies,
fills d'entrée, trades clôturés/ouverts et comptages LONG/SHORT, sorties stop/EMA,
gross après slippage avant frais, frais, diagnostic slippage, net réalisé,
wins/losses/breakeven, moyenne/médiane, PF, win rate, marked drawdown,
loss streak, S1/S2/S3, marks et provenance immuable complète.

Les frais totaux incluent les fills d'entrée encore ouverts, avec sous-totaux
`closed_trade_fees_usd` et `open_entry_fees_usd`. Le PnL net clôturé ne soustrait
que les frais de ses trades clôturés. Le slippage est déjà dans les prix effectifs
et reste uniquement diagnostique séparément, sans deuxième soustraction.
`trades per trading day/session` utilise le calendrier attesté et reste
**diagnostique seulement**, sans critère GO/NO_GO.

## Verdict mécanique

1. Total `< 100` ou au moins un segment `< 15` : `INSUFFICIENT_SAMPLE`,
   ni GO ni NO_GO. Aucun réglage. Seule prochaine gate :
   `EMA_PULLBACK_V2_DEVELOPMENT_SAMPLE_EXTENSION_REQUIRED`, pour un autre
   contrat DEVELOPMENT préengagé avec stratégie et seuils inchangés.
2. Échantillon suffisant et tous les critères globaux/segments satisfaits :
   `GO_TO_INDEPENDENT_VALIDATION`.
3. Échantillon suffisant et au moins un critère échoué : `NO_GO_BASELINE`.
   La baseline reste figée. Aucune recherche de seuils, optimisation,
   AlphaEvolve, nouvel indicateur/TP/stop/risque automatique. Une éventuelle
   variante commence par une hypothèse explicite et son protocole préengagé,
   avant ses résultats ; l'outil ne lance aucune variante.

## Run unique futur et validation scellée

Le protocole fusionné `PASS` puis la filiation `PASS` sont nécessaires avant
une gate séparée de replay. Cette PR n'autorise et n'exécute aucun run.
Le futur run unique sera enregistré **avant son exécution** et lié immuablement
à `strategy_manifest_sha256`, `development_protocol_sha256`,
`dataset_raw_sha256`, `runner_source_sha256`. Le run ID est le SHA-256 du
JSON canonique de ces quatre champs. Le hash de sortie porte sur le résultat
canonique avec le champ `output_sha256` omis.

Seul un rerun démontrant le déterminisme avec les mêmes inputs/code/output
hashes est autorisé. Il ne peut ni remplacer le verdict original ni servir
à choisir un meilleur résultat. Aucun runner réel n'est ajouté ici.

Préengager une validation indépendante sur le prochain contrat trimestriel
MNQ terminé admissible, jamais utilisé par V1 ou ce DEVELOPMENT V2 et jamais
inspecté pour la performance V2. Même métadonnées et tri par expiration.
Le contrat reste non sélectionné et **scellé** jusqu'au verdict DEVELOPMENT
`GO_TO_INDEPENDENT_VALIDATION` ; aucune influence anticipée sur V2.

## Preuves et limite de cette gate

Tests : exclusivement métadonnées et comptabilité inventées, sans lire prix
historiques, résultats réels, graphiques, OOS, ni calculer des signaux V2.
Les tests exercent toutes les frontières, PF infini, resets de loss streak,
marks exacts, absence de liquidation, rôles/hashes refusés, contamination,
couverture/reconciliation et déterminisme depuis des inputs neufs.

Après CI complète verte et fusion :

```text
EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL = PASS
NEXT = EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE_REQUIRED
DEVELOPMENT_REPLAY = NOT_EXECUTED
OOS = SEALED
```

Cette gate préengage un contrôle DEVELOPMENT, sans preuve de rentabilité
ou validation de production. Broker, paper trading et optimisation interdits.
