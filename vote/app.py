import os
import sqlite3
import socket
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from redis import Redis
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
redis = Redis(host='redis', port=6379)

# Initialize SQLite database for users
DATABASE = 'users.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    if not os.path.exists(DATABASE):
        db = get_db()
        db.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                has_voted INTEGER DEFAULT 0
            )
        ''')
        db.commit()
        db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user is None:
            error = 'User not found.'
        elif not check_password_hash(user['password'], password):
            error = 'Invalid password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('vote'))
        
        return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def vote():
    if request.method == 'POST':
        user_id = session['user_id']
        db = get_db()
        user = db.execute('SELECT has_voted FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if user['has_voted']:
            db.close()
            error = 'You have already voted!'
            return render_template('index.html', error=error, hostname=socket.gethostname())
        
        vote_data = request.form['vote']
        redis.rpush('votes', vote_data)
        
        # Mark user as voted
        db.execute('UPDATE users SET has_voted = 1 WHERE id = ?', (user_id,))
        db.commit()
        db.close()
        
        return redirect(url_for('thank_you'))
    
    return render_template('index.html', hostname=socket.gethostname())

@app.route('/thanks')
@login_required
def thank_you():
    return render_template('thanks.html')

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=80, debug=True)
