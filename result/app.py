from flask import Flask, render_template
import psycopg2

app = Flask(__name__)
db_conn = psycopg2.connect("dbname=voting_db user=postgres password=password host=db")
cursor = db_conn.cursor()

@app.route('/results')
def results():
    cursor.execute("SELECT vote_option, count FROM votes;")
    results = {row[0]: row[1] for row in cursor.fetchall()}
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
