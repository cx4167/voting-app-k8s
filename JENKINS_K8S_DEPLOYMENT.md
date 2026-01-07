# Jenkins + Kubernetes Deployment Guide

## 📋 Overview

Your voting app can be deployed via two methods:
1. **Jenkins CI/CD Pipeline** - Automated builds, tests, and deployments
2. **Kubernetes** - Container orchestration and scaling

This guide covers both approaches.

---

## 🔧 Prerequisites

### For Jenkins
- Jenkins server installed and running
- Docker CLI installed on Jenkins agent
- Docker Hub account with credentials configured
- kubectl installed on Jenkins agent
- Kubeconfig file configured

### For Kubernetes
- Kubernetes cluster (local minikube, EKS, AKS, GKE, etc.)
- kubectl CLI installed
- Docker images available (Docker Hub or private registry)
- Persistent storage configured (for database)

---

## 📦 Jenkins Deployment Pipeline

### 1. Set Up Jenkins Credentials

Go to **Jenkins → Manage Credentials → Global**:

```
Credential Type: Username with password
ID: docker-hub-credentials
Username: your-docker-hub-username
Password: your-docker-hub-token
```

### 2. Create a New Pipeline Job

1. Click **New Item**
2. Enter job name: `voting-app-deploy`
3. Select **Pipeline**
4. Click **OK**

### 3. Configure Pipeline

In **Pipeline** section, select:
- **Pipeline script from SCM**
- **SCM**: Git
- **Repository URL**: Your GitHub repo
- **Branch Specifier**: `*/main` (or your default branch)
- **Script Path**: `Jenkinsfile`

### 4. Jenkinsfile Overview

Your `Jenkinsfile` automatically:

✅ **Checkout Code** - Pulls latest from GitHub
✅ **Build Images** - Creates Docker images for vote, worker, result
✅ **Push to Registry** - Pushes to Docker Hub (denish952 namespace)
✅ **Update Manifests** - Updates Kubernetes YAML files with new image tags
✅ **Deploy to DEV** - Deploys to development namespace
✅ **Manual Approval** - Requires approval before production
✅ **Deploy to PROD** - Deploys to production namespace

### 5. Run the Pipeline

1. Go to your job: `voting-app-deploy`
2. Click **Build Now**
3. Monitor progress in **Build History**
4. When prompted, click **Deploy** to approve production deployment

### 6. Monitor Pipeline

```bash
# View all namespaces
kubectl get namespaces

# View dev deployment
kubectl get all -n voting-app-dev

# View prod deployment
kubectl get all -n voting-app

# View logs
kubectl logs -n voting-app-dev deployment/vote
kubectl logs -n voting-app deployment/vote
```

---

## ☸️ Kubernetes Manual Deployment

### Option 1: Direct kubectl Apply

#### Step 1: Create Namespace
```bash
kubectl create namespace voting-app-prod
```

#### Step 2: Configure Secrets & ConfigMaps
```bash
# Edit the file first with your actual values
nano k8s-yaml/configmap-prod.yaml

# Apply configuration
kubectl apply -f k8s-yaml/configmap-prod.yaml -n voting-app-prod
```

#### Step 3: Create Storage
```bash
kubectl apply -f k8s-yaml/pv-pvc.yaml -n voting-app-prod
```

#### Step 4: Deploy Database
```bash
kubectl apply -f k8s-yaml/db-statefulset-prod.yaml -n voting-app-prod
kubectl wait --for=condition=ready pod -l app=postgres -n voting-app-prod --timeout=300s
```

#### Step 5: Deploy Redis
```bash
kubectl apply -f k8s-yaml/redis-deployment.yaml -n voting-app-prod
kubectl wait --for=condition=ready pod -l app=redis -n voting-app-prod --timeout=300s
```

#### Step 6: Deploy Vote Service
```bash
kubectl apply -f k8s-yaml/vote-deployment-prod.yaml -n voting-app-prod
```

#### Step 7: Deploy Worker
```bash
kubectl apply -f k8s-yaml/worker-deployment.yaml -n voting-app-prod
```

#### Step 8: Deploy Results
```bash
kubectl apply -f k8s-yaml/result-deployment.yaml -n voting-app-prod
```

### Option 2: Deploy All at Once
```bash
kubectl create namespace voting-app-prod
kubectl apply -f k8s-yaml/ -n voting-app-prod
kubectl get all -n voting-app-prod
```

---

## 🌐 Access Your Application

### Kubernetes Ingress (Recommended)
```bash
# Get service IP/hostname
kubectl get svc -n voting-app-prod

# Access via NodePort or LoadBalancer
kubectl port-forward -n voting-app-prod svc/vote-service 5000:80
kubectl port-forward -n voting-app-prod svc/result-service 5001:80
```

