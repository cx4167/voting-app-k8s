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

## 🔴 Issue #3: PostgreSQL Password Mismatch ⭐ NEW
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

## ✅ Now Ready to Run

```bash
docker-compose -f docker-compose.prod.yml up --build
```

The vote service will work ✅
The result service will connect to database ✅
The worker will process votes ✅


