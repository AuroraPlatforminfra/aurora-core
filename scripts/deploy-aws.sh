#!/bin/bash
set -e

REGION="us-east-1"
CLUSTER="aurora-core-cluster"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/aurora-core"

echo "========================================================================"
echo "  AURORA CORE - AWS EKS DEPLOYMENT"
echo "========================================================================"
echo "AWS Account: $ACCOUNT_ID"
echo "Region: $REGION"
echo "Cluster: $CLUSTER"
echo "ECR Repository: $ECR_REPO"
echo ""

# 1. Provision infrastructure
echo "[1/7] Provisioning AWS infrastructure with Terraform..."
cd infra/terraform/aws
terraform init -upgrade
terraform apply -auto-approve -input=false
CLUSTER_NAME=$(terraform output -raw cluster_name)
ECR_URL=$(terraform output -raw ecr_repository_url)
DB_ENDPOINT=$(terraform output -raw db_endpoint)
cd ../../..

echo "Infrastructure provisioned:"
echo "  Cluster: $CLUSTER_NAME"
echo "  Database: $DB_ENDPOINT"
echo "  ECR: $ECR_URL"
echo ""

# 2. Get cluster credentials
echo "[2/7] Retrieving EKS cluster credentials..."
aws eks update-kubeconfig \
  --region=$REGION \
  --name=$CLUSTER_NAME \
  --alias=aurora-core

kubectl cluster-info

# 3. Create ECR repository if needed
echo "[3/7] Preparing ECR repository..."
aws ecr get-login-password --region=$REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# 4. Build Docker image
echo "[4/7] Building Docker image..."
docker build -t $ECR_URL:latest -t $ECR_URL:$(git rev-parse --short HEAD) .
echo "Image built: $ECR_URL:latest"

# 5. Push to ECR
echo "[5/7] Pushing to ECR..."
docker push $ECR_URL:latest
docker push $ECR_URL:$(git rev-parse --short HEAD)

# 6. Create namespace and secrets
echo "[6/7] Creating Kubernetes namespace and secrets..."
kubectl create namespace aurora --dry-run=client -o yaml | kubectl apply -f -

DB_HOST=$(echo $DB_ENDPOINT | cut -d: -f1)
kubectl create secret generic aurora-db \
  --from-literal=host=$DB_HOST \
  --from-literal=name=aurora \
  --from-literal=user=aurora \
  --from-literal=password=changeme \
  --namespace=aurora \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic aurora-github \
  --from-literal=token='' \
  --namespace=aurora \
  --dry-run=client -o yaml | kubectl apply -f -

# 7. Deploy with Helm
echo "[7/7] Deploying Aurora Core with Helm..."
helm upgrade --install aurora-core infra/helm/aurora-core \
  --namespace aurora \
  --create-namespace \
  --set image.repository=$ECR_URL \
  --set image.tag=latest \
  --wait \
  --timeout 5m

echo ""
echo "========================================================================"
echo "  DEPLOYMENT COMPLETE"
echo "========================================================================"
echo ""
echo "Verify deployment:"
echo "  kubectl get pods -n aurora"
echo "  kubectl get svc -n aurora"
echo ""
echo "Access Aurora Core:"
echo "  kubectl port-forward -n aurora svc/aurora-core 8000:8000"
echo ""
echo "Access Prometheus:"
echo "  kubectl port-forward -n aurora svc/prometheus 9090:9090"
echo "  http://localhost:9090"
echo ""
echo "Access Jaeger UI:"
echo "  kubectl port-forward -n aurora svc/jaeger-ui 16686:16686"
echo "  http://localhost:16686"
echo ""
echo "View logs:"
echo "  kubectl logs -n aurora -l app=aurora-core -f"
echo ""
echo "Database connection:"
echo "  psql -h $DB_HOST -U aurora -d aurora"
echo ""
