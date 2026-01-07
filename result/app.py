from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

# Get database connection parameters from environment variables
db_host = os.environ.get('POSTGRES_HOST', 'db')
db_user = os.environ.get('POSTGRES_USER', 'postgres')
db_password = os.environ.get('POSTGRES_PASSWORD', 'password')
db_name = os.environ.get('POSTGRES_DB', 'voting_db')

db_conn = psycopg2.connect(f"dbname={db_name} user={db_user} password={db_password} host={db_host}")
cursor = db_conn.cursor()

@app.route('/results')
def results():
    cursor.execute("SELECT vote_option, count FROM votes;")
    results = {row[0]: row[1] for row in cursor.fetchall()}
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
