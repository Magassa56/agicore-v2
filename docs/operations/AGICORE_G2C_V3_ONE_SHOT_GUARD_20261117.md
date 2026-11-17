# G2C V3 — verrou à usage unique, version 1

Mission : `AGICORE_G2C_V3_ONE_SHOT_EXECUTION_GUARD_IMPLEMENTATION`

Date : 17 novembre 2026

État : **IMPLEMENTED_INERT**. Aucune autorisation d’exécution n’est livrée.

Le [contrôleur](../../tools/ema_pullback_v2_g2c_one_shot_guard_v1.py) implémente le protocole de réservation et la vérification séparée du job de calcul. Son API GitHub est une interface injectée : aucun client HTTP, credential, adaptateur de production, lanceur stratégique ou commande de replay n’est fourni. Sa configuration par défaut contient uniquement des valeurs non approuvées et refuse avant le premier appel API.

La [proposition de workflow](g2c-parity-v3-one-shot.yml.example) est un document JSON, également valide en YAML, situé hors de `.github/workflows/`. Les jobs ont tous une condition littérale `false` et leurs étapes terminales font `exit 1`. Même une copie accidentelle dans les workflows ne lancerait pas de calcul. Le nom du fichier, l’emplacement et ces refus sont testés.

## Base et provenance

