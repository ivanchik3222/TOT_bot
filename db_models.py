import sqlite3

CHAT_MODES = {
    '💬 Чат': 'chat_default',
    '📚 Учёба': 'chat_study',
    '❤️ Здоровье': 'chat_health',
    '😂 Мемы': 'chat_memes',
    '⌚ Планировщик': 'chat_planner'
}

def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    for table in CHAT_MODES.values():
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    conn.commit()
    conn.close()


def save_message(table: str, user_id: int, role: str, content: str):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO {table} (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    conn.commit()
    conn.close()

def get_history(table: str, user_id: int, limit: int = 20):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT role, content FROM {table} WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{'role': role, 'content': content} for role, content in reversed(rows)]
