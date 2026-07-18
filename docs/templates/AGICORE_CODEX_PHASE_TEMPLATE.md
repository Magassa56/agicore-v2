# Modèle de phase AGIcore Codex

## PHASE

`[NOM COURT ET IDENTIFIANT DE LA PHASE]`

## MISSION

Décrire en une phrase la capacité concrète à livrer et la raison de la mission.

## VALEUR UTILISATEUR

Expliquer le résultat directement observable par l'utilisateur et, si pertinent, son effet attendu sur la rentabilité.

## ÉTAT INITIAL

- Branche de départ : `[branche]`
- Commit de départ : `[SHA]`
- État du working tree : `[propre / exception expliquée]`
- Preuve de synchronisation : `[commande et résultat]`
- Capacité existante vérifiée : `[commande et résultat]`

## OBJECTIF UNIQUE

`[Un seul résultat principal, précis et testable]`

## CONDITION D'ARRÊT

La phase s'arrête lorsque `[condition observable et mesurable]`, puis STOP avant commit.

## FICHIERS AUTORISÉS

- `[chemin autorisé 1]`
- `[chemin autorisé 2]`
- Budget maximal : `[N]` fichiers.

## FICHIERS INTERDITS

- `data/`
- `.env` et tout secret
- `[autres chemins explicitement hors périmètre]`

## CONTRAINTES DE SÉCURITÉ

- Travailler offline ; aucun réseau sans autorisation explicite.
- Ne lire, modifier, ajouter, supprimer ou versionner aucune donnée de `data/`.
- Ne lire, afficher ou modifier aucun secret.
- N'effectuer aucune action réelle de broker, ordre, compte ou position.
- Ne lancer aucun tag, publication ou déploiement.
- Ne supprimer aucun fichier utilisateur.

## COMPORTEMENT ATTENDU

1. Contrôler l'état initial et la branche.
2. Analyser les modules et tests strictement nécessaires.
3. Proposer un plan minimal lié à l'objectif unique.
4. Modifier uniquement les fichiers autorisés.
5. Exécuter les tests ciblés et corriger les erreurs dans le périmètre.
6. Exécuter les intégrations concernées et la suite complète lorsque raisonnable.
7. Contrôler le diff et produire le rapport obligatoire.
8. S'arrêter avant commit.

## NON-OBJECTIFS

- `[élément explicitement exclu 1]`
- `[élément explicitement exclu 2]`
- Aucun refactoring sans lien direct avec l'objectif.
- Aucune nouvelle priorité après la réussite de cette phase.

## TESTS CIBLÉS

```text
[commande de test ciblé]
```

Critère de réussite : `[résultat attendu]`.

## SUITE COMPLÈTE

```text
[commande de la suite complète, ou justification mesurable si elle n'est pas raisonnable]
```

Critère de réussite : `[résultat attendu]`.

## CONTRÔLES GIT

Avant modification :

```text
git status --short
git diff --check
```

Après modification :

```text
git diff --check
git status --short
git diff --name-only
git diff --stat
powershell -ExecutionPolicy Bypass -File scripts/agicore-preflight.ps1
```

Vérifier explicitement que le diff ne contient que les fichiers autorisés.

## FORMAT DU RAPPORT

```text
PHASE       : [NOM]
STATUS      : OK ou BLOCKED
NEXT        : STOP avant commit

Résultat
État du produit
Modifications
Tests
Sécurité
Valeur utilisateur et rentabilité
Risques restants
Décisions demandées
Prochaine étape recommandée
Git status
```

## STOP RULE

STOP obligatoire avant commit. Attendre une validation humaine explicite avant commit, push, création de PR, fusion, tag, publication ou déploiement. En cas d'erreur non corrigeable dans le périmètre, signaler `STATUS : BLOCKED` avec la preuve et ne pas poursuivre.

## Modèle `/goal` prêt à copier

```text
/goal Réaliser [OBJECTIF UNIQUE] sans arrêter avant [CONDITION VÉRIFIABLE],
dans la limite de [NOMBRE] fichiers, puis STOP avant commit.
```

Compléter le goal avec les fichiers autorisés, les non-objectifs, les tests attendus et les barrières humaines avant son lancement.
