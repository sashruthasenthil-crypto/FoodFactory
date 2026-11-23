import sqlite3
from pathlib import Path

db_path = Path("instance") / "foodfactory.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(raw_material)")
columns = [row[1] for row in cursor.fetchall()]

if "category" not in columns:
    cursor.execute(
        "ALTER TABLE raw_material ADD COLUMN category VARCHAR(100)"
    )

if "minimum_stock" not in columns:
    cursor.execute(
        "ALTER TABLE raw_material ADD COLUMN minimum_stock FLOAT DEFAULT 0"
    )

conn.commit()
conn.close()

print("Database updated successfully!")