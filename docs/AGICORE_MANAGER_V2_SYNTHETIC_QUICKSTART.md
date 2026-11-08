# AGIcoreManager V2 — mission synthétique candidate

Cette version exécute des scénarios inventés dans deux processus Python locaux,
avec `AgentOrchestrator` et `Dispatcher`. Les rôles sont des adaptateurs locaux :
aucun modèle Terra, Sol ou Astra n'est appelé par le runtime. La démonstration est
limitée aux profils fixes fournis ; elle n'établit ni performance de marché ni
rentabilité.

## Installation Linux

La version exercée utilise Linux et CPython 3.12. Le Manager dépend de primitives
Linux : l'exécution native sous Windows n'est pas validée. Un environnement Linux
séparé, éventuellement WSL, est requis sur Windows ; WSL n'a pas été testé ici.

Depuis un clone propre positionné sur le commit de la PR candidate :

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-synthetic-rc1.txt
python -m pip install --no-build-isolation --no-deps -e .
python -m pip check
```

Le fichier de dépendances fixe les versions observées en validation Linux ; il
ne verrouille pas les empreintes des paquets, l'interpréteur ni le système. Pour
une vérification hors réseau, les dépendances doivent être préalablement fournies
depuis une source de confiance. Une installation hors ligne avec des paquets déjà
présents ne prouve pas leur provenance.

## Exécuter une mission

Choisir un répertoire absolu **nouveau**, dont le parent existe déjà, sans lien
symbolique et hors d'un répertoire `data`. Cet exemple suit un scénario long de
39 observations inventées jusqu'à une sortie sur stop :

```sh
python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/agicore-rc1-stop-long \
  --observations 39 --timeout-seconds 30 \
  --stage exit --profile confirmation-long-exit-stop-v1 \
  > /tmp/agicore-rc1-stop-long-cli.json
```

Les autres profils fixes sont `confirmation-long-v1` et
`confirmation-short-v1` (position encore ouverte en fin de données),
`confirmation-long-rejected-v1` et `confirmation-short-rejected-v1` (risque
refusé), `confirmation-short-exit-stop-v1`, et les profils
`confirmation-long-exit-ema-v1` / `confirmation-short-exit-ema-v1`. Les étapes
`confirmation`, `stop`, `risk`, `entry` et `exit` s'arrêtent respectivement à
la confirmation, au stop, à la décision de risque, à l'entrée simulée ou à la
sortie simulée. Les étapes `events` et `pullback` disposent aussi du générateur
`standard` ; la valeur par défaut est de 64 observations.

L'étape `entry` produit une évaluation d'entrée simulée et, si elle est remplie,
un enregistrement dimensionné et un stop lié. L'étape `exit` construit ensuite
une position virtuelle et suit l'ordre des observations : gap du stop à
l'ouverture, éventuelle sortie EMA en attente à l'ouverture, stop intrabar, puis
signal EMA au close. Un risque refusé ne crée aucune entrée. La règle V2 gelée
prévoit un budget **structurel planifié** de 100 USD et 1 à 2 contrats MNQ ; ce
budget ne garantit pas une perte réelle maximale. Aucun objectif de prix ni
stop suiveur n'est ajouté.

La mission crée sur disque `mission.json`, `events.jsonl`,
`orchestrator.sqlite3`, les sorties des processus, le répertoire `bundle/` et
`report.json`. Le producteur et le vérificateur régénèrent et comparent les
observations et les reçus dans des processus distincts. Ils partagent cependant
le générateur et des prédicats V2 : ce n'est pas une implémentation entièrement
indépendante. Les empreintes détectent les changements par rapport aux points de
contrôle locaux ; elles ne constituent pas une signature contre une modification
conjointe de la base et des preuves.

## Reprise et diagnostic

Pour reprendre une mission existante, conserver son répertoire et ne fournir
aucune substitution de profil, de nombre ou de délai :

```sh
python -m agicore.manager.mission_cycle_v2 \
  --output-dir /tmp/agicore-rc1-stop-long --resume \
  > /tmp/agicore-rc1-stop-long-resume.json
cmp /tmp/agicore-rc1-stop-long-cli.json /tmp/agicore-rc1-stop-long-resume.json
```

La reprise vérifie notamment contrat, sources, versions d'exécution, journaux,
tâches et reçus. Les états `running`, échoués ou ambigus, les anciennes missions
sans scellement et les preuves altérées sont refusés ; certaines interruptions ne
peuvent donc pas être reprises automatiquement. Conserver les fichiers et lire
`report.json`, `events.jsonl` ainsi que les sorties `worker.stderr` et
`verifier.stderr` pour le diagnostic. Ne pas relancer une tâche dont l'état
reste incertain.

Le superviseur limite le temps, la mémoire et les fichiers des enfants locaux
fiables. Il n'impose pas de sandbox réseau et ne supervise pas tous les
éventuels descendants de ces processus. Il doit rester mono-thread lors du
lancement des adaptateurs. Le parseur valide l'entrée entière avant la boucle
causale : une ligne future malformée peut entraîner un refus avant la décision.
Le nettoyage suppose qu'aucun autre gestionnaire ne récolte simultanément ses
enfants ; la récupération d'un PID et l'arrêt de son groupe ne sont pas
atomiques. Les signaux usuels sont masqués pendant le lancement, mais une
exception arbitraire avant le retour de `Popen` n'est pas entièrement couverte.
L'inventaire des sources ignore toute entrée nommée `data` avant de consulter
ses métadonnées et refuse les liens symboliques dans les racines parcourues.
Il suppose toutefois que l'arbre source ne change pas de manière hostile
pendant le contrôle ; les vérifications de chemins ne sont pas atomiques.

## Limites et retour arrière

Les scénarios synthétiques sont petits et fixes ; ils ne certifient pas le replay
complet à 89 841 observations, une validation DEVELOPMENT, un paper trading ou
un fonctionnement sur compte réel. Aucun broker ni ordre réel n'est autorisé.
Les métriques financières, frais et slippage ne sont pas un livrable de cette
candidate. Le contrat historique `engineering_mission.py` et son paquet de
preuves d'origine n'ont pas été retrouvés dans les emplacements accessibles.

Le risque est précédé par le contrôle d'admission V2 pour le premier signal
des profils fixes, avec une position initialement vide. Cette démonstration ne
couvre pas les positions préexistantes, plusieurs opportunités successives ou
une équivalence générale de tous les parcours du moteur gelé.

Le Manager accepte les profils fixes avec une entrée simulée exécutable ou un
risque refusé. Une entrée expirée, faute d'ouverture suivante ou à cause d'un
écart temporel, est traitée par les fonctions de replay mais reste refusée par
le contrôle du Manager : elle ne constitue donc pas une mission validée. La
sortie synthétique retourne désormais `SyntheticExitBookV2` ; la compatibilité
de type avec les consommateurs externes de l'ancien livre n'est pas établie.

La preuve historique distincte de la campagne supervisée de 150 scénarios est
référencée par la [PR #316](https://github.com/Magassa56/agicore-v2/pull/316) ;
elle est conservée séparément et ne remplace pas les identités précédentes. Sa
CI historique n'est pas une CI verte de cette candidate.

Avant fusion, arrêter l'utilisation de la branche candidate suffit pour revenir
à l'état précédent : conserver les répertoires de missions et utiliser un nouveau
clone sur le commit connu. Après une éventuelle fusion autorisée, un retour par
commit de réversion doit être préparé et revu ; ne pas réécrire l'historique ni
supprimer les preuves. Aucune fusion, release ou mise en production n'est
réalisée par ces commandes.
