#!/bin/bash

# Pour Your Mind - Kubernetes Deployment Script

set -e

echo "🚀 Starting Pour Your Mind Kubernetes deployment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Not connected to a Kubernetes cluster. Please connect to your cluster first."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

# Apply ConfigMaps and Secrets
echo "🔧 Applying ConfigMaps and Secrets..."
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f nginx-configmap.yaml

# Deploy PostgreSQL
echo "🐘 Deploying PostgreSQL..."
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n pour-your-mind --timeout=300s

# Deploy Django application
echo "🐍 Deploying Django application..."
kubectl apply -f django-deployment.yaml

# Wait for Django to be ready
echo "⏳ Waiting for Django to be ready..."
kubectl wait --for=condition=ready pod -l app=django-app -n pour-your-mind --timeout=300s

# Deploy Nginx
echo "🌐 Deploying Nginx..."
kubectl apply -f nginx-deployment.yaml

# Deploy Ingress (optional)
echo "🔗 Deploying Ingress..."
kubectl apply -f ingress.yaml

# Deploy HPA (optional)
echo "📈 Deploying Horizontal Pod Autoscaler..."
kubectl apply -f hpa.yaml

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 To check the status of your deployment:"
echo "   kubectl get pods -n pour-your-mind"
echo "   kubectl get services -n pour-your-mind"
echo ""
echo "🌐 To access your application:"
echo "   kubectl port-forward -n pour-your-mind service/nginx-service 8080:80"
echo "   Then open http://localhost:8080 in your browser"
echo ""
echo "📊 To view logs:"
echo "   kubectl logs -n pour-your-mind -l app=django-app"
echo "   kubectl logs -n pour-your-mind -l app=nginx"

