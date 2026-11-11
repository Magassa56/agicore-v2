# G2C — montée en charge synthétique sous contrôle

Base : `main@be96e732643d5155fedafd4de76894c52c1fb183`. Le dépôt G2B et son
contrat de 201 observations restent inchangés. Aucun marché réel, fichier
`data/`, OOS, broker, claim ni replay à 89 841 observations n'a été utilisé.

## Première registration : contrat V1

Le contrat `fce3f82e10b276fb58ba09ba19b03a78005bd299afc971632d883d951529896c`
a été publié au commit `e304337913e49b3e5248cf179c1b8c795becd273` avant les
replays. Six fixtures inventées de 1 000 observations ont chacune été produites
deux fois, vérifiées séparément et comparées au replay de référence. Les sources,
les octets natifs et les empreintes sont conservés dans le rapport et l'archive.
Le scénario dense compte 13 positions fermées, sept entrées longues, six courtes,
huit stops structurels, cinq sorties EMA20 et deux refus de risque synthétiques.
Les autres fixtures couvrent l'absence d'opportunité, la suppression en position,
l'expiration, le stop sur gap et le refus de risque.

Le rapport de palier est `AGICORE_G2C_1000_E304_TIER_REPORT_20261111.json`,
SHA-256 `38a3d05e25cbcfeaa03e2e6a11fd57648b81fc49922b0469e35cecd5626b4968`.
Les 36 contrôles sur les six bundles, dont 30 altérations rejetées, sont dans
`AGICORE_G2C_1000_E304_NEGATIVE_20261111.json`, SHA-256
`33d933c38acb839eb43c9a0926451c8e5d02136018ffa36756746e3334fdf2e9`.
Le script exact de ces contrôles est conservé en texte avec ses chemins de
l'environnement d'exécution ; pour le reproduire ailleurs, les adapter sans
changer les cas. L'archive `AGICORE_G2C_1000_E304_BUNDLES_20261111.zip`, SHA-256
`b380c7f13f36db7c1ae90e9485c66862ae2d78be732062a39d01f1ae6072f745`, contient
un bundle vérifié par fixture, les reçus des deux processus et leurs journaux.

Pour chaque bundle archivé, la reconstruction doit utiliser le code du commit
`e304337913e49b3e5248cf179c1b8c795becd273` et l'ancre V1 ci-dessus. Les SHA du
manifeste et du résultat natif attendus figurent dans le rapport de palier. Le
vérificateur contrôle les invariants et la comptabilité à partir des reçus ; il
ne recalcule pas lui-même les signaux de stratégie. La comparaison des sorties
complètes avec le moteur de référence est effectuée séparément ; une projection
d'identité temporaire reste uniquement en mémoire et n'est pas publiée.

## Correction du garde-fou et contrat V2

Le premier préflight 5 000 a confirmé les limites de processus et l'arrêt du
groupe, mais n'a pas pu lire la limite mémoire effective du cgroup. Sa mention
`status: PASS` ne constitue donc pas une validation complète pour 5 000. Ce
préflight est préservé dans `AGICORE_G2C_5000_E304_PREFLIGHT_20261111.json`.

Le contrat G2C V2 conserve les fixtures et les plafonds, et ajoute une condition
fermée : le palier 5 000 ne peut pas démarrer si la limite mémoire cgroup n'est
pas lisible ou si la marge observée est insuffisante. Ses six replays 1 000 ont
réussi sous le commit `f3f4ed0d8679aad7c6dce3589c7914e7516c6c47`, avec le
contrat `b5a00c165b150974baa6267ad3794e2e79ee0b5cdf3f432a67da0f7f1013cb13`.
Le rapport est `AGICORE_G2C_1000_F3F4_TIER_REPORT_20261111.json`, SHA-256
`20c6ccc56eb66b6c3deadf4e17eba4d4d413f10c8f098eccaf67a9b1938d41df`.

Le contrat V3 ajoute deux vérifications : refuser les appartenances cgroup
imbriquées ou ambiguës plutôt que d'utiliser par erreur la limite du groupe
racine, et vérifier la marge disque par rapport au budget total du palier. Les
registrations V1 et V2 restent inchangées. Le contrat V3 a été préengagé au
commit `9e6eadcd81c2aec152872aa7783b5374e9731568` avec le SHA-256
`5de23f01bb157b2d7575a54dcc0d36033f6ba3ae751f6338067088c895bf6663`.

