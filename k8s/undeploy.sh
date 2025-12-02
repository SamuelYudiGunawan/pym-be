#!/bin/bash

# Pour Your Mind - Kubernetes Undeployment Script

set -e

echo "🗑️  Starting Pour Your Mind Kubernetes undeployment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

echo "⚠️  This will delete all resources in the pour-your-mind namespace."
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Undeployment cancelled."
    exit 1
fi

# Delete all resources
echo "🗑️  Deleting all resources..."
kubectl delete -f hpa.yaml --ignore-not-found=true
kubectl delete -f ingress.yaml --ignore-not-found=true
kubectl delete -f nginx-deployment.yaml --ignore-not-found=true
kubectl delete -f django-deployment.yaml --ignore-not-found=true
kubectl delete -f postgres-deployment.yaml --ignore-not-found=true
kubectl delete -f postgres-pvc.yaml --ignore-not-found=true
kubectl delete -f nginx-configmap.yaml --ignore-not-found=true
kubectl delete -f secret.yaml --ignore-not-found=true
kubectl delete -f configmap.yaml --ignore-not-found=true

# Delete namespace (this will delete any remaining resources)
echo "🗑️  Deleting namespace..."
kubectl delete namespace pour-your-mind --ignore-not-found=true

echo "✅ Undeployment completed successfully!"

