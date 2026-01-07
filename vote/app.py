import os
import sqlite3
import socket
import secrets
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from redis import Redis
from functools import wraps

app = Flask(__name__)
# Use environment variable for production secret key
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP in dev/k8s
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_NAME'] = 'voting_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis = Redis(host=redis_host, port=redis_port, decode_responses=True)

# Initialize SQLite database for users
DATABASE = os.environ.get('DATABASE_PATH', '/app/data/users.db')

def ensure_db_dir():
    """Ensure database directory exists."""
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database with tables and default users."""
    ensure_db_dir()
    
    # Only create if doesn't exist
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("📊 Creating users table...")
        db.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                has_voted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
        
        # Add default users
        default_users = [
            ('admin', 'admin123'),
            ('bob', 'secure456'),
            ('charlie', 'voting789'),
            ('diana', 'choices123'),
        ]
        
        for username, password in default_users:
            try:
                hashed_password = generate_password_hash(password)
                db.execute(
                    'INSERT INTO users (username, password, has_voted) VALUES (?, ?, 0)',
                    (username, hashed_password)
                )
                print(f"✅ User '{username}' created")
            except sqlite3.IntegrityError:
                pass
        
        db.commit()
        print("✅ Database initialized with default users")
    
    db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    """Initialize database before first request."""
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        error = None
        
        # Validate input
        if not username or not password:
            error = 'Username and password are required.'
        
        if error is None:
            try:
                db = get_db()
                user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                db.close()
                
                if user is None:
                    error = 'Invalid credentials.'
                elif not check_password_hash(user['password'], password):
                    error = 'Invalid credentials.'
            except Exception as e:
                print(f"Login error: {str(e)}")
                error = f'Database error: {str(e)}'
        
        if error is None:
            session.clear()
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            print(f"✅ Login successful for user: {username}, user_id: {user['id']}")
            print(f"   Session data: user_id={session.get('user_id')}, username={session.get('username')}")
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
        
        vote_data = request.form.get('vote', '').strip()
        if vote_data not in ['cats', 'dogs']:
            db.close()
            error = 'Invalid vote option.'
            return render_template('index.html', error=error, hostname=socket.gethostname())
        
        try:
            redis.rpush('votes', vote_data)
            
            # Mark user as voted
            db.execute('UPDATE users SET has_voted = 1 WHERE id = ?', (user_id,))
            db.commit()
            db.close()
            
            return redirect(url_for('thank_you'))
        except Exception as e:
            db.close()
            error = 'An error occurred while processing your vote. Please try again.'
            return render_template('index.html', error=error, hostname=socket.gethostname())
    
    return render_template('index.html', hostname=socket.gethostname())

@app.route('/thanks')
@login_required
def thank_you():
    return render_template('thanks.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('login.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('login.html', error='Internal server error'), 500

if __name__ == "__main__":
    init_db()
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host="0.0.0.0", port=80, debug=debug_mode)
