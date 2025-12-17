#!/bin/bash
# Deploy Pour Your Mind to Oracle Cloud OKE
# 
# Prerequisites:
# 1. OKE cluster created and running
# 2. kubectl configured with OKE cluster
# 3. OCI CLI configured
# 4. Docker installed

set -e

# Configuration - UPDATE THESE VALUES
OCI_REGION="iad"  # e.g., iad (US-Ashburn), phx (US-Phoenix), fra (Germany)
OCI_NAMESPACE="your-tenancy-namespace"  # Your OCI tenancy namespace
BACKEND_IMAGE_TAG="v1"
FRONTEND_IMAGE_TAG="v1"

# Derived values
BACKEND_IMAGE="${OCI_REGION}.ocir.io/${OCI_NAMESPACE}/pym-backend:${BACKEND_IMAGE_TAG}"
FRONTEND_IMAGE="${OCI_REGION}.ocir.io/${OCI_NAMESPACE}/pym-frontend:${FRONTEND_IMAGE_TAG}"

echo "============================================"
echo "Deploying Pour Your Mind to Oracle Cloud OKE"
echo "============================================"
echo ""
echo "Backend Image: ${BACKEND_IMAGE}"
echo "Frontend Image: ${FRONTEND_IMAGE}"
echo ""

# Step 1: Create namespace
echo "Step 1: Creating namespace..."
kubectl apply -f namespace.yaml

# Step 2: Create OCI Registry Secret (if not exists)
echo "Step 2: Checking OCI registry secret..."
if ! kubectl get secret oci-registry-secret -n pour-your-mind > /dev/null 2>&1; then
    echo "Creating OCI registry secret..."
    echo "Please enter your OCI details:"
    read -p "OCI Username (namespace/email): " OCI_USERNAME
    read -s -p "OCI Auth Token: " OCI_AUTH_TOKEN
    echo ""
    read -p "Email: " OCI_EMAIL
    
    kubectl create secret docker-registry oci-registry-secret \
        --namespace=pour-your-mind \
        --docker-server="${OCI_REGION}.ocir.io" \
        --docker-username="${OCI_USERNAME}" \
        --docker-password="${OCI_AUTH_TOKEN}" \
        --docker-email="${OCI_EMAIL}"
fi

# Step 3: Apply ConfigMaps and Secrets
echo "Step 3: Applying ConfigMaps and Secrets..."
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

# Step 4: Apply Persistent Volume Claim
echo "Step 4: Applying Persistent Volume Claim..."
kubectl apply -f postgres-pvc.yaml

# Step 5: Deploy PostgreSQL
echo "Step 5: Deploying PostgreSQL..."
kubectl apply -f postgres-deployment.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/postgres -n pour-your-mind

# Step 6: Update backend deployment with correct image
echo "Step 6: Deploying Django backend..."
sed "s|<region>.ocir.io/<namespace>/pym-backend:v1|${BACKEND_IMAGE}|g" django-deployment.yaml | kubectl apply -f -

# Wait for backend to be ready
echo "Waiting for Django backend to be ready..."
kubectl wait --for=condition=available --timeout=180s deployment/django-app -n pour-your-mind

# Step 7: Get backend LoadBalancer IP
echo "Step 7: Getting backend LoadBalancer IP..."
echo "Waiting for LoadBalancer IP (this may take a few minutes)..."
BACKEND_IP=""
while [ -z "$BACKEND_IP" ]; do
    BACKEND_IP=$(kubectl get service django-service -n pour-your-mind -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ -z "$BACKEND_IP" ]; then
        echo "Still waiting for backend LoadBalancer IP..."
        sleep 10
    fi
done
echo "Backend LoadBalancer IP: ${BACKEND_IP}"

# Step 8: Apply frontend ConfigMap
echo "Step 8: Applying frontend ConfigMap..."
kubectl apply -f ../pym_fe/k8s/configmap.yaml

# Step 9: Deploy frontend
echo "Step 9: Deploying SvelteKit frontend..."
sed "s|<region>.ocir.io/<namespace>/pym-frontend:v1|${FRONTEND_IMAGE}|g" ../pym_fe/k8s/deployment.yaml | kubectl apply -f -

# Wait for frontend to be ready
echo "Waiting for SvelteKit frontend to be ready..."
kubectl wait --for=condition=available --timeout=180s deployment/frontend-app -n pour-your-mind

# Step 10: Get frontend LoadBalancer IP
echo "Step 10: Getting frontend LoadBalancer IP..."
echo "Waiting for LoadBalancer IP (this may take a few minutes)..."
FRONTEND_IP=""
while [ -z "$FRONTEND_IP" ]; do
    FRONTEND_IP=$(kubectl get service frontend-service -n pour-your-mind -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ -z "$FRONTEND_IP" ]; then
        echo "Still waiting for frontend LoadBalancer IP..."
        sleep 10
    fi
done
echo "Frontend LoadBalancer IP: ${FRONTEND_IP}"

echo ""
echo "============================================"
echo "Deployment Complete!"
echo "============================================"
echo ""
echo "Frontend URL: http://${FRONTEND_IP}"
echo "Backend API:  http://${BACKEND_IP}/api"
echo ""
echo "Next steps:"
echo "1. Update FRONTEND_URL in configmap.yaml to: http://${FRONTEND_IP}"
echo "2. Update ORIGIN in pym_fe/k8s/configmap.yaml to: http://${FRONTEND_IP}"
echo "3. Rebuild and redeploy frontend with: --build-arg VITE_API_URL=http://${BACKEND_IP}/api"
echo "4. Re-apply the configmaps: kubectl apply -f configmap.yaml"
echo ""
echo "To view pods: kubectl get pods -n pour-your-mind"
echo "To view logs: kubectl logs -l app=django-app -n pour-your-mind"
