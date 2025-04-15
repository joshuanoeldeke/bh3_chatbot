import sqlite3
import os

# Get the directory of the current script
current_dir = os.path.dirname(__file__)
db_path = os.path.join(current_dir, "bugland.db")
init_path = os.path.join(current_dir, "init.sql")

# Delete old DB if it exists
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to the SQLite database (this also creates the new database file)
conn = sqlite3.connect(os.path.join(current_dir, "bugland.db"))
c = conn.cursor()

# Read and execute the SQL file
with open(os.path.join(current_dir, "init.sql"), "r") as sql_file:
    sql_script = sql_file.read()

c.executescript(sql_script)

# Commit changes and close the connection
conn.commit()
conn.close()
