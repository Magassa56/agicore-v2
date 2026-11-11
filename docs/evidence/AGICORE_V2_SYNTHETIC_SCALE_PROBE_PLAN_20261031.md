# AGIcore V2 — plan de mesure synthétique à 89 841 observations

Le volume demandé sera généré en mémoire, sans lecture de fichier de marché :
89 841 lignes OHLCV Last/minute inventées, horodatées à partir de 2099, avec des
variations et des interruptions d'horloge déterministes. Le volume et le format
sont représentatifs ; la distribution des prix n'est pas un modèle de marché réel.

Le traitement appelle le parseur V2 existant puis le détecteur d'impulsion
existants sur chaque observation, en conservant une fenêtre de 21 observations
pour le détecteur. Chaque évaluation complète est sérialisée avec le sérialiseur
canonique V2 et ajoutée à une empreinte SHA-256. Le parseur matérialise toutefois
toutes les observations en mémoire. Aucun replay complet, ordre, broker, métrique
de résultat financier ou calcul de rentabilité ne sera exécuté.

Deux exécutions indépendantes seront lancées dans des processus Linux distincts,
avec une limite d'espace d'adressage de 4 Gio et un délai maximal de 300 secondes
chacune. Elles enregistreront les empreintes des entrées et des évaluations, les
versions et empreintes de sources, le temps mural, le temps CPU, le débit et le
maximum de mémoire RSS. Les empreintes devront être identiques entre répétitions.

Le stockage de preuve synthétique existant garde sa limite de 200 observations :
un test vérifie explicitement son rejet d'une 201e ligne. La présente mesure ne
prouve donc ni le stockage de 89 841 observations, ni la faisabilité du replay V2
complet, ni une équivalence de performance ou de stratégie sur données réelles.
Les reçus des anciennes closures ne sont ni modifiés ni réattribués.
