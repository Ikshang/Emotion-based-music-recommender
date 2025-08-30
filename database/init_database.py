import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_db():
    # Create database directory
    os.makedirs('database', exist_ok=True)
    
    # Connect to SQLite database (will create if not exists)
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    
    # Create songs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        file_path TEXT NOT NULL,
        emotion_tag TEXT NOT NULL,
        valence REAL NOT NULL,
        energy REAL NOT NULL
    )
    ''')
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create favorites table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        song_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (song_id) REFERENCES songs (id),
        UNIQUE(user_id, song_id)
    )
    ''')
    
    # Create user preferences table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        preferred_genre TEXT,
        preferred_artist TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create a default admin user for testing
    try:
        admin_password = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ("admin", "admin@example.com", admin_password)
        )
    except sqlite3.IntegrityError:
        pass  # Admin user already exists
    
    # Commit and close
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()