La surveillance de l'occupation physique est périodique, avec vérification
finale ; elle n'est pas un quota disque instantané. Les temps et mémoires de ces
fixtures ne démontrent pas la capacité à 89 841 observations ni une performance
sur le marché.

## Résultat 1 000 sous le contrat V3

Les six fixtures ont chacune réussi deux productions et deux vérifications en
processus séparés, puis la comparaison complète avec la référence. La référence
et le runner optimisé gardent leurs propres identités ; leurs octets ne sont pas
identiques avant projection temporaire dans le test. Les résultats et témoins
stockés ont été reconstruits à l'identique, et les six bundles archivés ont été
revérifiés après extraction. Trente falsifications ont été rejetées ; six copies
intactes ont été acceptées.

| Fixture | Entrées | Fermées | Natif, octets | Temps maximal, s | CPU maximal, s | RSS maximale, octets |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Constante | 0 | 0 | 220 983 | 2,911 | 2,832 | 73 945 088 |
| Dense | 13 | 13 | 6 771 181 | 9,142 | 9,093 | 81 584 128 |
| Suppression en position | 1 | 0 | 267 874 | 6,829 | 6,727 | 74 973 184 |
| Expiration | 0 | 0 | 221 884 | 3,113 | 3,066 | 73 662 464 |
| Stop sur gap | 1 | 1 | 281 179 | 3,522 | 3,445 | 70 012 928 |
| Refus de risque | 0 | 0 | 235 558 | 3,212 | 3,174 | 74 248 192 |

Ces maximums sont ceux des processus producteur, vérificateur ou comparaison
de chaque fixture, et non le temps de la campagne entière. Le dossier du palier,
rapports et journaux compris, occupait physiquement 4 096 000 octets après
exécution. Les plafonds étaient de 90 s murales, 60 s CPU, 1 Gio d'espace
d'adressage par processus, 64 Mio par fichier et 512 Mio pour le palier. Les
contrôles négatifs, leurs copies et journaux occupaient 11 718 656 octets.

Le rapport V3 est `AGICORE_G2C_1000_9E6E_TIER_REPORT_20261111.json`, SHA-256
`c7b1c48c69f81439892082cc23bb7ddb34190775b93f528177df6a6d49dad555`. L'archive
complète des six bundles est `AGICORE_G2C_1000_9E6E_BUNDLES_20261111.zip`,
SHA-256 `8dfa4e7aa278cbc1503aae4ea48489f0330c720b2a6f6f0d49966b065c349fa7`.
Les contrôles négatifs, le contrôle de l'archive et les mesures physiques sont
conservés séparément sous le préfixe `AGICORE_G2C_1000_9E6E_`. L'archive inclut
un bundle par fixture et les reçus et journaux des deux exécutions ; son
vérificateur est le code du commit `9e6eadcd81c2aec152872aa7783b5374e9731568`.
Le profil de codec lie notamment la version de Python et le binaire zlib : une
reconstruction sur un autre environnement exige de vérifier cette compatibilité.

## Arrêt avant 5 000

Après le PASS 1 000 et les tests négatifs, le préflight V3 a constaté que
`/sys/fs/cgroup/memory.max` et `memory.current` n'étaient pas visibles. Le
contrôle est donc `BLOCKED` et aucun replay 5 000 n'a démarré. Le verdict est
`AGICORE_G2C_5000_9E6E_PREFLIGHT_20261111.json`, SHA-256
`c33f30bf6399efb0f5b96a96e365013be974d7d221f035d4e4019540eaca0c4b`.
Pour reprendre, utiliser un hôte Linux dont le cgroup mémoire effectif est
observable au niveau racine du processus, vérifier une marge mémoire d'au moins
deux fois le plafond de 2 Gio et une marge disque d'au moins deux fois le budget
du palier de 1 Gio, puis relancer le préflight et le contrôle d'arrêt du groupe.
Une appartenance cgroup imbriquée est refusée par cette version du superviseur.
