# AGIcore V2 — vérification synthétique du pilote

Date UTC : 2026-10-28. Périmètre : récupération et stockage synthétique EMA Pullback V2.

## Résultat

Le blocage du harnais est reproductible sur le commit
`83dbae18cb4f0655300cad1748044134269172ee`. Le test
`test_complete_native_roundtrip[impulse_profit_LONG]` s'arrête dans sa fixture
`registration` avec `StorageProofError: registered executable source changed: FAIL_CLOSED`
(code de sortie 1). Le harnais sélectionne la registration historique, dont les
empreintes ne correspondent plus au producer, au verifier, au format et au harnais
réparés. Par exemple, la registration attend le SHA-256 producer
`3f0dad5ee903e56596416ee08db8718ab4be2a20dc9cb541ef4d2cd18c853e2d`,
alors que le fichier réparé a pour SHA-256
`bbfc658310f27af6a03b34e8771205af84843b97315266098f21725ebfec03d3`.

Sur le commit `95ef7c92a8e6a4b7a7a13d34f96a480a76619991`, le même test réussit
(code de sortie 0). La correction du binding et les tests de non-régression existaient
déjà dans ce commit ; ce pilote les a reproduits et vérifiés indépendamment. Le
binding sélectionne désormais la registration
`EMA_PULLBACK_V2_RECOVERY_STORAGE_HARNESS_BINDING_SOURCE_REGISTRATION_V1.json`,
et non la registration historique. Le changement n'efface pas l'identité antérieure.

## Vérifications exécutées

| Vérification | Résultat |
| --- | --- |
| Préflight des registrations et des closures | 11 réussis |
| Tests ciblés du parseur | 24 réussis |
| Même test historique sur le commit corrigé | 1 réussi |
| Harnais complet et préflight | 126 réussis |
| Ruff ciblé | Réussi |
| Campagne supervisée formelle | 150 workers réussis sur 150 |

Les campagnes pytest ont produit un avertissement `Unknown config option:
asyncio_mode`, car le plugin `pytest-asyncio` n'était pas chargé dans cet
installation minimale. Aucun test sélectionné n'a été sauté ; le code de sortie des
campagnes réussies est 0. Le test historique a délibérément échoué avant exécution
du scénario.

La campagne formelle comprend 110 workers natifs (55 scénarios, deux répétitions
chacun), 14 workers de codec (7 scénarios, deux répétitions chacun), 25 scénarios
de corruption rejetés et 1 worker comprenant 6 vecteurs statistiques et 9 cas de
screening. Un script indépendant fourni avec l'archive a recontrôlé les 150 reçus,
reconstruit les octets natifs et codec depuis les fragments, comparé les sources,
les résultats et les manifests des 55 paires natives, et comparé les 7 paires codec.
Toutes ces comparaisons ont réussi. Les scénarios de corruption ont été rejetés ;
leurs motifs individuels sont dans `independent-audit.json`.

La campagne s'est déroulée du `2026-10-28T21:45:59.860937Z` au
`2026-10-28T21:50:39.854801Z`. Mémoire maximale rapportée par les reçus du
superviseur : 132 952 064 octets ; occupation physique du répertoire de preuve
avant `END.json` : 40 382 464 octets. Ces mesures concernent ces petits jeux
synthétiques et ne prouvent pas la faisabilité à 89 841 observations.

## Identités et preuve durable

- Commit vérifié : `95ef7c92a8e6a4b7a7a13d34f96a480a76619991`.
- Registration utilisée, SHA-256 : `52a6c2fc2ecc7825344df6131d77282910ea5beaf3d410523da42861d9874b22`.
- Closure complète, SHA-256 : `9f6c3edc9b787a5df7cd9bda0c2f412d69af9ea1a6cc51a9e4efa226ef7eeb73`.
- Registration des fixtures, SHA-256 : `60038227f5b57bf777149fad00e37ce764fc77169c5d26443aeeda664b98a714`.
- Profil formel : CPython 3.12.14, zlib 1.3.2 ; pytest 9.0.3 et Ruff 0.14.2.
- Ancienne archive d'échec consultée, SHA-256 : `34c1f0883a73f1acf857f6c650627de3c2aaf29c1b496aeb76002d0d59eab318`.
- [Archive des reçus, journaux et script de vérification](https://chatgpt.com/library?file_id=libfile_9a424f50c7c481919a66dc718a4236e5&account_id=personal),
  SHA-256 : `24d67c35aa7b97434a0984c359726e28b9989306df79e931384f05bb0aa11918`.

L'archive a été relue après enregistrement : ses octets et son SHA-256 correspondent
à la copie produite localement. Son fichier `MANIFEST.sha256` engage les membres ;
`verify_pilot_receipts.py` vérifie à nouveau les reçus et reconstructions.

## Commandes reproductibles

Exécuter les commandes dans des worktrees isolés ; `DEPS` désigne un dossier hors du
dépôt contenant pytest 9.0.3. Le profil `--formal` exige les mêmes identités
Python et zlib que la registration, pas seulement les mêmes numéros de version.
La destination de la preuve doit être nouvelle et située hors du dépôt.

```bash
# Dans un worktree détaché sur 83dbae18cb4f0655300cad1748044134269172ee :
env PYTHONPATH="$DEPS:$PWD/src:$PWD" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  PYTHONDONTWRITEBYTECODE=1 python -B -m pytest --noconftest -p no:cacheprovider \
  -q 'tests/unit/trading/test_ema_pullback_v2_recovery_storage.py::test_complete_native_roundtrip[impulse_profit_LONG]'

# Dans un worktree sur 95ef7c92a8e6a4b7a7a13d34f96a480a76619991 :
env PYTHONPATH="$DEPS:$PWD/src:$PWD" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  PYTHONDONTWRITEBYTECODE=1 python -B -m pytest --noconftest -p no:cacheprovider \
  -q tests/unit/trading/test_ema_pullback_v2_recovery_storage.py \
  tests/unit/trading/test_ema_pullback_v2_recovery_storage_registration_v1.py

env PYTHONPATH="$DEPS:$PWD/src:$PWD" PYTHONDONTWRITEBYTECODE=1 \
  python -B -m tools.ema_pullback_v2_storage_synthetic_proof \
  --registration "$PWD/docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_HARNESS_BINDING_SOURCE_REGISTRATION_V1.json" \
  --destination "$NEW_PROOF_DIRECTORY" --formal
```

## Limites

Les 150 reçus appartiennent à la nouvelle closure. Ils ne remplacent pas les 66
reçus historiques et ne démontrent pas une compatibilité générale entre closures.
Les entrées de test étaient inventées ; aucun fichier de données de marché réelles
n'a été ouvert pour les tests, aucun replay réel ni ordre n'a été effectué. La suite
complète du dépôt, la faisabilité sur 89 841 observations, la performance financière
et l'aptitude au paper trading ne sont pas certifiées par ce pilote. La PR existante
sur le vérificateur portable est distincte et reste en brouillon.
