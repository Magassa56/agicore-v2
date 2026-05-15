# Cloud — AGIcore-v2

> Couche concernée : transverse (déploiement de L1–L5).

---

## 1. Providers

| Rôle | Provider |
|---|---|
| Principal | AWS |
| Secondaire | GCP |

---

## 2. Services AWS prioritaires

| Service | Usage |
|---|---|
| EC2 | Workloads persistants (orchestrator, agents long-running) |
| Lambda | Tâches courtes, event-driven, perception L1 |
| S3 | Stockage de données brutes, backtests, snapshots LTM |
| RDS (PostgreSQL) | LTM production |
| ECS / Fargate | Conteneurs sans gérer EC2 |
| ElastiCache (Redis) | STM partagée |
| CloudWatch | Logs et métriques |

---

## 3. Infrastructure as Code

| Outil | Quand l'utiliser |
|---|---|
| Terraform | Multi-cloud, écosystème mature |
| AWS CDK | AWS-only, IaC en Python |

Choix par défaut : **Terraform** pour la portabilité.

Tout changement infra passe par un PR avec `terraform plan` collé en commentaire.

---

## 4. CI/CD

- **GitHub Actions** comme runner principal
- Workflows attendus :
  - `ci.yml` : lint + tests sur chaque PR
  - `cd-staging.yml` : déploiement automatique sur staging à chaque merge `main`
  - `cd-prod.yml` : déploiement manuel sur prod (release tag)

Tout déploiement cloud (coût) demande **confirmation explicite** de J'ai.

---

## 5. Containers

| Outil | Quand |
|---|---|
| Docker | Toujours pour les services déployés |
| Kubernetes | Seulement si l'orchestration multi-conteneurs devient ingérable autrement |

Préférer Fargate / serverless tant que possible — éviter l'overhead K8s.

---

## 6. Monitoring

- **CloudWatch** par défaut (logs + métriques + alarmes)
- **Grafana** possible pour dashboards consolidés
- **Sentry** ou équivalent pour les erreurs applicatives

Métriques minimales par agent :
- requêtes / minute
- latence p50, p95, p99
- taux d'erreur
- coût LLM cumulé

---

## 7. Coûts — règles dures

- Privilégier serverless (Lambda, Fargate) sur EC2 quand le pattern d'usage est intermittent
- Spot instances pour les workloads tolérants aux interruptions (backtesting massif)
- Alarme budgétaire AWS configurée à 80 % du budget mensuel
- Tout service > 50 USD/mois doit avoir une justification écrite
- Aucun service "always on" sans monitoring de coût

---

## 8. Secrets

- Jamais dans le repo
- AWS Secrets Manager pour la prod
- `.env` local en dev, jamais committé
- Rotation des clés API : trimestrielle minimum