- Base vérifiée : `main@b86453d880b32245b046e5cb7dfa3bf74862dc7c`.
- [CI post-fusion #339](https://github.com/Magassa56/agicore-v2/actions/runs/43938414914) : deux jobs réussis au SHA exact ; journaux consultés, 9 415 tests généraux et 85 portables.
- Plan immuable : `4baa39605bd3b05bd177681d0c382e923237541c770af648f35b83f47dcf552c`.
- Worker V3 et contrats historiques conservés intégralement.
- Marqueur réel consulté en lecture : absent, HTTP 404. Aucun appel réel de création de ce marqueur.
- Le seul ruleset observé protège `main`. Aucun ruleset du marqueur n’a été créé.

Le contrôleur vérifie les octets du plan, les enregistrements V2/V3/V4/V5/V5.1, la liaison de supervision, les 52 sources de la clôture V4, les sources courantes des rôles, le manifeste et le protocole gelés, la gate historique 1 000 avec son rapport négatif et son archive, ainsi que le rapport de validation #339. Les anciens enregistrements restent des preuves authentifiées par leur empreinte ; leurs anciennes sources ne sont pas assimilées à la version courante.

Aucun import des composants de trading n’est nécessaire à ces vérifications. Aucun fichier `data/`, marché réel, DEVELOPMENT réel, OOS ou broker n’est utilisé.

| Livrable | SHA-256 |
| --- | --- |
| Contrôleur versionné v1 | `a124a7f88efd7b294b8ac051bf36953fd6e2e3e3e5e0e55db387bc358e2076a5` |
| Tests du contrôleur | `b04f91668e2870b387dda55e3fac9f350cba0d45d6d0e906613ff3210aaa69d2` |
| Proposition de workflow inerte | `88693661f43bca6b362a89a29c56f5a1857357d16be9d71067b73c50aa735bed` |
| Inventaire authentifié des identités | `c4282fb8821e27d883d6d9b2232d9978657c3932d073a6aa507217deedc6280c` |

## Réservation et refus des secondes tentatives

Référence unique et fixe :

```text
refs/heads/agicore-execution-claims/g2c-parity-v3-5000-campaign-1
```

1. Le contrôleur consomme son entrée locale avant tout contrôle. Une exception ou interruption ne permet aucune réentrée de cette instance.
2. Il exige une autorisation indépendante dont l’empreinte est fournie par une source de confiance extérieure aux inputs de dispatch. Cette autorisation lie propriétaire, campagne, plan, inventaire, contrôleur, ruleset, SHA d’activation **et run_id précis**.
3. Le contexte Actions doit être authentique : dépôt, événement manuel, branche main, acteur et acteur déclenchant, `run_attempt == 1`, SHA Actions, SHA du workflow et SHA extrait égaux à l’activation approuvée.
4. Le SHA courant de main et le ruleset approuvé sont relus. Le ruleset doit être actif, viser la référence ou son namespace, interdire modification et suppression sans bypass, sans bloquer la création initiale.
5. Une lecture préalable du ref peut refuser un marqueur présent, mais elle ne constitue pas le verrou. Une absence indéterminée est refusée.
6. Un commit de reçu est créé avec le même arbre que le commit d’activation et ce commit pour parent. Son message contient les octets canoniques du reçu de réservation : aucune modification du moteur ni du plan.
7. Une seule requête `POST /git/refs` tente la création du ref fixe. Seul HTTP 201 avec identité exacte est accepté. Les concurrents peuvent préparer des objets Git orphelins ; un seul peut réserver le ref.
8. Le reçu n’est retourné qu’après vérification du commit distant. Aucun PATCH, DELETE, réarmement ou retry n’existe dans le contrôleur.

Après une réponse perdue, un 202 ambigu ou une interruption après création, le marqueur reste consommé et aucun reçu utilisable n’est délivré. Après une panne avant création, le contrôleur ne recommence pas ; un rerun a une tentative supérieure à 1 et un nouveau dispatch a un autre run_id, non couvert par l’autorisation.

Le futur adaptateur réseau devra désactiver lui aussi les retries automatiques de mutations et les redirections. Une erreur doit remonter jusqu’au refus ; elle ne doit jamais être transformée en succès.

## Vérification dans le job de calcul

Un second objet contrôleur, dans le job de calcul, revalide l’autorisation, tous les SHA, le contexte, le ruleset et `run_attempt == 1`. Il vérifie les octets canoniques du reçu transmis, le ref distant, son commit, son arbre, son parent et son run_id. Le job dépendra exclusivement du succès et des outputs du job de réservation, jamais d’un reçu fourni dans les inputs manuels.

Ce contrôle propre au calcul est indispensable lorsque GitHub réutilise les outputs d’un job précédent pour un rerun partiel. La proposition comporte un seul job de calcul, sans matrice ni chemin alternatif. L’objet du job refuse aussi une seconde entrée locale.

Le protocole suppose des contextes Actions authentiques, un adaptateur de confiance, un unique chemin de calcul dans le workflow approuvé et le maintien du ruleset. Il ne sécurise pas un administrateur retirant les protections ni un adaptateur exécutant le moteur hors de ce chemin. Ces intégrations ne sont pas encore livrées et aucune exécution de production n’est autorisée par ces simulations.

## Préflight prévu, jamais exécuté dans cette mission

Le validateur de préflight reçoit uniquement une attestation locale future, liée au claim, au run_id et au SHA d’activation. Les tests lui fournissent des valeurs inventées. Il n’interroge pas la machine et ne lance aucune sonde.

L’adaptateur futur devra, **après réservation et avant tout worker, y compris la sonde d’arrêt** :

- Mesurer Linux, cgroup-v2 et l’ascendance mémoire complète ; refuser toute valeur inconnue.
- Vérifier au moins 4 Gio de mémoire effectivement disponibles et 2 Gio de disque libre.
- Vérifier un dossier neuf, sans symlink, isolé de `data/`.
- Réutiliser le test existant d’arrêt du groupe et de ses descendants.
- Produire l’attestation depuis ces mesures ; ne jamais accepter un JSON de dispatch comme preuve de ressources.
- Réutiliser ensuite une seule fois le superviseur existant et son plan, sans retry ni reprise automatique.

| Limite | Valeur conservée |
| --- | ---: |
| CPU par worker | 150 s |
| Mur par worker | 240 s |
| Espace d’adressage | 2 147 483 648 octets |
| Taille de fichier | 67 108 864 octets |
| Logique et physique par worker | 268 435 456 octets |
| Physique du palier | 1 073 741 824 octets |

Le contrôle physique historique reste échantillonné et final ; aucun quota noyau supplémentaire ni nouvelle limite n’est prétendu. Le validateur refuse aussi une limite augmentée, remplacée par une valeur non entière ou liée à un autre claim.

## Conservation des preuves

Le marqueur et son commit restent persistants après tout échec ; aucun code de suppression ou de modification du ref n’existe. Les événements du contrôleur portent UTC, task_id, agent_id, état et identité de réservation. Ils sont exposés au futur adaptateur, sans sink réseau ou base externe dans cette version.

La future intégration devra enregistrer et vider régulièrement ces événements, conserver exceptions, préflight, logs, reçus et mesures, et collecter les preuves bornées avec `always()` même en cas d’échec normal. Un arrêt brutal du runner peut laisser les logs partiels ; le claim Git demeure. Aucun artifact Actions ni cache à rétention limitée ne remplace le verrou.

## Tests et preuves

[Preuve versionnée](../evidence/AGICORE_G2C_V3_ONE_SHOT_GUARD_SIMULATION_20261117.json) : **98 réussites**, 0 échec, 0 skip, en 2,37 s avec Python 3.12.14 / Pytest 9.0.3.

- 92 cas du nouveau contrôleur ; API Git atomique en mémoire et sentinelle ajoutant uniquement un dictionnaire à une liste.
- 6 non-régressions existantes du validateur de plan, sans worker ni replay.
- Plugin autoload et conftest désactivés ; le module des simulations interdit Popen, fork, os.system et les connexions réseau.
- Une concurrence réelle de deux threads démontre une unique réservation gagnante ; aucun sous-processus de test.
- Ruff, vérification de format et `git diff --check` réussis.
- La suite générale de 9 415 tests n’a pas été relancée. Aucun workflow CI n’est autorisé pour cette branche ; le commit de livraison conserve `[skip ci]`.

| Scénario | Résultat |
| --- | --- |
| Deux demandes concurrentes | Un seul HTTP 201 simulé, un seul passage sentinelle |
| Marqueur préexistant, même ou nouveau dispatch approuvé | Refus, marqueur conservé |
| Réponse perdue après création | Refus terminal, aucun retry, aucun reçu délivré |
| Interruption avant/après création | Refus de réentrée ; aucune remise à zéro |
| SHA, autorisation, propriétaire ou run_id incorrect | Refus avant réservation |
| Ruleset absent, inactif, incomplet, bypassable ou mauvais namespace | Refus |
| Rerun complet et rerun du seul calcul avec ancien reçu | Refus avant accès API |
| Reçu ou commit distant falsifié | Aucun passage sentinelle |
| Ressource inconnue, insuffisante ou limite modifiée | Aucun passage sentinelle |
| Échec de sentinelle après réservation | Marqueur et événements conservés |
| Configuration livrée non approuvée | Refus avant le premier appel API |

Commande reproductible avec Pytest disponible dans l’environnement :

```bash
PYTHONPATH=src:. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
PYTHONNOUSERSITE=1 python -B -m pytest -c pyproject.toml --noconftest \
  -o addopts= -p no:cacheprovider -q \
  tests/unit/test_ema_pullback_v2_g2c_one_shot_guard_v1.py \
  tests/unit/test_ema_pullback_v2_g2c_parity_v3_plan_check.py
```

Dans l’environnement de cette mission, les sources locales déjà disponibles de Pytest, Pluggy et Iniconfig ont été ajoutées au PYTHONPATH ; aucun paquet réseau n’a été installé.

## Étapes distinctes avant toute activation

Il reste à faire approuver et installer le ruleset du claim, authentifier un canal d’autorisation propriétaire indépendant, approuver le futur commit d’activation et le contrôleur, lier l’autorisation au run_id, implémenter l’adaptateur réseau sans retry, les mesures locales et la collecte durable, puis intégrer et tester le chemin unique de calcul. La présence d’une CI verte ou la fusion du présent code inerte ne vaut pas autorisation de campagne.

Une autorisation séparée sera nécessaire pour toute CI contenant des workers, puis une autre décision pour le replay G2C 5 000. Cette mission s’arrête à la PR en brouillon.

Références : [création de références Git](https://docs.github.com/en/rest/git/refs#create-a-reference), [règles de protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), [contextes Actions et run_attempt](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts).

```text
MISSION = AGICORE_G2C_V3_ONE_SHOT_EXECUTION_GUARD_IMPLEMENTATION
POSTMERGE_CI_339 = PASS
GUARD_STATE = IMPLEMENTED_INERT
NEGATIVE_TESTS = PASS; 92 GUARD CASES AND 6 READONLY NONREGRESSIONS
CLAIM_RULESET = NOT_CONFIGURED
REAL_CLAIM_REF = NOT_CREATED
ACTIVATION_SHA = NOT_APPROVED
WORKERS_LAUNCHED = 0
G2C_5000 = NOT_EXECUTED
MERGE = NOT_EXECUTED
NEXT = AGICOREMANAGER_GUARD_REVIEW
```
