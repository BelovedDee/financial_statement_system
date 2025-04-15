from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import create_user
from auth import login_user, logout_user, login_required
from transactions import add_transaction, get_transactions, delete_transaction, get_accounts, get_categories
from reports import generate_income_statement, generate_balance_sheet, generate_cash_flow
from models import init_db

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production!
app.config['DATABASE'] = 'finance.db'

# Initialize database
init_db()

@app.route('/')
@login_required
def dashboard():
    user_id = session['user_id']
    
    # Get recent transactions
    transactions = get_transactions(user_id, limit=5)
    
    # Get account balances
    accounts = get_accounts(user_id)
    
    # Generate quick financial overview
    income_statement = generate_income_statement(user_id)
    
    return render_template('dashboard.html', 
                         transactions=transactions,
                         accounts=accounts,
                         income_statement=income_statement)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('register'))
        
        user_id = create_user(username, password, email)
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = login_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/transactions')
@login_required
def view_transactions():
    user_id = session['user_id']
    transactions = get_transactions(user_id)
    return render_template('transactions.html', transactions=transactions)

@app.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction_view():
    user_id = session['user_id']
    
    if request.method == 'POST':
        account_id = request.form['account_id']
        category_id = request.form.get('category_id')
        amount = request.form['amount']
        description = request.form.get('description', '')
        transaction_type = request.form['type']
        
        success, message = add_transaction(
            user_id, account_id, category_id, amount, 
            description, transaction_type
        )
        
        if success:
            flash('Transaction added successfully', 'success')
            return redirect(url_for('view_transactions'))
        else:
            flash(f'Error: {message}', 'danger')
    
    accounts = get_accounts(user_id)
    income_categories = get_categories(user_id, 'income')
    expense_categories = get_categories(user_id, 'expense')
    
    return render_template('add_transaction.html',
                         accounts=accounts,
                         income_categories=income_categories,
                         expense_categories=expense_categories)

@app.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction_view(transaction_id):
    user_id = session['user_id']
    success, message = delete_transaction(user_id, transaction_id)
    
    if success:
        flash('Transaction deleted successfully', 'success')
    else:
        flash(f'Error: {message}', 'danger')
    
    return redirect(url_for('view_transactions'))

@app.route('/reports')
@login_required
def view_reports():
    user_id = session['user_id']
    
    # Get date filters from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    income_statement = generate_income_statement(user_id, start_date, end_date)
    balance_sheet = generate_balance_sheet(user_id)
    cash_flow = generate_cash_flow(user_id, start_date, end_date)
    
    return render_template('reports.html',
                         income_statement=income_statement,
                         balance_sheet=balance_sheet,
                         cash_flow=cash_flow)

if __name__ == '__main__':
    app.run(debug=True)