import time
import redis
import psycopg2

redis_conn = redis.Redis(host='redis')
db_conn = psycopg2.connect("dbname=voting_db user=postgres password=password host=db")
cursor = db_conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS votes (vote_option VARCHAR(10) PRIMARY KEY, count INT);")
cursor.execute("INSERT INTO votes (vote_option, count) VALUES (%s, %s) ON CONFLICT (vote_option) DO NOTHING;", ('cats', 0))
cursor.execute("INSERT INTO votes (vote_option, count) VALUES (%s, %s) ON CONFLICT (vote_option) DO NOTHING;", ('dogs', 0))
db_conn.commit()

while True:
    vote = redis_conn.blpop('votes', timeout=10)
    if vote:
        vote_option = vote[1].decode('utf-8')
        cursor.execute("UPDATE votes SET count = count + 1 WHERE vote_option = %s;", (vote_option,))
        db_conn.commit()
        print(f"Processed vote for: {vote_option}")
    time.sleep(1)
