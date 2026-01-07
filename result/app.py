from flask import Flask, render_template
import psycopg2
import os
import time

app = Flask(__name__)

# Get database connection parameters from environment variables
db_host = os.environ.get('POSTGRES_HOST', 'db')
db_user = os.environ.get('POSTGRES_USER', 'postgres')
db_password = os.environ.get('POSTGRES_PASSWORD', 'password')
db_name = os.environ.get('POSTGRES_DB', 'voting_db')

db_conn = None
cursor = None

def get_db_connection():
    """Get or create database connection with retries."""
    global db_conn, cursor
    
    if db_conn is None:
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                db_conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host}")
                cursor = db_conn.cursor()
                print("✅ Connected to database")
                return db_conn
            except psycopg2.OperationalError as e:
                retry_count += 1
                print(f"⚠️ Database connection attempt {retry_count}/{max_retries} failed: {e}")
                if retry_count < max_retries:
                    time.sleep(2)
                else:
                    print("❌ Failed to connect to database after retries")
                    raise
    
    return db_conn

@app.route('/results')
def results():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT vote_option, count FROM votes;")
        results = {row[0]: row[1] for row in cursor.fetchall()}
        return render_template('results.html', results=results)
    except Exception as e:
        print(f"Error fetching results: {e}")
        return render_template('results.html', results={"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
