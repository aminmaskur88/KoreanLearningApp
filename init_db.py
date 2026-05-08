import sqlite3
import json
import os

def init_db():
    db_path = 'database.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        streak INTEGER DEFAULT 0,
        last_login DATE
    )
    ''')

    # Create vocabulary table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        korean TEXT NOT NULL,
        meaning TEXT NOT NULL,
        romanization TEXT,
        category TEXT,
        level INTEGER,
        example TEXT
    )
    ''')

    # Create hangul table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hangul (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        char TEXT NOT NULL,
        name TEXT,
        type TEXT,
        romanization TEXT,
        pronunciation TEXT
    )
    ''')

    # Create progress table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        user_id INTEGER,
        vocab_id INTEGER,
        status TEXT DEFAULT 'learning',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(vocab_id) REFERENCES vocabulary(id)
    )
    ''')

    # Create quiz_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quiz_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        score INTEGER,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    # Create daily_missions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mission_type TEXT,
        target INTEGER,
        progress INTEGER DEFAULT 0,
        completed BOOLEAN DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    # Seed data
    with open('data/hangul.json', 'r', encoding='utf-8') as f:
        hangul_data = json.load(f)
        for h in hangul_data:
            cursor.execute('INSERT INTO hangul (char, name, type, romanization, pronunciation) VALUES (?, ?, ?, ?, ?)',
                           (h['char'], h['name'], h['type'], h['romanization'], h['pronunciation']))

    with open('data/vocab.json', 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)
        for v in vocab_data:
            cursor.execute('INSERT INTO vocabulary (korean, meaning, romanization, category, level, example) VALUES (?, ?, ?, ?, ?, ?)',
                           (v['korean'], v['meaning'], v['romanization'], v['category'], v['level'], v['example']))

    # Create default user
    cursor.execute("INSERT INTO users (username, xp, level, streak) VALUES ('Pelajar', 0, 1, 0)")

    conn.commit()
    conn.close()
    print("Database initialized and seeded successfully.")

if __name__ == "__main__":
    init_db()
