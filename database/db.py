import sqlite3

DB_PATH = "buresu.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        discord_id TEXT,
        ign TEXT,
        team1 TEXT,
        team2 TEXT,
        date TEXT,
        trackerid TEXT,
        reason TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_log(action, discord_id, ign, team1, team2, date, trackerid, reason):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO player_logs
        (action, discord_id, ign, team1, team2, date, trackerid, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (action, discord_id, ign, team1, team2, date, trackerid, reason),
    )

    conn.commit()
    conn.close()


def search_logs(search):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT action, discord_id, ign, team1, team2, date, trackerid, reason
        FROM player_logs
        WHERE discord_id = ?
        OR LOWER(ign) LIKE ?
        OR date LIKE ?
        ORDER BY id DESC
        """,
        (search, f"%{search.lower()}%", f"%{search}%"),
    )

    rows = cursor.fetchall()

    conn.close()

    return rows
