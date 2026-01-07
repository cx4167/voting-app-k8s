import time
import redis
import psycopg2
import os
import sys

redis_conn = redis.Redis(host=os.environ.get('REDIS_HOST', 'redis'))

# Get database connection parameters from environment variables
db_host = os.environ.get('POSTGRES_HOST', 'db')
db_user = os.environ.get('POSTGRES_USER', 'postgres')
db_password = os.environ.get('POSTGRES_PASSWORD', 'password')
db_name = os.environ.get('POSTGRES_DB', 'voting_db')

db_conn = None
cursor = None

def init_db():
    """Initialize database connection and tables with retries."""
    global db_conn, cursor
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"🔄 Attempting to connect to database (attempt {retry_count + 1}/{max_retries})...")
            db_conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host}")
            cursor = db_conn.cursor()
            
            # Create table if doesn't exist
            cursor.execute("CREATE TABLE IF NOT EXISTS votes (vote_option VARCHAR(10) PRIMARY KEY, count INT);")
            cursor.execute("INSERT INTO votes (vote_option, count) VALUES (%s, %s) ON CONFLICT (vote_option) DO NOTHING;", ('cats', 0))
            cursor.execute("INSERT INTO votes (vote_option, count) VALUES (%s, %s) ON CONFLICT (vote_option) DO NOTHING;", ('dogs', 0))
            db_conn.commit()
            
            print("✅ Database initialized successfully!")
            return True
            
        except psycopg2.OperationalError as e:
            retry_count += 1
            print(f"⚠️ Connection failed: {e}")
            if retry_count < max_retries:
                print(f"⏳ Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print("❌ Failed to connect after all retries!")
                return False

# Initialize database on startup
if not init_db():
    print("❌ Worker cannot start without database!")
    sys.exit(1)

print("🚀 Worker started, listening for votes...")

while True:
    try:
        vote = redis_conn.blpop('votes', timeout=10)
        if vote:
            vote_option = vote[1].decode('utf-8')
            cursor.execute("UPDATE votes SET count = count + 1 WHERE vote_option = %s;", (vote_option,))
            db_conn.commit()
            print(f"✅ Processed vote for: {vote_option}")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Error processing vote: {e}")
        time.sleep(2)

