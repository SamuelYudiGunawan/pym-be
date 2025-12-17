# Deploy Pour Your Mind to Oracle Cloud OKE (PowerShell version)
# 
# Prerequisites:
# 1. OKE cluster created and running
# 2. kubectl configured with OKE cluster
# 3. OCI CLI configured
# 4. Docker installed

$ErrorActionPreference = "Stop"

# Configuration - UPDATE THESE VALUES
$OCI_REGION = "iad"  # e.g., iad (US-Ashburn), phx (US-Phoenix), fra (Germany)
$OCI_NAMESPACE = "your-tenancy-namespace"  # Your OCI tenancy namespace
$BACKEND_IMAGE_TAG = "v1"
$FRONTEND_IMAGE_TAG = "v1"

# Derived values
$BACKEND_IMAGE = "${OCI_REGION}.ocir.io/${OCI_NAMESPACE}/pym-backend:${BACKEND_IMAGE_TAG}"
$FRONTEND_IMAGE = "${OCI_REGION}.ocir.io/${OCI_NAMESPACE}/pym-frontend:${FRONTEND_IMAGE_TAG}"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Deploying Pour Your Mind to Oracle Cloud OKE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend Image: $BACKEND_IMAGE"
Write-Host "Frontend Image: $FRONTEND_IMAGE"
Write-Host ""

# Step 1: Create namespace
Write-Host "Step 1: Creating namespace..." -ForegroundColor Yellow
kubectl apply -f namespace.yaml

# Step 2: Create OCI Registry Secret (if not exists)
Write-Host "Step 2: Checking OCI registry secret..." -ForegroundColor Yellow
$secretExists = kubectl get secret oci-registry-secret -n pour-your-mind 2>$null
if (-not $secretExists) {
    Write-Host "Creating OCI registry secret..."
    $OCI_USERNAME = Read-Host "OCI Username (namespace/email)"
    $OCI_AUTH_TOKEN = Read-Host "OCI Auth Token" -AsSecureString
    $OCI_EMAIL = Read-Host "Email"
    
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($OCI_AUTH_TOKEN)
    $PlainToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    
    kubectl create secret docker-registry oci-registry-secret `
        --namespace=pour-your-mind `
        --docker-server="${OCI_REGION}.ocir.io" `
        --docker-username="$OCI_USERNAME" `
        --docker-password="$PlainToken" `
        --docker-email="$OCI_EMAIL"
}

# Step 3: Apply ConfigMaps and Secrets
Write-Host "Step 3: Applying ConfigMaps and Secrets..." -ForegroundColor Yellow
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

# Step 4: Apply Persistent Volume Claim
Write-Host "Step 4: Applying Persistent Volume Claim..." -ForegroundColor Yellow
kubectl apply -f postgres-pvc.yaml

# Step 5: Deploy PostgreSQL
Write-Host "Step 5: Deploying PostgreSQL..." -ForegroundColor Yellow
kubectl apply -f postgres-deployment.yaml

Write-Host "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/postgres -n pour-your-mind

# Step 6: Deploy Django backend
Write-Host "Step 6: Deploying Django backend..." -ForegroundColor Yellow
$deploymentYaml = Get-Content django-deployment.yaml -Raw
$deploymentYaml = $deploymentYaml -replace "<region>.ocir.io/<namespace>/pym-backend:v1", $BACKEND_IMAGE
$deploymentYaml | kubectl apply -f -

Write-Host "Waiting for Django backend to be ready..."
kubectl wait --for=condition=available --timeout=180s deployment/django-app -n pour-your-mind

# Step 7: Get backend LoadBalancer IP
Write-Host "Step 7: Getting backend LoadBalancer IP..." -ForegroundColor Yellow
Write-Host "Waiting for LoadBalancer IP (this may take a few minutes)..."
$BACKEND_IP = ""
while (-not $BACKEND_IP) {
    $BACKEND_IP = kubectl get service django-service -n pour-your-mind -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
    if (-not $BACKEND_IP) {
        Write-Host "Still waiting for backend LoadBalancer IP..."
        Start-Sleep -Seconds 10
    }
}
Write-Host "Backend LoadBalancer IP: $BACKEND_IP" -ForegroundColor Green

# Step 8: Apply frontend ConfigMap
Write-Host "Step 8: Applying frontend ConfigMap..." -ForegroundColor Yellow
kubectl apply -f ..\pym_fe\k8s\configmap.yaml

# Step 9: Deploy frontend
Write-Host "Step 9: Deploying SvelteKit frontend..." -ForegroundColor Yellow
$frontendYaml = Get-Content ..\pym_fe\k8s\deployment.yaml -Raw
$frontendYaml = $frontendYaml -replace "<region>.ocir.io/<namespace>/pym-frontend:v1", $FRONTEND_IMAGE
$frontendYaml | kubectl apply -f -

Write-Host "Waiting for SvelteKit frontend to be ready..."
kubectl wait --for=condition=available --timeout=180s deployment/frontend-app -n pour-your-mind

# Step 10: Get frontend LoadBalancer IP
Write-Host "Step 10: Getting frontend LoadBalancer IP..." -ForegroundColor Yellow
Write-Host "Waiting for LoadBalancer IP (this may take a few minutes)..."
$FRONTEND_IP = ""
while (-not $FRONTEND_IP) {
    $FRONTEND_IP = kubectl get service frontend-service -n pour-your-mind -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
    if (-not $FRONTEND_IP) {
        Write-Host "Still waiting for frontend LoadBalancer IP..."
        Start-Sleep -Seconds 10
    }
}
Write-Host "Frontend LoadBalancer IP: $FRONTEND_IP" -ForegroundColor Green

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend URL: http://$FRONTEND_IP" -ForegroundColor Green
Write-Host "Backend API:  http://$BACKEND_IP/api" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update FRONTEND_URL in configmap.yaml to: http://$FRONTEND_IP"
Write-Host "2. Update ORIGIN in pym_fe/k8s/configmap.yaml to: http://$FRONTEND_IP"
Write-Host "3. Rebuild and redeploy frontend with: --build-arg VITE_API_URL=http://$($BACKEND_IP)/api"
Write-Host "4. Re-apply the configmaps: kubectl apply -f configmap.yaml"
Write-Host ""
Write-Host "To view pods: kubectl get pods -n pour-your-mind"
Write-Host "To view logs: kubectl logs -l app=django-app -n pour-your-mind"


