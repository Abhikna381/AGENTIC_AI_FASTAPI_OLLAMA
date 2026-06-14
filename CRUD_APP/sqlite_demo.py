import sqlite3

conn = sqlite3.connect('test.db') # Connect to the SQLite database (or create it if it doesn't exist)
cursor = conn.cursor() # Create a cursor object to interact with the database

# List all tables in database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") # Execute a query to get the names of all tables in the database
tables = cursor.fetchall() # Fetch all results from the query and store them in the 'tables' variable
print("Tables:", tables)

# Query from the first table
if tables:
    table_name = tables[0][0] # Get the name of the first table from the list of tables
    cursor.execute(f"SELECT * FROM {table_name};") # Execute a query to select all records from the first table
    rows = cursor.fetchall() # Fetch all results from the query and store them in the 'rows' variable
    for row in rows:
        print(row)

conn.close() # Close the connection to the database to free up resources