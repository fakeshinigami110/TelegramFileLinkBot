import sqlite3

def update_database():
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()

    # Add the file_type column if it doesn't exist
    cursor.execute("ALTER TABLE files ADD COLUMN file_type TEXT")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_database()
