import sqlite3
from models import User

def get_db_connection():
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints
    return conn

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'], 
                   password_hash=user['password_hash'], email=user['email'])
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(id=user['id'], username=user['username'],
                   password_hash=user['password_hash'], email=user['email'])
    return None

def create_user(username, password, email=None):
    conn = get_db_connection()
    try:
        user = User(id=None, username=username, email=email)
        user.set_password(password)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                      (user.username, user.password_hash, user.email))
        user_id = cursor.lastrowid
        
        # Create default accounts
        default_accounts = [
            ('Cash', 'asset'),
            ('Bank Account', 'asset'),
            ('Credit Card', 'liability'),
            ('Loan', 'liability')
        ]
        
        for name, type_ in default_accounts:
            cursor.execute('INSERT INTO accounts (user_id, name, type, balance) VALUES (?, ?, ?, ?)',
                         (user_id, name, type_, 0))
        
        # Copy default categories to user
        cursor.execute('''
        INSERT INTO categories (user_id, name, type) 
        SELECT ?, name, type FROM categories WHERE user_id = 0
        ''', (user_id,))
        
        conn.commit()
        return user_id
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"User creation failed: {str(e)}")
    finally:
        conn.close()