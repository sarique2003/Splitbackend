import sqlite3
from database import connect_db
import pandas as pd

def split_expense(expense_id, split_method, splits):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT amount, payer_id FROM expenses WHERE id = ?', (expense_id,))
    expense = cursor.fetchone()
    total_amount, payer_id = expense

    if split_method == 'exact':
        for user_id, amount in splits.items():
            if user_id == payer_id:
                cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
            else:
                cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, user_id))
    elif split_method == 'percent':
        for user_id, percent in splits.items():
            amount = (percent / 100) * total_amount
            if user_id == payer_id:
                cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
            else:
                cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, user_id))
    elif split_method == 'equal':
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        split_amount = total_amount / user_count
        cursor.execute('SELECT id FROM users')
        users = cursor.fetchall()
        for user in users:
            user_id = user[0]
            if user_id == payer_id:
                cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (split_amount, user_id))
            else:
                cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (split_amount, user_id))
    
    conn.commit()
    conn.close()

def generate_balance_sheet(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()
    
    data = []
    for expense in expenses:
        expense_id, amount, description, payer_id, split_method, date = expense
        cursor.execute('SELECT name FROM users WHERE id = ?', (payer_id,))
        payer_name = cursor.fetchone()[0]
        
        data.append({
            'Description': description,
            'Amount': amount,
            'Payer': payer_name,
            'Split Method': split_method,
            'Date': date
        })
    
    df = pd.DataFrame(data)
    file_path = f'balance_sheet_user_{user_id}.xlsx'
    df.to_excel(file_path, index=False)
    
    conn.close()
    return file_path
