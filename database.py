import sqlite3
from datetime import date


DATABASE = "arithomancer.db"


# ============================================================
# DATABASE SETUP
# ============================================================

def create_table():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # --------------------------------------------------------
    # HIGH SCORES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS high_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            questions_survived INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # PROFILES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            arcana INTEGER NOT NULL DEFAULT 0,
            runic_potion_owned INTEGER NOT NULL DEFAULT 0,
            soul_shard_owned INTEGER NOT NULL DEFAULT 0,
            tempo_crystal_owned INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# HIGH SCORES
# ============================================================

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


# ============================================================
# PROFILE FUNCTIONS
# ============================================================

def create_profile(name):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO profiles (name)
            VALUES (?)
        """, (name,))

        connection.commit()

        profile_id = cursor.lastrowid

        return profile_id

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


# ------------------------------------------------------------
# GET ALL PROFILES
# ------------------------------------------------------------

def get_profiles():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            arcana,
            runic_potion_owned,
            soul_shard_owned,
            tempo_crystal_owned
        FROM profiles
        ORDER BY id
    """)

    profiles = cursor.fetchall()

    connection.close()

    return profiles


# ------------------------------------------------------------
# GET ONE PROFILE
# ------------------------------------------------------------

def get_profile(profile_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            arcana,
            runic_potion_owned,
            soul_shard_owned,
            tempo_crystal_owned
        FROM profiles
        WHERE id = ?
    """, (profile_id,))

    profile = cursor.fetchone()

    connection.close()

    return profile


# ------------------------------------------------------------
# CHECK IF PROFILE NAME EXISTS
# ------------------------------------------------------------

def profile_exists(name):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM profiles
        WHERE name = ?
    """, (name,))

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ------------------------------------------------------------
# SAVE PROFILE
# ------------------------------------------------------------

def save_profile(
    profile_id,
    arcana,
    runic_potion_owned,
    soul_shard_owned,
    tempo_crystal_owned
):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE profiles
        SET
            arcana = ?,
            runic_potion_owned = ?,
            soul_shard_owned = ?,
            tempo_crystal_owned = ?
        WHERE id = ?
    """, (
        arcana,
        int(runic_potion_owned),
        int(soul_shard_owned),
        int(tempo_crystal_owned),
        profile_id
    ))

    connection.commit()
    connection.close()

    # =============================
    # DELETE PROFILE
    # =============================
def delete_profile(profile_id):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM profiles
        WHERE id = ?
    """, (profile_id,))

    connection.commit()
    connection.close()