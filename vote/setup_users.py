#!/usr/bin/env python3
"""
Script to initialize the user database and add pre-registered users.
Run this script before starting the application.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = 'users.db'

def init_db():
    """Initialize the database and create users table."""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    db = sqlite3.connect(DATABASE)
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
    print("✅ Database initialized!")

def add_user(username, password):
    """Add a user to the database."""
    db = sqlite3.connect(DATABASE)
    try:
        hashed_password = generate_password_hash(password)
        db.execute(
            'INSERT INTO users (username, password, has_voted) VALUES (?, ?, 0)',
            (username, hashed_password)
        )
        db.commit()
        print(f"✅ User '{username}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"❌ User '{username}' already exists!")
    finally:
        db.close()

def list_users():
    """List all registered users."""
    db = sqlite3.connect(DATABASE)
    users = db.execute('SELECT id, username, has_voted FROM users').fetchall()
    db.close()
    
    if users:
        print("\n📋 Registered Users:")
        print("-" * 50)
        for user_id, username, has_voted in users:
            status = "✓ Voted" if has_voted else "⊘ Not Voted"
            print(f"ID: {user_id:2d} | Username: {username:20s} | {status}")
        print("-" * 50)
    else:
        print("\n❌ No users registered yet!")

if __name__ == '__main__':
    print("🗳️  Voting App - User Database Setup\n")
    
    # Initialize database
    init_db()
    
    # Add some pre-registered users
    print("\n➕ Adding pre-registered users...\n")
    add_user('admin', 'admin123')
    add_user('bob', 'secure456')
    add_user('charlie', 'voting789')
    add_user('diana', 'choices123')
    
    # List all users
    list_users()
    
    print("\n✨ Setup complete! You can now run the application.")
    print("📝 Login with any of the registered usernames and their passwords.")
