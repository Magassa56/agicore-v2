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
registrations V1 et V2 restent inchangées. Aucun replay 5 000 n'a été lancé
pendant le premier préflight.

La surveillance de l'occupation physique est périodique, avec vérification
finale ; elle n'est pas un quota disque instantané. Les temps et mémoires de ces
fixtures ne démontrent pas la capacité à 89 841 observations ni une performance
sur le marché. Les replays 1 000 de V3 restent à exécuter après préengagement.
