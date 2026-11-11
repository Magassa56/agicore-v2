# EMA Pullback V2 — plan de réparation du binding du harnais V1

Ce préengagement autorise uniquement une registration versionnée, le changement minimal de `SOURCE_REGISTRATION` dans le harnais pytest et un préflight sans worker.

La commande pytest complète de Batch 5 reste interdite. Le préflight dédié ne peut appeler ni `native_case`, ni `tamper_case`, ni `byte_case`, ni `statistics_cases`, ni une fonction de replay. Il vérifie les closures, le codec, la sélection statique de registration et un rejet négatif de dérive source.

Les deux registrations historiques restent immuables. Les 66 reçus historiques conservent leur closure d’origine et ne sont pas réattribués à la nouvelle closure.

Limites : 120 secondes par commande, 1 Gio d’espace d’adressage, zéro worker. Toute divergence arrête la gate sans relance de Batch 5.
