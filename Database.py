import sqlite3

def create_database():
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL,
            deep_link TEXT NOT NULL UNIQUE
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
