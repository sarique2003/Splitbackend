from flask import Flask, request, jsonify, send_file
import sqlite3
import os
import hashlib
from functools import wraps
from split import equal_split, diff_split, percent_split, generate_report

app = Flask(__name__)

def connect_db():
    return sqlite3.connect('Data.db')

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        name TEXT PRIMARY KEY NOT NULL,
        email TEXT NOT NULL UNIQUE,
        mobile REAL DEFAULT 0.0,
        password TEXT NOT NULL
    )
    ''')

    # Create expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        expname TEXT,
        email TEXT,
        amount REAL NOT NULL,
        split_method TEXT NOT NULL,
        FOREIGN KEY (email) REFERENCES users (email)
    )
    ''')

    conn.commit()
    conn.close()

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Decorator to check authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'message': 'Authentication required!'}), 401
        return f(*args, **kwargs)
    return decorated

def check_auth(email, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and user[0] == hash_password(password):
        return True
    return False

# Route to register a new user
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        name = data['name']
        email = data['email']
        mobile = data['mobile']
        password = hash_password(data['password'])

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email, mobile, password) VALUES (?, ?, ?, ?)', (name, email, mobile, password))
        conn.commit()
        conn.close()

        return jsonify({'message': 'User registered successfully!'}), 201

    except sqlite3.IntegrityError as e:
        return jsonify({'error': 'User with this email already exists!'}), 409

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to get user details by email
@app.route('/user/<email>', methods=['GET'])
@requires_auth
def get_user(email):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, email, mobile FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_details = {
                'name': user[0],
                'email': user[1],
                'mobile': user[2]
            }
            return jsonify(user_details), 200
        else:
            return jsonify({'error': 'User not found!'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/addexpense', methods=['POST'])
@requires_auth
def add_expense():
    try:
        data = request.get_json()
        expname = data['expname']
        email = data['email']
        amount = data['amount']
        split_method = data['split_method']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO expenses (expname, email, amount, split_method) VALUES (?, ?, ?, ?)', (expname, email, amount, split_method))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Expense registered successfully!'}), 201

    except sqlite3.IntegrityError as e:
        return jsonify({'error': 'User with this email already exists!'}), 409

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/split', methods=['POST'])
@requires_auth
def split_expense():
    data = request.json
    total_bill = data.get('total_bill')
    num_friends = data.get('num_friends')
    split_method = data.get('split_method').strip().lower()

    if split_method == "equal":
        amounts = equal_split(total_bill, num_friends)
    elif split_method == "diff":
        amounts = diff_split(total_bill, num_friends)
    elif split_method == "percentage":
        amounts = percent_split(total_bill, num_friends)
    else:
        return jsonify({"error": "Invalid split method. Choose from 'Equal', 'Diff', 'Percentage'."}), 400

    pdf_file = generate_report(total_bill, num_friends, amounts, split_method.capitalize())

    response = {
        "amounts": amounts,
        "pdf_file": pdf_file
    }

    # Print individual expensesfor i, amount in enumerate(amounts):
    #    print(f"Person {i+1} owes: {amount}")

    return jsonify(response)

@app.route('/download_report', methods=['GET'])
@requires_auth
def download_report():
    pdf_file = request.args.get('pdf_file')
    if os.path.exists(pdf_file):
        return send_file(pdf_file, as_attachment=True)
    else:
        return jsonify({"error": "File not found."}), 404

@app.route('/total_expense', methods=['GET'])
@requires_auth
def total_expense():
    total_bill = request.args.get('total_bill')
    if total_bill:
        return jsonify({"total_expense": float(total_bill)})
    else:
        return jsonify({"error": "Total bill not provided."}), 400

@app.route('/individual_expenses', methods=['GET'])
@requires_auth
def individual_expenses():
    total_bill = float(request.args.get('total_bill'))
    num_friends = int(request.args.get('num_friends'))
    split_method = request.args.get('split_method').strip().lower()

    if split_method == "equal":
        amounts = equal_split(total_bill, num_friends)
    elif split_method == "diff":
        amounts = diff_split(total_bill, num_friends)
    elif split_method == "percentage":
        amounts = percent_split(total_bill, num_friends)
    else:
        return jsonify({"error": "Invalid split method. Choose from 'Equal', 'Diff', 'Percentage'."}), 400

    return jsonify({"amounts": amounts})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
