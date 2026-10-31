# AGIcore Manager V2 — cycle local minimal

Cette première version exécute une seule mission autorisée : générer des
observations inventées, les stocker dans un nouveau format, puis mesurer les
étapes V2 de détection d'impulsion, de retournement et de contexte. Elle ne
produit ni ordres, ni positions, ni PnL et ne lit aucun fichier de marché.

## Utilisation

Sous Linux, depuis la racine d'un checkout avec les dépendances du projet :

```bash
export PYTHONPATH="$PWD/src:$PWD"
python -m agicore.manager.mission_cycle_v2 \
  --output-dir /chemin/existant/mission-nouvelle \
  --observations 89841 --timeout-seconds 300
```

Le répertoire parent doit exister et le répertoire de mission ne doit pas
exister. Les chemins avec un composant `data` ou un parent symbolique sont
refusés. L'entrée est toujours générée par le code : aucune option ne permet
de fournir un fichier externe. Le nombre autorisé va de 1 à 89 841.

## Cycle et preuves

1. Le manager écrit une mission identifiée et affecte un processus Python local.
2. Ce processus écrit un bundle inventé par blocs et évalue les événements et
   le contexte, sans qualification de pullback ou étape financière.
3. Un second processus régénère l'entrée, contrôle tous les blocs, leur ordre,
   leurs tailles et empreintes, puis recalcule les mêmes étapes de replay.
4. Le manager compare les reçus et écrit un rapport `PASS` ou `FAILED` et un
   journal `events.jsonl` horodaté. Les échecs ne déclenchent aucune reprise
   automatique, et un échec du worker empêche l'exécution du vérificateur.

La vérification du stockage utilise un code distinct et ne fait pas confiance
aux octets déclarés par le producteur. Le vérificateur reconstruit séparément
le parcours des événements, en utilisant les **mêmes prédicats V2 existants** ;
ce n'est pas une seconde implémentation indépendante de ces prédicats. Les empreintes des sources et
les versions de Python et zlib sont enregistrées dans la mission. Les limites
de temps et de mémoire sont appliquées séparément à chaque processus ; les
mesures de mémoire proviennent de `wait4` sous Linux.

Le bundle `agicore:invented-observation-bundle:v2` est une preuve nouvelle et
distincte. Il ne modifie pas le harnais historique limité à 200 témoins et ne
certifie pas son ancien format ni une closure historique. Le parseur matérialise
toutes les observations ; la fenêtre des détecteurs est bornée à 21 barres.

## Limites de cette version

- Les rôles sont des adaptateurs Python locaux déterministes. Aucun modèle
  Terra, Codex ou Astra n'est appelé ; aucun fournisseur API n'est configuré.
- Les adaptateurs sont inscrits dans le code, pas chargés comme des commandes
  arbitraires. Les limites de processus ne constituent pas un bac à sable pour
  du code non fiable et n'imposent pas une isolation réseau au niveau système.
- Le replay s'arrête au contexte d'événements : pullback, entrées, sorties,
  risque, stockage natif de résultat et stratégie complète restent hors portée.
- Les missions sont synchrones et locales ; il n'y a ni service permanent,
  ni file distribuée, ni fusion de PR, ni déploiement.
