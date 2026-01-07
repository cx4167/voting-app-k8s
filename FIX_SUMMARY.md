# Problem & Solution Summary

## 🔴 Issue #1: Docker Build Context
Docker Compose was failing with error:
```
failed to compute cache key: failed to calculate checksum of ref: "/requirements.txt": not found
```

### Root Cause
The `docker-compose.yml` files had incorrect build contexts.

### Solution
Changed build context to point to service directories instead of root.

---

## 🔴 Issue #2: SQLite in requirements.txt
Error during build:
```
ERROR: Could not find a version that satisfies the requirement sqlite3
```

### Root Cause
`sqlite3` is a built-in Python module and cannot be installed via pip.

### Solution
Removed `sqlite3` from `vote/requirements.txt`.

---

## 🔴 Issue #3: PostgreSQL Password Mismatch
Error during runtime:
```
psycopg2.OperationalError: FATAL: password authentication failed for user "postgres"
```

### Root Cause
- `result/app.py` had hardcoded password: `password`
- `worker/worker.py` had hardcoded password: `password`
- `docker-compose.prod.yml` set password to: `voting-password`
- **They didn't match!**

### Solution
Updated both files to use environment variables:

**result/app.py:**
```python
db_host = os.environ.get('POSTGRES_HOST', 'db')
db_user = os.environ.get('POSTGRES_USER', 'postgres')
db_password = os.environ.get('POSTGRES_PASSWORD', 'password')
db_name = os.environ.get('POSTGRES_DB', 'voting_db')
db_conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host}")
```

**worker/worker.py:**
Same approach - reads from environment variables.

---

## 🔴 Issue #4: Jenkins Pipeline Namespace Conflicts
Error during Jenkins deployment:
```
the namespace from the provided object "voting-app-prod" does not match the namespace "voting-app-dev". 
You must pass '--namespace=voting-app-prod' to perform this operation.
```

### Root Cause
The Kubernetes manifests had **hardcoded namespaces**:
- `k8s-yaml/configmap-prod.yaml` → `namespace: voting-app-prod`
- `k8s-yaml/db-statefulset-prod.yaml` → `namespace: voting-app-prod`
- `k8s-yaml/vote-deployment-prod.yaml` → `namespace: voting-app-prod`

The Jenkins pipeline was trying to deploy these manifests to `voting-app-dev` namespace using `-n voting-app-dev` flag, which conflicts with the hardcoded namespace.

### Solution
Removed **all hardcoded namespace declarations** from Kubernetes manifests.

**Files Updated:**
- ✅ `configmap-prod.yaml` - Removed from ConfigMap & Secret
- ✅ `db-statefulset-prod.yaml` - Removed from StatefulSet & Service
- ✅ `vote-deployment-prod.yaml` - Removed from Deployment & Service

---

## 🔴 Issue #5: Conflicting Kubernetes Service Definitions ⭐ NEW
Error during deployment:
```
The Service "db" is invalid: spec.clusterIPs[0]: Invalid value: []string{"None"}: may not change once set
```

### Root Cause
Two conflicting database definitions in the manifest files:

1. **db-deployment.yaml** (Deployment) - Regular ClusterIP Service
2. **db-statefulset-prod.yaml** (StatefulSet) - Headless Service (clusterIP: None)

Both tried to create a Service named `db`. Kubernetes won't let you change the clusterIP after it's set, so they conflicted.

### Solution
Removed the old `db-deployment.yaml` and kept only `db-statefulset-prod.yaml`:
- ✅ Backed up `db-deployment.yaml` → `db-deployment.yaml.bak`
- ✅ Keep only the production-ready StatefulSet definition
- ✅ StatefulSet provides better persistence and ordering guarantees

---

## ✅ Now Ready to Run

### Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up --build
```
✅ Vote service works
✅ Result service connects to database
✅ Worker processes votes

### Jenkins Pipeline
```bash
# Jenkins will automatically:
# 1. Build Docker images
# 2. Push to Docker Hub
# 3. Update manifests with new image tags
# 4. Deploy to voting-app-dev namespace
# 5. Wait for approval
# 6. Deploy to voting-app-prod namespace
```

### Manual Kubernetes
```bash
# Deploy to DEV
kubectl create namespace voting-app-dev
kubectl apply -f k8s-yaml/ -n voting-app-dev

# Deploy to PROD
kubectl create namespace voting-app-prod
kubectl apply -f k8s-yaml/ -n voting-app-prod
```






