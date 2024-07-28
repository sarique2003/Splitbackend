import sqlite3

def fetch_all_data(db_name, table_name):
    conn = sqlite3.connect(db_name)

    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()

    # Print the column names
    column_names = [description[0] for description in cursor.description]
    print(f"{' | '.join(column_names)}")
    print('-' * 40)
    for row in rows:
        print(f"{' | '.join(map(str, row))}")
    conn.close()

fetch_all_data('Data.db', 'expenses')
