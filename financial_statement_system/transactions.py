from datetime import datetime
import sqlite3
from database import get_db_connection

def add_transaction(user_id, account_id, category_id, amount, description, transaction_type, date=None):
    conn = get_db_connection()
    try:
        # Convert empty category_id to NULL
        category_id = category_id if category_id else None
        
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO transactions (user_id, account_id, category_id, amount, description, date, type)
        VALUES (?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP), ?)
        ''', (user_id, account_id, category_id, float(amount), description, date, transaction_type))
        
        # Update account balance
        if transaction_type == 'income':
            cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ? AND user_id = ?',
                         (float(amount), account_id, user_id))
        else:
            cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ? AND user_id = ?',
                         (float(amount), account_id, user_id))
        
        conn.commit()
        return True, "Transaction added successfully"
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, f"Database error: {str(e)}"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

# ... (keep other functions but add FK checks where needed)

def get_transactions(user_id, limit=None, start_date=None, end_date=None):
    conn = get_db_connection()
    query = '''
    SELECT t.id, t.amount, t.description, t.date, t.type, 
           a.name as account_name, c.name as category_name
    FROM transactions t
    LEFT JOIN accounts a ON t.account_id = a.id
    LEFT JOIN categories c ON t.category_id = c.id
    WHERE t.user_id = ?
    '''
    params = [user_id]
    
    if start_date:
        query += ' AND t.date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND t.date <= ?'
        params.append(end_date)
    
    query += ' ORDER BY t.date DESC'
    
    if limit:
        query += ' LIMIT ?'
        params.append(limit)
    
    transactions = conn.execute(query, params).fetchall()
    conn.close()
    return transactions

def delete_transaction(user_id, transaction_id):
    conn = get_db_connection()
    try:
        # First get the transaction details
        transaction = conn.execute('''
        SELECT account_id, amount, type FROM transactions 
        WHERE id = ? AND user_id = ?
        ''', (transaction_id, user_id)).fetchone()
        
        if not transaction:
            return False, "Transaction not found"
        
        # Delete the transaction
        conn.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', 
                    (transaction_id, user_id))
        
        # Reverse the account balance change
        if transaction['type'] == 'income':
            conn.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', 
                         (transaction['amount'], transaction['account_id']))
        else:  # expense
            conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', 
                         (transaction['amount'], transaction['account_id']))
        
        conn.commit()
        return True, "Transaction deleted successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_accounts(user_id):
    conn = get_db_connection()
    accounts = conn.execute('SELECT id, name, type, balance FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return accounts

def get_categories(user_id, type_=None):
    conn = get_db_connection()
    query = 'SELECT id, name, type FROM categories WHERE user_id = ?'
    params = [user_id]
    
    if type_:
        query += ' AND type = ?'
        params.append(type_)
    
    categories = conn.execute(query, params).fetchall()
    conn.close()
    return categories