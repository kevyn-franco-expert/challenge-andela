import os
DB_PATH = "watchdog.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"Deleted {DB_PATH}")
else:
    print(f"{DB_PATH} not found")
