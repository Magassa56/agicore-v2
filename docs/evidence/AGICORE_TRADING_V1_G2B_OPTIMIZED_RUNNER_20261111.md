# G2B — runner optimisé et stockage synthétique versionnés

Base : `main@5c88044162df7faf866bbf9e941570db4d6f2952`, après fusion de #330.
Périmètre : données inventées, 201 observations maximum. Aucun résultat ne
constitue une validation DEVELOPMENT ni une preuve de rentabilité.

## Identités et séparation des contrats

Les cinq modules optimisés sont repris octet pour octet depuis
`f40445911d3b8c8599c0228d1342fdba0a4aecff`. Le runner conserve son propre
SHA-256 `854a6cbe7b89f3c6f0e9f49a8a5095745baf20693c2e89b115dfcadbfacbdf56`.
La nouvelle registration `EMA_PULLBACK_V2_G2B_SYNTHETIC_CONTRACT_V1.json` a pour
SHA-256 `1d5d01c390326cba6f0a4f24f3db2820832a831847f9b31a17487780f503e935` ;
sa closure de 47 sources a pour SHA-256
`17681d345cd9ddb590b584466945c18f4951b657a4665780b9c5a0cd5e0be45c`.
Elle lie le runner, les producteurs, le codec, le vérificateur, l'auditeur, les
fixtures, le manifeste de stratégie et le protocole gelé. Le SHA du contrat est
une ancre de confiance **externe** : le recalculer depuis un fichier non fiable
ne l'approuve pas. Les sources chargées ont été contrôlées pour les deux familles
de générateurs utilisées ; cela n'est pas une preuve de toutes les configurations.

Le chemin G2B appelle `run_synthetic_native_v1` et sérialise son identité native.
Le validateur historique `validate_native_result_v1` du WIP réalise une projection
vers l'identité de référence : il n'est **pas appelé** par ce chemin. Une
normalisation temporaire est utilisée seulement dans les tests différentiels ;
aucun reçu ou résultat G2B n'est réécrit avec l'identité du runner historique.

Le producteur et le vérificateur sont exécutables dans deux processus distincts.
Le vérificateur réemploie le décodeur et les fonctions d'audit historiques, sans
importer le moteur ou le producteur. L'orchestration de l'audit est séparément
versionnée pour vérifier directement l'identité optimisée. Elle recalcule les
éléments comptables et les invariants à partir des reçus ; elle ne recalcule pas
les signaux de stratégie. Le manifeste et le SHA natif attendus sont fournis par
un canal externe au bundle. Toute preuve partielle, source inconnue ou altération
vérifiée échoue fermée.

L'ancien contrat demeure inchangé à 200 observations et 16 Mio par flux. Le
contrat G2B autorise 201 observations et jusqu'à 32 Mio par flux logique en
utilisant des segments ordonnés du codec historique. La frontière 16 Mio + 1
octet a été vérifiée sur des **octets inventés de codec** ; ce n'est pas une
exécution native de cette taille ni une preuve de capacité DEVELOPMENT.

## Résultats ciblés

Les tests différentiels comparent les résultats natifs complets sur 12 fixtures
inventées : long, short, gaps, stop, expiration, refus de risque, suppression en
position, fin de données, deux positions successives et une série de 201 lignes.
Après normalisation d'identité limitée aux tests, tous les champs causaux,
quantités, frais, slippage, résultats comptables et preuves correspondent à la
référence sur ces cas. Les octets non normalisés restent distincts. Un test de
mutation future vérifie que les décisions précédentes ne changent pas.

Deux producteurs indépendants sur 201 observations ont produit les mêmes reçus
et octets natifs ; un vérificateur distinct a reconstruit et scellé le bundle,
puis l'a relu. Les tests négatifs couvrent notamment source, identité, fragment,
scellement et résultat comptable falsifiés. Le résumé des mesures est conservé
dans `AGICORE_G2B_OPTIMIZED_SYNTHETIC_201_20261111.json`, SHA-256
`e07088db5aea3a63679069ec2964f53cdb1e9f50f13c18e1f2076fa0d4d1223c`.

Sur cet essai Linux, le plus lent des deux producteurs a pris 0,905 s et atteint
52 297 728 octets de RSS ; le plus lent des deux passages du vérificateur a pris
0,554 s et atteint 48 390 144 octets de RSS. L'espace physique des deux bundles
et de leurs journaux était de 135 168 octets avant le résumé. Les temps, RSS et
espace sont des mesures de ce seul cas, pas des estimations à grande échelle.
Les processus ont été bornés à 60 s, 512 Mio d'espace d'adressage et 256 Mio par
fichier ; l'espace total a été vérifié après exécution. Le CLI ne fournit pas un
quota disque temps réel et nécessite un superviseur externe de temps mural.

## Commandes

Après installation et vérification indépendante de l'ancre du contrat :

```bash
timeout 60s env PYTHONPATH=src:. python -B -m tools.ema_pullback_v2_g2b_synthetic \
  --role produce --fixture invented-scale-201-v1 \
  --contract-sha256 1d5d01c390326cba6f0a4f24f3db2820832a831847f9b31a17487780f503e935 \
  --bundle /tmp/agicore-g2b-example
```

Conserver séparément `manifest_sha256` et `native_sha256` affichés par le
producteur, puis les fournir au vérificateur avec `--role verify --seal`, le même
contrat et le même bundle. Une lecture ultérieure retire `--seal`. Le CLI ne
prend aucune entrée de marché externe. Les bundles contiennent des résultats
comptables **synthétiques**, non des performances de marché réelles.

## Limites et suite

Les 30 tests G2B ciblés et les 56 tests de non-régression sélectionnés passent
localement. Ruff `check` passe sur les cinq sources historiques et les nouvelles
sources ; `format --check` passe sur les nouvelles sources, mais reformaterait
les cinq sources historiques, conservées identiques pour ne pas changer leur SHA.

Aucun essai à 1 000 ou 5 000 observations n'a été lancé. Le contrat actuel les
refuse : ils nécessitent une nouvelle registration des fixtures et des plafonds,
ainsi que la vérification préalable de la mémoire, du stockage et du superviseur
sur l'hôte. Les plafonds historiques de 120/600 s, 4 Gio de mémoire et 8 Gio de
sortie native ne sont pas une preuve que cet hôte les satisfait. Aucune exécution
à 89 841 observations ni récupération réelle n'est autorisée par cette livraison.
