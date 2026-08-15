import os
import sys

db_path = os.path.join(os.path.dirname(__file__), '../backend/db.sqlite3')
if os.path.exists(db_path):
    os.remove(db_path)
    print("Deleted db.sqlite3")
else:
    print("db.sqlite3 does not exist.")
