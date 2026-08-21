import sqlite3
from datetime import date

print("SCRIPT STARTED!")

connection = sqlite3.connect("arithomancer.db")
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS high_scores")

# Make sure the table exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS high_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT NOT NULL,
        questions_survived INTEGER NOT NULL,
        date TEXT NOT NULL
    )
""")

# Clear previous test data

# Reset ID counter

# Fake scores
fake_scores = [
    ("Rishi", 87),
    ("Alex", 72),
    ("Sam", 51),
    ("Rishi", 64),
    ("Maya", 93),
    ("Alex", 41),
    ("John", 28),
    ("Rishi", 76),
    ("Sara", 55),
    ("Tom", 19),
    ("Maya", 68),
    ("Leo", 34)
]

# Insert the 12 scores
for player, questions_survived in fake_scores:

    cursor.execute("""
        INSERT INTO high_scores
        (player, questions_survived, date)
        VALUES (?, ?, ?)
    """, (
        player,
        questions_survived,
        date.today().strftime("%d/%m/%y")
    ))

# Keep only the best 10
cursor.execute("""
    DELETE FROM high_scores
    WHERE id NOT IN (
        SELECT id
        FROM high_scores
        ORDER BY questions_survived DESC
        LIMIT 10
    )
""")

connection.commit()

# Read leaderboard
cursor.execute("""
    SELECT id, player, questions_survived, date
    FROM high_scores
    ORDER BY questions_survived DESC
""")

scores = cursor.fetchall()

connection.close()

# Display
print("\n🏆 HIGH SCORES")
print("-" * 45)

for position, score in enumerate(scores, start=1):

    id, player, questions, played_date = score

    print(
        f"{position:>2}. "
        f"{player:<10} "
        f"{questions:>3} questions   "
        f"{played_date}"
    )

print("-" * 45)
print(f"✓ {len(scores)} scores stored")