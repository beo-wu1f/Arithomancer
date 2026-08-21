import sqlite3
from datetime import date


DATABASE = "arithomancer.db"


# --------------------------------------------------
# CREATE DATABASE TABLE
# --------------------------------------------------

def create_table():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS high_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            questions_survived INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# SAVE A SCORE
# --------------------------------------------------

def save_score(player, questions_survived):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO high_scores
        (player, questions_survived, date)
        VALUES (?, ?, ?)
    """, (
        player,
        questions_survived,
        date.today().strftime("%d/%m/%y")
    ))

    # Keep only the top 10 scores
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
    connection.close()


# --------------------------------------------------
# GET HIGH SCORES
# --------------------------------------------------

def get_high_scores():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT player, questions_survived, date
        FROM high_scores
        ORDER BY questions_survived DESC
    """)

    scores = cursor.fetchall()

    connection.close()

    return scores

def reset_high_scores():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM high_scores")

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name = 'high_scores'
    """)

    connection.commit()
    connection.close()