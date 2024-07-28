import sqlite3

def connect_db():
    conn = sqlite3.connect('Data.db')
    return conn

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Create users table
    #cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        name TEXT PRIMARY KEY NOT NULL,
        email TEXT NOT NULL UNIQUE,
        mobile REAL DEFAULT 0.0,
        password TEXT NOT NULL
    )
    ''')

    # Drop expenses table if it exists cursor.execute('DROP TABLE IF EXISTS expenses')
    # Create expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        expname TEXT NOT NULL,           
        email TEXT NOT NULL,
        amount REAL NOT NULL,
        split_method TEXT NOT NULL,
        FOREIGN KEY (email) REFERENCES users (email)
    )
    ''')

    # Creating the owning table cursor.execute('DROP TABLE IF EXISTS owns')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS owns (
        email1 TEXT NOT NULL,
        email2 TEXT NOT NULL,
        amount REAL NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_db()
