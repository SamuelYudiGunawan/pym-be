# Pour Your Mind - Kubernetes Deployment on Oracle Cloud OKE

This guide walks you through deploying Pour Your Mind to Oracle Cloud Kubernetes Engine (OKE) for free.

## 🏗️ Architecture

```
                         Internet
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌───────────────────┐               ┌───────────────────┐
│   OCI Load        │               │   OCI Load        │
│   Balancer        │               │   Balancer        │
│   (Frontend)      │               │   (Backend API)   │
│   Port 80         │               │   Port 80         │
└─────────┬─────────┘               └─────────┬─────────┘
          │                                   │
          ▼                                   ▼
┌─────────────────────────────────────────────────────────┐
│                    OKE Cluster                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │ SvelteKit   │ │ Django      │ │  PostgreSQL     │   │
│  │ Frontend    │ │ Backend     │ │  Database       │   │
│  │ (2 pods)    │ │ (2 pods)    │ │  (1 pod + PVC)  │   │
│  └─────────────┘ └─────────────┘ └─────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │     Ampere A1 Worker Nodes (Always Free!)       │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

1. **Oracle Cloud Account** (Free tier)
   - Go to [cloud.oracle.com/free](https://www.oracle.com/cloud/free/)
   - Sign up (no credit card required for most regions)

2. **Tools installed locally**:
   - Docker Desktop
   - kubectl
   - OCI CLI

## 🚀 Step-by-Step Deployment

### Step 1: Create OKE Cluster

1. Go to Oracle Cloud Console → **Developer Services** → **Kubernetes Clusters (OKE)**
2. Click **Create Cluster** → **Quick Create**
3. Configure:
   - **Name**: `pym-cluster`
   - **Kubernetes Version**: Latest
   - **Shape**: `VM.Standard.A1.Flex` (FREE!)
   - **OCPUs**: 2
   - **Memory**: 12 GB
   - **Number of Nodes**: 2
4. Click **Next** → **Create Cluster**
5. Wait ~10 minutes for cluster to be ready

### Step 2: Configure kubectl

```powershell
# Install OCI CLI (if not installed)
# Windows PowerShell:
Invoke-WebRequest https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.ps1 -OutFile install.ps1
.\install.ps1 -AcceptAllDefaults

# Configure OCI CLI
oci setup config

# Get kubeconfig for your cluster
# Find cluster OCID in OKE console
oci ce cluster create-kubeconfig `
    --cluster-id <your-cluster-ocid> `
    --file $HOME\.kube\config `
    --region <your-region> `
    --token-version 2.0.0

# Verify connection
kubectl get nodes
```

### Step 3: Set Up Container Registry (OCIR)

1. Go to **Developer Services** → **Container Registry**
2. Create two repositories:
   - `pym-backend`
   - `pym-frontend`

3. Create Auth Token:
   - Profile → **User Settings** → **Auth Tokens** → **Generate Token**
   - **Save the token!** (you can only see it once)

4. Login to OCIR:
```powershell
# Format: <region-key>.ocir.io
docker login <region>.ocir.io
# Username: <namespace>/<email>
# Password: <auth-token>
```

### Step 4: Build and Push Docker Images

```powershell
# Navigate to project root
cd F:\PourYourMind

# Build and push backend
cd pym_be
docker build -t <region>.ocir.io/<namespace>/pym-backend:v1 .
docker push <region>.ocir.io/<namespace>/pym-backend:v1

# Build and push frontend
cd ../pym_fe
docker build -t <region>.ocir.io/<namespace>/pym-frontend:v1 .
docker push <region>.ocir.io/<namespace>/pym-frontend:v1
```

### Step 5: Create Kubernetes Secrets

```powershell
# Create namespace
kubectl apply -f pym_be/k8s/namespace.yaml

