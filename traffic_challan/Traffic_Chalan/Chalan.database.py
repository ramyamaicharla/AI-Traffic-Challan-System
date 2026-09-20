import sqlite3

# Connect to Chalan.db
conn = sqlite3.connect("Chalan.db")
cursor = conn.cursor()

# Create violations table
cursor.execute("""
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    violation_name TEXT NOT NULL UNIQUE,
    fine INTEGER NOT NULL
)
""")

# Traffic violation data
violations = [
    ("Triple Ride", 1000),
    ("No Parking", 100),
    ("No Helmet", 200),
    ("Overspeed", 1000)
]

# Insert data
cursor.executemany("""
INSERT OR IGNORE INTO violations
(
    violation_name,
    fine
)
VALUES (?, ?)
""", violations)

# Save changes
conn.commit()

# Display database
print("--------------------------------")
print("CHALAN DATABASE")
print("--------------------------------")

cursor.execute("""
SELECT
    id,
    violation_name,
    fine
FROM violations
""")

for row in cursor.fetchall():
    print(row)

print("--------------------------------")

conn.close()

print("Chalan.db created successfully")
print("--------------------------------")