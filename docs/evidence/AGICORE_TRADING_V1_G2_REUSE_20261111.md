# G2 — réutilisation des preuves et frontière du moteur optimisé

État : **PARTIAL — intégration du moteur optimisé et faisabilité à 89 841 observations non démontrées**.
Base examinée : `fa70eaa417625a1f3367bab8fe3f3d3f79cee3d9`. Aucun accès à
des données DEVELOPMENT réelles ou OOS, aucune claim, aucun run de récupération.

## Preuves existantes

L'[archive formelle de #317](https://chatgpt.com/library?file_id=libfile_5fce528c02e4819190d59546c7fb6dcd&account_id=personal)
est identifiée par SHA-256 `45c47fbe04600bc0579d92532c4eccc07be0b45826d3987ec71b4922a0a0219e`.
Sa registration a pour SHA-256 `37045900d919484f2e644a36a96f94efed597ddeb6ddd927779f1ef5525426e4`,
identique aux octets de la registration portable actuelle. La closure complète est
`155a6d8349f87a0ac6a48829324f417e915daf9b48b95207884660f284b897f3`.

L'archive a été relue sans relancer de worker : ses 2 108 fichiers figurant dans
`MANIFEST.sha256` correspondent à leurs empreintes. Les 150 reçus passent :
110 natifs, 14 codec, 25 corruptions rejetées et un worker statistiques/screening.
Une reconstruction indépendante depuis les fragments a confirmé les 55 paires
de résultats natifs et les 7 paires codec, ainsi que les 6 vecteurs statistiques
et 9 cas de screening. Ces contrôles portent sur les octets et reçus conservés ;
ils ne sont pas une nouvelle campagne ni une preuve à 89 841 observations.

Le rapport historique de #316 `AGICORE_V2_PILOT_SYNTHETIC_VERIFICATION_20261028.md`
était absent de `main`. Il est repris **à l'identique** depuis le blob Git
`d1f63a24963492f08062555edabbacdd41de53c1` de `c1ac9315cc98d9208b238e42568c59cfd93880c2`.
Il décrit la campagne antérieure sous la closure
`9f6c3edc9b787a5df7cd9bda0c2f412d69af9ea1a6cc51a9e4efa226ef7eeb73` ;
ses reçus ne sont pas attribués à la closure suivante. L'échec initial de stockage
et la tentative DEVELOPMENT `FAILED_NO_RESULT / NOT_AVAILABLE` restent conservés.

## Présence sur main

Les commits de tête de #315 et #318 sont des ancêtres de la base examinée, même
si les deux PR restent en brouillon. Les quatre fichiers modifiés par #317 sont
identiques à ceux de `main` ; son commit de tête n'est pas un ancêtre de `main`.
Pour #318, cinq des six fichiers modifiés sont identiques ; le workflow diffère
uniquement par la capture des sorties de la suite complète ajoutée ultérieurement.
Le vérificateur portable, le binding et les contrôles distincts des closures sont
donc déjà présents. Les contrôles Linux post-fusion de la base sont réussis.

## Moteur optimisé et limite de raccordement

Le travail historique `f40445911d3b8c8599c0228d1342fdba0a4aecff` contient un
moteur synthétique optimisé distinct, avec des indicateurs incrémentaux et un
réducteur de cycle de vie. Sa closure n'est pas enregistrée pour une récupération
réelle et son état historique est `BLOCKED_TECHNICAL_FEASIBILITY`. Parmi les
27 sources de cette closure, 22 correspondent exactement à `main` et les cinq
modules de récupération optimisée sont absents de `main`.

Le rapport historique de ce WIP décrit 63 cas natifs comparés deux fois après
normalisation limitée de l'identité ; il ne certifie pas sa suite complète ni la
capacité à 89 841 observations. Un contrôle nouveau, borné à 60 secondes et
512 Mio d'espace d'adressage, a utilisé les cinq fichiers historiques dont les
empreintes ont été vérifiées et la fixture préengagée `impulse_profit_LONG`
(57 observations inventées). Les octets natifs complets diffèrent parce que le
runner est identifié différemment. Ils sont identiques après remplacement des
seuls champs `run_identity.runner_source_sha256` et `run_id_sha256`, puis recalcul
du champ dérivé `output_sha256`. Les identités ne sont pas modifiées dans les
résultats livrés. L'essai et ses empreintes figurent dans
`AGICORE_TRADING_V1_G2_IDENTITY_PROBE_20261111.json`.

Le producteur actuel refuse ce résultat du runner optimisé avec
`result identity/source binding mismatch`. L'auditeur indépendant le refuse
avec `native reference run binding`. Ces refus sont attendus : accepter ce runner
en lui prêtant l'identité du runner gelé falsifierait la provenance. Le nouveau
test de non-régression reconstruit une identité alternative cohérente et vérifie
ces deux refus, sans copier le moteur historique dans `main`.

Le stockage historique accepte au plus **200 observations** et **16 777 216 octets**
par flux. Un test inventé accepte 200 témoins et rejette la 201e observation.
Ces plafonds sont ceux du petit harnais, pas une mesure de capacité du moteur
sur 89 841 observations. Les mesures historiques du WIP à 1 000 et 5 000
observations portent sur une version antérieure du candidat ; elles ne prouvent
pas les ressources ou l'équivalence du candidat révisé à la taille cible.

## Travail restant

Le raccordement doit garder le runner optimisé sous sa propre identité, établir
une closure et un contrat de stockage/vérification versionnés, puis démontrer
l'équivalence et la reconstruction exactes sans affaiblir les contrôles historiques.
Un chemin pour plus de 200 observations et des mesures synthétiques non constantes,
bornées et représentatives sont encore nécessaires. L'ancien plafond de 8 Gio
sur les octets natifs reste applicable tant que l'exception documentaire relative
au stockage physique n'est pas explicitement activée. Aucune extrapolation ni
simple compression ne vaut preuve de faisabilité complète.

Le test ciblé est :

```bash
PYTHONPATH=src:. python -B -m pytest -q -o addopts= --show-capture=no \
  tests/integration/test_ema_pullback_v2_recovery_identity_boundary.py
```

Cette livraison ne modifie ni stratégie gelée, ni manifeste historique, ni preuve
existante. Elle ne déclenche pas de replay réel, d'ordre ou de fusion.
