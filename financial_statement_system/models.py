import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL,  -- 'asset', 'liability', 'equity'
        balance REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # Categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        type TEXT NOT NULL,  -- 'income' or 'expense'
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')
    
    # Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        account_id INTEGER NOT NULL,
        category_id INTEGER,
        amount REAL NOT NULL,
        description TEXT,
        date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        type TEXT NOT NULL,  -- 'income' or 'expense'
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (account_id) REFERENCES accounts (id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
    )
    ''')
    
    # Create default categories if they don't exist
    default_categories = [
        ('Salary', 'income'),
        ('Investment', 'income'),
        ('Rent', 'expense'),
        ('Food', 'expense'),
        ('Transportation', 'expense'),
        ('Utilities', 'expense'),
        ('Entertainment', 'expense')
    ]
    
    # Insert default categories for all users (user_id=0 represents system defaults)
    cursor.execute('SELECT 1 FROM categories WHERE user_id = 0 LIMIT 1')
    if not cursor.fetchone():
        for name, type_ in default_categories:
            cursor.execute('INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)', 
                         (0, name, type_))
    
    conn.commit()
    conn.close()

class User:
    def __init__(self, id, username, password_hash=None, email=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

if __name__ == "__main__":
    init_db()
