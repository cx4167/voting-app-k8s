# Production Deployment Guide

## 🚀 Authentication & Security Updates

### Key Improvements:

#### 1. **Authentication Enhancements**
- ✅ Session security with HTTPS-only cookies (production)
- ✅ HTTPOnly cookie protection against XSS
- ✅ SameSite cookie policy
- ✅ 1-hour session timeout
- ✅ Secure secret key generation from environment variables
- ✅ Input validation and sanitization
- ✅ Generic error messages (no user enumeration)

#### 2. **Dockerfile Improvements**
- ✅ Updated to Python 3.11 (latest stable)
- ✅ Gunicorn WSGI server (4 workers)
- ✅ Non-root user execution
- ✅ Health checks with timeout
- ✅ Persistent volume support
- ✅ Reduced image size with --no-cache-dir

#### 3. **Application Hardening**
- ✅ Error handlers (404, 500)
- ✅ Input validation and sanitization
- ✅ Database error handling
- ✅ Redis connection resilience
- ✅ Environment-based configuration

---

## 🔧 Deployment Steps

### Prerequisites
```bash
# 1. Generate a strong secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# 2. Generate a secure password
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

### Local Testing (Docker Compose)
```bash
# Build and run production setup
docker-compose -f docker-compose.prod.yml up --build

# Access
# - Voting: http://localhost:5000
# - Results: http://localhost:5001

# Clean up
docker-compose -f docker-compose.prod.yml down -v
```

### Kubernetes Deployment

#### Step 1: Create Namespace
```bash
kubectl create namespace voting-app-prod
```

#### Step 2: Update Secrets
```bash
# Edit k8s-yaml/configmap-prod.yaml with your actual values
# 1. Update SECRET_KEY
# 2. Update POSTGRES_PASSWORD
# 3. Update DOCKER_REGISTRY_PASSWORD if using private registry

kubectl apply -f k8s-yaml/configmap-prod.yaml
```

#### Step 3: Create Persistent Storage
```bash
# If using local storage or NFS
kubectl apply -f k8s-yaml/pv-pvc.yaml -n voting-app-prod
```

#### Step 4: Deploy Database
```bash
kubectl apply -f k8s-yaml/db-statefulset-prod.yaml
```

#### Step 5: Deploy Vote Service
```bash
kubectl apply -f k8s-yaml/vote-deployment-prod.yaml
```

#### Step 6: Deploy Redis
```bash
kubectl apply -f k8s-yaml/redis-deployment.yaml -n voting-app-prod
```

#### Step 7: Deploy Worker
```bash
kubectl apply -f k8s-yaml/worker-deployment.yaml -n voting-app-prod
```

#### Step 8: Deploy Results
```bash
kubectl apply -f k8s-yaml/result-deployment.yaml -n voting-app-prod
```

#### Step 9: Verify Deployment
```bash
kubectl get deployments -n voting-app-prod
kubectl get services -n voting-app-prod
kubectl get pods -n voting-app-prod

# Port forward for testing
kubectl port-forward svc/vote-service 5000:80 -n voting-app-prod
```

---

## 🔐 Security Configuration

### Environment Variables Required
```bash
# Production Environment
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_PATH=/app/data/users.db
REDIS_HOST=redis
REDIS_PORT=6379
POSTGRES_HOST=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=voting_db
```

### Security Checklist
- [ ] Changed SECRET_KEY in ConfigMap
- [ ] Changed POSTGRES_PASSWORD in Secret
- [ ] Enabled HTTPS/TLS on load balancer
- [ ] Set up network policies
- [ ] Configured resource limits
- [ ] Enabled audit logging
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configured backup strategy

---

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- **Vote Service**: `GET /login` - Returns 200 if healthy
- **Result Service**: `GET /results` - Returns 200 if healthy
- **Database**: PostgreSQL readiness probe
- **Redis**: PING command

### Logs
```bash
# Check pod logs
kubectl logs -f deployment/vote -n voting-app-prod

# Check all service logs
kubectl logs -f deployment/worker -n voting-app-prod
```

---

## 🔄 Rolling Updates

### Update Application
```bash
# Build new version
docker build -t denish952/voting-app-vote:v2 -f vote/Dockerfile vote/
docker push denish952/voting-app-vote:v2

# Update deployment
kubectl set image deployment/vote vote=denish952/voting-app-vote:v2 -n voting-app-prod

# Monitor rollout
kubectl rollout status deployment/vote -n voting-app-prod
```

---

## 📝 Database Initialization

Initialize users in production:
```bash
# Connect to pod
kubectl exec -it pod/<vote-pod-name> -n voting-app-prod -- /bin/bash

# Run setup script
python3 setup_users.py

# Verify users
sqlite3 /app/data/users.db "SELECT * FROM users;"
```

---

## 🛑 Cleanup

```bash
# Delete entire namespace
kubectl delete namespace voting-app-prod

# Or delete individual resources
kubectl delete -f k8s-yaml/vote-deployment-prod.yaml -n voting-app-prod
```

---

## 🐛 Troubleshooting

### Pod Won't Start
```bash
kubectl describe pod <pod-name> -n voting-app-prod
kubectl logs <pod-name> -n voting-app-prod
```

### Connection Issues
```bash
# Check service discovery
kubectl get svc -n voting-app-prod
kubectl exec -it pod/<pod> -n voting-app-prod -- nslookup redis
```

### Database Issues
```bash
# Check PVC status
kubectl get pvc -n voting-app-prod

# Verify volume mounts
kubectl describe statefulset db -n voting-app-prod
```

---

## 📚 Additional Resources

- Gunicorn Documentation: https://gunicorn.org/
- Flask Security: https://flask.palletsprojects.com/security/
- Kubernetes Best Practices: https://kubernetes.io/docs/concepts/configuration/
