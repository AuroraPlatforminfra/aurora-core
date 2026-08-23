#!/bin/bash
set -e

PROJECT_ID="aurora-mlops-dev"
REGION="us-central1"
CLUSTER="aurora-core-cluster"

echo "=== Aurora Core GCP Deployment ==="

# 1. Create GKE cluster (if not exists)
echo "[1/5] Checking GKE cluster..."
if ! gcloud container clusters describe $CLUSTER --region=$REGION --project=$PROJECT_ID 2>/dev/null; then
  echo "Creating GKE cluster..."
  cd infra/terraform/gcp
  terraform init
  terraform apply -auto-approve
  cd ../../..
fi

# 2. Get credentials
echo "[2/5] Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER --region=$REGION --project=$PROJECT_ID

# 3. Build and push Docker image
echo "[3/5] Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/aurora-core:latest .
docker push gcr.io/$PROJECT_ID/aurora-core:latest

# 4. Deploy with Helm
echo "[4/5] Deploying with Helm..."
helm repo add aurora infra/helm || true
helm upgrade --install aurora-core infra/helm/aurora-core \
  --namespace aurora \
  --create-namespace \
  --values infra/helm/aurora-core/values.yaml

# 5. Wait for deployment
echo "[5/5] Waiting for deployment..."
kubectl rollout status deployment/aurora-core -n aurora --timeout=5m

echo "✓ Aurora Core deployed to GCP"
echo "Prometheus: kubectl port-forward -n aurora svc/prometheus 9090:9090"
echo "Jaeger: kubectl port-forward -n aurora svc/jaeger-ui 16686:16686"
