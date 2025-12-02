# Pour Your Mind - Kubernetes Deployment

This directory contains all the Kubernetes manifests needed to deploy the "Pour Your Mind" application to a Kubernetes cluster.

## Prerequisites

1. **Kubernetes cluster** (local or cloud)
2. **kubectl** configured to connect to your cluster
3. **Docker image** built and pushed to a registry

## Architecture

The deployment includes:

- **PostgreSQL Database** - Persistent storage for the application
- **Django Application** - Main API server with 3 replicas
- **Nginx** - Reverse proxy and load balancer
- **Ingress** - External access to the application
- **HPA** - Horizontal Pod Autoscaler for automatic scaling

## Quick Start

### 1. Build and Push Docker Image

First, you need to build and push your Docker image to a registry:

```bash
# Build the image
docker build -t pour-your-mind:latest .

# Tag for your registry (replace with your registry)
docker tag pour-your-mind:latest your-registry.com/pour-your-mind:latest

# Push to registry
docker push your-registry.com/pour-your-mind:latest
```

### 2. Update Image Reference

Edit `django-deployment.yaml` and update the image reference:

```yaml
image: your-registry.com/pour-your-mind:latest
```

### 3. Deploy to Kubernetes

```bash
# Deploy everything
./deploy.sh

# Or deploy manually
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f nginx-configmap.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f django-deployment.yaml
kubectl apply -f nginx-deployment.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
```

### 4. Access the Application

```bash
# Port forward to access locally
kubectl port-forward -n pour-your-mind service/nginx-service 8080:80

# Open http://localhost:8080 in your browser
```

## Configuration

### Environment Variables

Update `configmap.yaml` and `secret.yaml` with your configuration:

```yaml
# configmap.yaml
data:
  DEBUG: "0"
  POSTGRES_DB: "pym_db"
  POSTGRES_USER: "pym_user"
  DB_HOST: "postgres-service"
  DB_PORT: "5432"

# secret.yaml
data:
  POSTGRES_PASSWORD: <base64-encoded-password>
  SECRET_KEY: <base64-encoded-secret-key>
```

### Storage

The PostgreSQL database uses a PersistentVolumeClaim. Update `postgres-pvc.yaml`:

```yaml
spec:
  storageClassName: your-storage-class # Change this
  resources:
    requests:
      storage: 10Gi # Adjust size as needed
```

### Ingress

Update `ingress.yaml` with your domain:

```yaml
spec:
  rules:
    - host: your-domain.com # Change this
```

## Monitoring and Management

### Check Deployment Status

```bash
# Check all resources
kubectl get all -n pour-your-mind

# Check pods
kubectl get pods -n pour-your-mind

# Check services
kubectl get services -n pour-your-mind

# Check ingress
kubectl get ingress -n pour-your-mind
```

### View Logs

```bash
# Django application logs
kubectl logs -n pour-your-mind -l app=django-app

# Nginx logs
kubectl logs -n pour-your-mind -l app=nginx

# PostgreSQL logs
kubectl logs -n pour-your-mind -l app=postgres
```

### Scale Application

```bash
# Scale Django replicas
kubectl scale deployment django-app -n pour-your-mind --replicas=5

# Check HPA status
kubectl get hpa -n pour-your-mind
```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**

   - Ensure your image is pushed to the registry
   - Check image reference in `django-deployment.yaml`

2. **Database Connection Issues**

   - Verify PostgreSQL is running: `kubectl get pods -l app=postgres -n pour-your-mind`
   - Check database credentials in secrets

3. **Storage Issues**
   - Verify storage class exists: `kubectl get storageclass`
   - Check PVC status: `kubectl get pvc -n pour-your-mind`

### Debug Commands

```bash
# Describe resources for detailed info
kubectl describe pod <pod-name> -n pour-your-mind
kubectl describe service <service-name> -n pour-your-mind

# Execute commands in pods
kubectl exec -it <pod-name> -n pour-your-mind -- /bin/bash

# Check events
kubectl get events -n pour-your-mind --sort-by='.lastTimestamp'
```

## Cleanup

To remove all resources:

```bash
# Use the cleanup script
./undeploy.sh

# Or manually
kubectl delete namespace pour-your-mind
```

## Production Considerations

1. **Security**

   - Use proper secrets management (e.g., Kubernetes secrets, external secret operators)
   - Enable RBAC
   - Use network policies

2. **Monitoring**

   - Add Prometheus and Grafana for monitoring
   - Set up log aggregation (e.g., ELK stack)

3. **Backup**

   - Set up database backups
   - Use Velero for cluster backups

4. **SSL/TLS**
   - Configure cert-manager for automatic SSL certificates
   - Update ingress with TLS configuration