### Local Access
- **Vote App**: http://localhost:5000/login
- **Results**: http://localhost:5001/results

### Default Credentials
- Username: `admin`
- Password: `admin123`

---

## 🔄 Update Deployment (Rolling Update)

### Via Jenkins
1. Push code to GitHub
2. Jenkins automatically triggers pipeline
3. New images built and pushed
4. Kubernetes automatically rolls out new version

### Via kubectl
```bash
# Update image
kubectl set image deployment/vote \
  vote=denish952/voting-app-vote:v2.0 \
  -n voting-app-prod

# Watch rollout
kubectl rollout status deployment/vote -n voting-app-prod

# Rollback if needed
kubectl rollout undo deployment/vote -n voting-app-prod
```

---

## 📊 Monitoring & Debugging

### View Pod Status
```bash
kubectl get pods -n voting-app-prod
kubectl get pods -n voting-app-prod -w  # Watch mode
```

### View Logs
```bash
# Vote service
kubectl logs -n voting-app-prod deployment/vote --tail=50
kubectl logs -n voting-app-prod deployment/vote -f  # Follow

# Worker service
kubectl logs -n voting-app-prod deployment/worker --tail=50

# Results service
kubectl logs -n voting-app-prod deployment/result --tail=50
```

### Describe Resources
```bash
kubectl describe pod <pod-name> -n voting-app-prod
kubectl describe svc vote-service -n voting-app-prod
kubectl describe statefulset postgres -n voting-app-prod
```

### Execute Commands in Pod
```bash
# Connect to PostgreSQL
kubectl exec -it postgres-0 -n voting-app-prod -- psql -U postgres -d voting_db

# Check vote app
kubectl exec -it <vote-pod> -n voting-app-prod -- curl http://localhost:80/login
```

---

## 🔐 Security Best Practices

### 1. Update Secrets
```bash
# Generate new passwords
python3 -c "import secrets; print(secrets.token_urlsafe(16))"

# Update in configmap-prod.yaml
POSTGRES_PASSWORD: "your-new-secure-password"
SECRET_KEY: "your-new-secret-key"
```

### 2. HTTPS/TLS Setup
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create certificate
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: voting-app-cert
  namespace: voting-app-prod
spec:
  secretName: voting-app-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
EOF
```

### 3. Network Policies
```bash
# Restrict traffic
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: voting-app-network-policy
  namespace: voting-app-prod
spec:
  podSelector:
    matchLabels:
      app: vote
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: voting-app-prod
EOF
```

### 4. Pod Security Policy
```bash
# Enforce security standards
kubectl label namespace voting-app-prod pod-security.kubernetes.io/enforce=baseline
```

---

## 📈 Scaling & Performance

### Scale Vote Service
```bash
# Scale to 5 replicas
kubectl scale deployment vote --replicas=5 -n voting-app-prod

# Auto-scaling
kubectl autoscale deployment vote --min=3 --max=10 --cpu-percent=70 -n voting-app-prod
```

### View Resource Usage
```bash
kubectl top nodes
kubectl top pod -n voting-app-prod
```

### Resource Limits
Check current limits in `vote-deployment-prod.yaml`:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

---

## ✅ Deployment Checklist

- [ ] Jenkins credentials configured (Docker Hub)
- [ ] Kubeconfig file accessible to Jenkins
- [ ] Kubernetes cluster running and accessible
- [ ] Namespace created
- [ ] Secrets/ConfigMaps applied
- [ ] Persistent storage configured
- [ ] Database StatefulSet deployed
- [ ] Redis deployment deployed
- [ ] Vote service deployed and accessible
- [ ] Worker service deployed
- [ ] Results service deployed and accessible
- [ ] Test votes submitted and verified
- [ ] HTTPS/TLS configured
- [ ] Monitoring and logging enabled
- [ ] Backup strategy in place

---

## 🆘 Troubleshooting

### Pipeline Fails at Docker Build
```bash
# Check Jenkins Docker permissions
docker ps  # Run on Jenkins agent

# Grant Docker access to Jenkins user
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Kubernetes Pods Not Starting
```bash
# Check events
kubectl describe pod <pod-name> -n voting-app-prod

# Check resource availability
kubectl describe nodes

# Check image pull errors
kubectl logs <pod-name> -n voting-app-prod
```

### Database Connection Failures
```bash
# Check PostgreSQL is running
kubectl get pod postgres-0 -n voting-app-prod

# Test connection
kubectl exec -it postgres-0 -n voting-app-prod -- psql -U postgres
```

### Redis Connection Issues
```bash
# Check Redis pod
kubectl get pod -l app=redis -n voting-app-prod

# Test Redis connection
kubectl exec -it <redis-pod> -n voting-app-prod -- redis-cli PING
```

---

## 📚 Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

