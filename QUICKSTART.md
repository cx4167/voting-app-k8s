# Quick Start Guide - Production Deployment

## Prerequisites
- Docker Desktop installed and running
- Docker Compose installed
- Git repository cloned locally

## Running Locally with Docker Compose

### 1. Start all services
```bash
docker-compose -f docker-compose.prod.yml up --build
```

### 2. Access the applications
- **Voting App**: http://localhost:5000
- **Results Dashboard**: http://localhost:5001

### 3. Default Login Credentials
Run the setup script first to create users:
```bash
docker-compose -f docker-compose.prod.yml exec vote python setup_users.py
```

Or use pre-configured users:
- Username: `admin` | Password: `admin123`
- Username: `bob` | Password: `secure456`
- Username: `charlie` | Password: `voting789`
- Username: `diana` | Password: `choices123`

### 4. Stop all services
```bash
docker-compose -f docker-compose.prod.yml down
```

### 5. Clean up volumes (fresh start)
```bash
docker-compose -f docker-compose.prod.yml down -v
```

---

## Troubleshooting

### Port already in use
If ports 5000, 5001, 5432, or 6379 are already in use, modify the port mappings in `docker-compose.prod.yml`:

```yaml
ports:
  - "5000:80"  # Change 5000 to any available port
```

### Build fails
Clear Docker cache and rebuild:
```bash
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a
docker-compose -f docker-compose.prod.yml up --build
```

### View logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f vote
docker-compose -f docker-compose.prod.yml logs -f worker
docker-compose -f docker-compose.prod.yml logs -f result
```

### Container health check
```bash
docker-compose -f docker-compose.prod.yml ps
```

---

## Services Overview

| Service | Port | Purpose |
|---------|------|---------|
| **vote** | 5000 | Frontend voting application |
| **result** | 5001 | Results dashboard |
| **redis** | 6379 | Message queue |
| **db** | 5432 | PostgreSQL database |
| **worker** | N/A | Background vote processor |

---

## Environment Variables

All environment variables are configured in `docker-compose.prod.yml`. For production deployment, update:

```yaml
FLASK_ENV: production
SECRET_KEY: your-strong-secret-key
POSTGRES_PASSWORD: your-strong-password
```

---

## Next Steps

### Deploy to Kubernetes
See `PRODUCTION_DEPLOYMENT.md` for detailed Kubernetes deployment instructions.

### Monitor & Logging
- Set up Prometheus + Grafana for monitoring
- Configure ELK stack for centralized logging
- Enable audit logging in Kubernetes

### Security Hardening
- Change all default passwords
- Set up HTTPS/TLS certificates
- Configure network policies
- Enable Pod Security Policies
