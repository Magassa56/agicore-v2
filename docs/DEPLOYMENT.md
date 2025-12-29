# Documentation du Déploiement

Ce document décrit le pipeline de CI/CD pour le projet AGIcore-v2, la configuration requise et les commandes de débogage.

## Vue d'ensemble du Pipeline CI/CD

Le pipeline est défini dans `.github/workflows/main-ci-cd.yml` et automatisé avec GitHub Actions.

1.  **Déclenchement** : Le workflow est déclenché à chaque `push` ou `pull_request` sur la branche `main`.
2.  **Détection des changements** (`changes`) : Un premier job identifie les services dont le code a été modifié (dans `services/operator` ou `services/agicore-trader`).
3.  **Tests** (`test`) : Les tests unitaires et d'intégration sont exécutés. Le pipeline s'arrête en cas d'échec.
4.  **Build & Deploy** (`build-and-deploy`) : Ce job s'exécute uniquement en cas de `push` sur `main` et si des changements ont été détectés. Il utilise une **matrice** pour lancer un déploiement en parallèle pour chaque service modifié.
    - **Build & Push** : Construit l'image Docker du service, la tague avec le `SHA` du commit et `latest`, puis la pousse sur Google Artifact Registry.
    - **Deploy** : Déploie la nouvelle image (identifiée par son SHA) sur le service Cloud Run correspondant.
    - **Smoke Test** : Après le déploiement, un test de santé vérifie que le service est bien accessible et répond avec un code HTTP 2xx.

## Configuration Requise

Le pipeline nécessite les variables et secrets suivants dans les paramètres du repository GitHub (`Settings > Secrets and variables > Actions`).

### Variables

| Nom              | Description                                        | Exemple de Valeur                 |
| ---------------- | -------------------------------------------------- | --------------------------------- |
| `GCP_PROJECT_ID` | L'ID de votre projet Google Cloud.                 | `ace-forest-420208`               |
| `GCP_REGION`     | La région pour Cloud Run et Artifact Registry.     | `europe-west1`                    |
| `GAR_REPOSITORY` | Le nom du dépôt Artifact Registry.                 | `bama`                            |

### Secrets

| Nom          | Description                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| `GCP_SA_KEY` | La clé JSON du compte de service GCP utilisé pour l'authentification. Le SA doit avoir les rôles : `Artifact Registry Writer`, `Cloud Run Developer`, `Service Account User`. |

## Services Déployés

| Nom du Service (Matrice) | Répertoire Source         | Image Artifact Registry (`DOCKER_IMAGE_NAME`) | Service Cloud Run (`CLOUD_RUN_SERVICE`) | Endpoint de Santé |
| ------------------------ | ------------------------- | --------------------------------------------- | --------------------------------------- | ----------------- |
| `operator`               | `services/operator`       | `operator`                                    | `bama-operator-agi-core-v2`             | `/`               |
| `trader`                 | `services/agicore-trader` | `agicore-trader`                              | `trader-agent`                          | `/health`         |

## Commandes de Débogage et Validation

Ces commandes sont à exécuter dans un environnement où `gcloud` est configuré et authentifié (ex: Google Cloud Shell).

### 1. Vérifier le statut d'un service Cloud Run

Remplacez `[SERVICE_NAME]` par le nom du service (ex: `trader-agent`).

```bash
gcloud run services describe [SERVICE_NAME] \
  --platform managed \
  --region europe-west1 \
  --project ace-forest-420208
```

### 2. Consulter les logs d'un service

Pour voir les logs en temps réel :
```bash
gcloud run services logs tail [SERVICE_NAME] \
  --platform managed \
  --region europe-west1 \
  --project ace-forest-420208
```

### 3. Lister les images dans Artifact Registry

Pour voir les images Docker qui ont été poussées :
```bash
gcloud artifacts docker images list europe-west1-docker.pkg.dev/ace-forest-420208/bama
```

### 4. Tester un service manuellement

Récupérez l'URL du service et testez-la avec `curl`.

```bash
# Récupérer l'URL
SERVICE_URL=$(gcloud run services describe [SERVICE_NAME] --platform managed --region europe-west1 --format 'value(status.url)')

# Tester l'endpoint
curl -v "${SERVICE_URL}/"
# Pour le trader, tester aussi /health
curl -v "${SERVICE_URL}/health"
```
