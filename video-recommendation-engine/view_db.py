import sqlite3

# Connect to your .db file
conn = sqlite3.connect('socialverse.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Read contents of a specific table
for table_name in tables:
    table = table_name[0]
    print(f"\nContents of {table}:")
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

conn.close()