# Create OCI registry secret
kubectl create secret docker-registry oci-registry-secret `
    --namespace=pour-your-mind `
    --docker-server=<region>.ocir.io `
    --docker-username='<namespace>/<email>' `
    --docker-password='<auth-token>' `
    --docker-email='<email>'
```

### Step 6: Update Image References

Edit the deployment files to use your OCI images:

**pym_be/k8s/django-deployment.yaml**:
```yaml
image: <region>.ocir.io/<namespace>/pym-backend:v1
```

**pym_fe/k8s/deployment.yaml**:
```yaml
image: <region>.ocir.io/<namespace>/pym-frontend:v1
```

### Step 7: Deploy Everything

```powershell
# From pym_be/k8s directory
cd pym_be/k8s

# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f django-deployment.yaml

# Wait for backend to be ready
kubectl wait --for=condition=available --timeout=180s deployment/django-app -n pour-your-mind

# Deploy frontend
kubectl apply -f ../../pym_fe/k8s/configmap.yaml
kubectl apply -f ../../pym_fe/k8s/deployment.yaml
```

### Step 8: Get LoadBalancer IPs

```powershell
# Watch services for external IPs
kubectl get services -n pour-your-mind -w

# You'll see output like:
# NAME               TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)
# django-service     LoadBalancer   10.x.x.x       129.x.x.x       80:xxxxx/TCP
# frontend-service   LoadBalancer   10.x.x.x       130.x.x.x       80:xxxxx/TCP
```

### Step 9: Access Your App

- **Frontend**: `http://<frontend-external-ip>`
- **Backend API**: `http://<backend-external-ip>/api/notes/`

## 🔄 Updating Deployments

After getting the LoadBalancer IPs, rebuild with the correct API URL:

```powershell
# Rebuild frontend with backend URL
cd pym_fe
docker build --build-arg VITE_API_URL=http://<backend-ip>/api -t <region>.ocir.io/<namespace>/pym-frontend:v2 .
docker push <region>.ocir.io/<namespace>/pym-frontend:v2

# Update deployment
kubectl set image deployment/frontend-app sveltekit=<region>.ocir.io/<namespace>/pym-frontend:v2 -n pour-your-mind
```

## 📊 Useful Commands

```powershell
# View all resources
kubectl get all -n pour-your-mind

# View pod logs
kubectl logs -l app=django-app -n pour-your-mind
kubectl logs -l app=frontend-app -n pour-your-mind

# Scale deployments
kubectl scale deployment django-app --replicas=3 -n pour-your-mind
kubectl scale deployment frontend-app --replicas=3 -n pour-your-mind

# View pod details
kubectl describe pod <pod-name> -n pour-your-mind

# Execute command in pod
kubectl exec -it <pod-name> -n pour-your-mind -- /bin/bash

# Run Django migrations
kubectl exec -it deployment/django-app -n pour-your-mind -- python manage.py migrate

# Create Django superuser
kubectl exec -it deployment/django-app -n pour-your-mind -- python manage.py createsuperuser
```

## 🧹 Cleanup

To remove all resources:

```powershell
kubectl delete namespace pour-your-mind
```

## 💰 Free Tier Limits

Oracle Cloud Always Free includes:
- **OKE Control Plane**: FREE
- **Ampere A1 Compute**: 4 OCPUs + 24GB RAM total (can split across nodes)
- **Block Storage**: 200GB
- **Load Balancer**: 1 flexible (10 Mbps)
- **Object Storage**: 20GB

## 🔧 Troubleshooting

**Pods not starting?**
```powershell
kubectl describe pod <pod-name> -n pour-your-mind
kubectl logs <pod-name> -n pour-your-mind
```

**Can't pull images?**
- Verify OCI registry secret is created
- Check image path matches exactly
- Ensure auth token is valid

**Database connection errors?**
- Wait for PostgreSQL pod to be ready first
- Check configmap values match secret values

**LoadBalancer pending?**
- OCI LB provisioning can take 2-5 minutes
- Check OCI console for LB status
