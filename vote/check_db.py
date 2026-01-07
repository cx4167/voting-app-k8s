#!/usr/bin/env python3
"""
Script to check database status and initialize if needed.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = os.environ.get('DATABASE_PATH', 'users.db')

def check_and_init():
    """Check database and initialize if needed."""
    print(f"📁 Database path: {DATABASE}")
    
    if os.path.exists(DATABASE):
        print("✅ Database file exists")
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Tables: {tables}")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 Total users: {user_count}")
        
        if user_count == 0:
            print("⚠️  No users found! Creating default users...")
            add_default_users(db)
        
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        print(f"📋 Users in database:")
        for user_id, username in users:
            print(f"   - {username} (ID: {user_id})")
        
        db.close()
    else:
        print("❌ Database file does not exist! Creating new database...")
        create_db()
        add_default_users()

def create_db():
    """Create database and users table."""
    db = sqlite3.connect(DATABASE)
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
    db.close()
    print("✅ Database created!")

def add_default_users(db=None):
    """Add default test users."""
    if db is None:
        db = sqlite3.connect(DATABASE)
        close_db = True
    else:
        close_db = False
    
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
            db.commit()
            print(f"✅ User '{username}' created!")
        except sqlite3.IntegrityError:
            print(f"⚠️  User '{username}' already exists!")
    
    if close_db:
        db.close()

if __name__ == '__main__':
    check_and_init()
