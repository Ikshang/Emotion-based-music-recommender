import sqlite3
import os

# Emotion to valence/energy mapping
EMOTION_FEATURES = {
    'happy': {'valence': 0.8, 'energy': 0.7},
    'sad': {'valence': 0.2, 'energy': 0.3},
    'angry': {'valence': 0.3, 'energy': 0.9},
    'surprise': {'valence': 0.7, 'energy': 0.8},
    'neutral': {'valence': 0.5, 'energy': 0.5},
    'fear': {'valence': 0.2, 'energy': 0.6},
    'disgust': {'valence': 0.3, 'energy': 0.4}
}

def add_song(title, artist, file_path, emotion_tag):
    """Add a song to the database with the specified emotion tag"""
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    
    # Get valence and energy based on emotion
    features = EMOTION_FEATURES.get(emotion_tag, {'valence': 0.5, 'energy': 0.5})
    
    # Insert song
    cursor.execute('''
    INSERT INTO songs (title, artist, file_path, emotion_tag, valence, energy)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, artist, file_path, emotion_tag, features['valence'], features['energy']))
    
    conn.commit()
    conn.close()
    print(f"Added song: {title} by {artist}")

def add_sample_data():
    """Add sample data to the database for demonstration"""
    # Sample songs for each emotion
    sample_songs = [
        # Happy songs
        {"title": "Sunny Day", "artist": "Joyful Artist", "emotion": "happy"},
        {"title": "Happy Tune", "artist": "Smiling Band", "emotion": "happy"},
        
        # Sad songs
        {"title": "Rainy Night", "artist": "Melancholy Singer", "emotion": "sad"},
        {"title": "Lonely Road", "artist": "Soulful Artist", "emotion": "sad"},
        
        # Angry songs
        {"title": "Thunder Storm", "artist": "Intense Band", "emotion": "angry"},
        {"title": "Raging Fire", "artist": "Powerful Singer", "emotion": "angry"},
        
        # Surprise songs
        {"title": "Unexpected Twist", "artist": "Surprising Band", "emotion": "surprise"},
        {"title": "Sudden Change", "artist": "Unexpected Artist", "emotion": "surprise"},
        
        # Neutral songs
        {"title": "Calm Breeze", "artist": "Relaxing Band", "emotion": "neutral"},
        {"title": "Quiet Moment", "artist": "Peaceful Singer", "emotion": "neutral"},
        
        # Fear songs
        {"title": "Dark Alley", "artist": "Scary Band", "emotion": "fear"},
        {"title": "Haunted House", "artist": "Spooky Singer", "emotion": "fear"},
        
        # Disgust songs
        {"title": "Bitter Taste", "artist": "Revolting Band", "emotion": "disgust"},
        {"title": "Unpleasant Feeling", "artist": "Displeased Singer", "emotion": "disgust"},
    ]
    
    for song in sample_songs:
        file_path = f"/static/music/{song['emotion']}/sample.mp3"
        add_song(song["title"], song["artist"], file_path, song["emotion"])

if __name__ == '__main__':
    # Initialize database first if not exists
    from init_database import init_db
    init_db()
    
    # Add sample data
    add_sample_data()
    print("Sample data added to database!")