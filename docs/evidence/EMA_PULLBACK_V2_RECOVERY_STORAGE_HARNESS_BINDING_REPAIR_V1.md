# EMA Pullback V2 — réparation V1 du binding du harnais de stockage

## Résultat

La suite pytest de stockage pointait encore vers la registration historique alors que le producer, le verifier, le parseur canonique et le harnais avaient déjà des octets réparés. Le binding est désormais explicite vers `EMA_PULLBACK_V2_RECOVERY_STORAGE_HARNESS_BINDING_SOURCE_REGISTRATION_V1.json`.

Cette registration est une identité supplémentaire. Elle ne remplace ni la registration historique ni la registration de réparation ciblée du parser. Elle n’autorise aucun worker, aucun replay réel, aucun claim et aucun run ID.

## Identités

| Rôle | Registration SHA-256 | Closure SHA-256 |
|---|---|---|
| `HISTORICAL_STORAGE_SOURCE` | `cb8650fa6997f021fc678b5cd28814472c4145b075572b7b06fae8876aa8d32c` | `8a188999dfeee33ea71a21327360f1d17962ab7b4083b690b08beef72233dc5c` |
| `PARSER_REPAIR_SOURCE` | `accd0fbe1501ae272cb7959930f9278ed3733b2c0277f9ebe9d3e6aa32db78cf` | `7a730b86b51fd1c063cc7ea637763009d2bf303a9d1b4afa879e99116ec077ec` |
| `HARNESS_BINDING_REPAIR_SOURCE` | `52a6c2fc2ecc7825344df6131d77282910ea5beaf3d410523da42861d9874b22` | `9f6c3edc9b787a5df7cd9bda0c2f412d69af9ea1a6cc51a9e4efa226ef7eeb73` |

La closure indépendante du verifier reste `c53540c52e8b3b98b1284dd59252ac954582e8b654376b57a4aa89201efd1487`.

## Matrice de compatibilité documentaire

| Comparaison | Producer | Verifier | Générateur | Harnais | Sélection | Reçus |
|---|---|---|---|---|---|---|
| Historique → parser réparé | modifié | modifié | inchangé | modifié | registration ciblée distincte | 66 reçus restent historiques |
| Parser réparé → binding réparé | inchangé | inchangé | inchangé | modifié | nouvelle registration versionnée | aucun reçu attribué à la nouvelle closure |

`CROSS_CLOSURE_COMPATIBILITY = NOT_ESTABLISHED`. L’identité identique du producer et du verifier entre les deux dernières closures ne suffit pas à transférer les 66 reçus historiques.

## Préflight non-worker

Commande :

```text
timeout 120s env PYTHONPATH=<deps>:<repo>/src:<repo> python -B -m pytest -q tests/unit/trading/test_ema_pullback_v2_recovery_storage_registration_v1.py
```

Résultat : `11 passed, 1 warning in 0.51s`, exit code `0`. L’avertissement concerne l’option pytest `asyncio_mode` absente de l’environnement minimal ; il n’affecte pas les contrôles exécutés.

Le préflight vérifie la sélection du nouveau binding, les deux closures, les octets producer/verifier/générateur, le codec, l’absence de cycle, le rejet fail-closed d’une dérive SHA volontaire et l’absence statique d’appel aux fonctions worker/replay interdites.

Lint ciblé Ruff 0.14.2 : `All checks passed!`, exit code `0`.

## Gouvernance

- Workers natifs, tamper, codec et statistiques : `0`.
- Batch 5 : conservé inchangé, non relancé.
- Reçus historiques : `49` natifs, `17` tamper, `0` codec, `0` statistiques.
- Données DEVELOPMENT réelles et OOS : non accédées.
- Recovery invocation : `0` ; claim non créée ; run ID non enregistré.
- Faisabilité 89 841 observations : `NOT_PROVEN`.
- Prochaine gate : autorisation séparée de continuation synthétique contrôlée.
