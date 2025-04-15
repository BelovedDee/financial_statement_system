from datetime import datetime, timedelta
from database import get_db_connection

def generate_income_statement(user_id, start_date=None, end_date=None):
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    
    # Get income
    income = conn.execute('''
    SELECT c.name as category, SUM(t.amount) as total
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    WHERE t.user_id = ? AND t.type = 'income' AND t.date BETWEEN ? AND ?
    GROUP BY c.name
    ''', (user_id, start_date, end_date)).fetchall()
    
    total_income = sum(row['total'] for row in income)
    
    # Get expenses
    expenses = conn.execute('''
    SELECT c.name as category, SUM(t.amount) as total
    FROM transactions t
    JOIN categories c ON t.category_id = c.id
    WHERE t.user_id = ? AND t.type = 'expense' AND t.date BETWEEN ? AND ?
    GROUP BY c.name
    ''', (user_id, start_date, end_date)).fetchall()
    
    total_expenses = sum(row['total'] for row in expenses)
    net_income = total_income - total_expenses
    
    conn.close()
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'income': income,
        'total_income': total_income,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'net_income': net_income
    }

def generate_balance_sheet(user_id, as_of_date=None):
    if not as_of_date:
        as_of_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    
    # Get assets
    assets = conn.execute('''
    SELECT name, balance FROM accounts 
    WHERE user_id = ? AND type = 'asset' AND balance != 0
    ''', (user_id,)).fetchall()
    total_assets = sum(row['balance'] for row in assets)
    
    # Get liabilities
    liabilities = conn.execute('''
    SELECT name, balance FROM accounts 
    WHERE user_id = ? AND type = 'liability' AND balance != 0
    ''', (user_id,)).fetchall()
    total_liabilities = sum(row['balance'] for row in liabilities)
    
    # Get equity (starting with retained earnings from net income)
    equity = []
    net_income = generate_income_statement(user_id)['net_income']
    equity.append(('Retained Earnings', net_income))
    
    # Add equity accounts
    equity_accounts = conn.execute('''
    SELECT name, balance FROM accounts 
    WHERE user_id = ? AND type = 'equity' AND balance != 0
    ''', (user_id,)).fetchall()
    equity.extend([(row['name'], row['balance']) for row in equity_accounts])
    
    total_equity = sum(row[1] for row in equity)
    
    # Check balance sheet equation
    balance_check = total_assets - (total_liabilities + total_equity)
    
    conn.close()
    
    return {
        'as_of_date': as_of_date,
        'assets': assets,
        'total_assets': total_assets,
        'liabilities': liabilities,
        'total_liabilities': total_liabilities,
        'equity': equity,
        'total_equity': total_equity,
        'balance_check': balance_check
    }

def generate_cash_flow(user_id, start_date=None, end_date=None):
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    
    # Cash from operating activities (income - expenses)
    operating = conn.execute('''
    SELECT t.type, SUM(t.amount) as total
    FROM transactions t
    WHERE t.user_id = ? AND t.date BETWEEN ? AND ?
    AND t.type IN ('income', 'expense')
    GROUP BY t.type
    ''', (user_id, start_date, end_date)).fetchall()
    
    cash_from_operations = 0
    for row in operating:
        if row['type'] == 'income':
            cash_from_operations += row['total']
        else:
            cash_from_operations -= row['total']
    
    # Cash from investing activities (asset account changes)
    # This would require tracking changes in asset accounts over time
    # Simplified version for this example
    
    # Cash from financing activities (liability/equity account changes)
    # This would require tracking changes in liability/equity accounts over time
    # Simplified version for this example
    
    conn.close()
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'cash_from_operations': cash_from_operations,
        'cash_from_investing': 0,  # Placeholder
        'cash_from_financing': 0,  # Placeholder
        'net_cash_flow': cash_from_operations  # Simplified
    }