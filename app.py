from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import cv2
import base64
import io
import os
from PIL import Image
import sqlite3
import numpy as np
import random
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create necessary directories
os.makedirs('ml_model', exist_ok=True)
os.makedirs('static/music', exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('temp', exist_ok=True)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key
CORS(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    return None

# Simple emotion detection using face detection and random emotion for demo
def detect_emotion(image):
    """
    Simple emotion detection for demonstration
    In a real application, you would use a proper ML model
    """
    try:
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Load Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            # For demo purposes, return a random emotion when a face is detected
            emotions = ['happy', 'sad', 'angry', 'surprise', 'neutral']
            emotion = random.choice(emotions)
            confidence = round(random.uniform(0.7, 0.95), 2)
        else:
            emotion = 'neutral'
            confidence = 0.5
            
        return emotion, confidence
        
    except Exception as e:
        print(f"Error in emotion detection: {e}")
        return 'neutral', 0.5

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[3], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    
    return jsonify({'success': False, 'message': 'Invalid request method'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    password_hash = generate_password_hash(password)
    
    try:
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username or email already exists'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logout successful'})

@app.route('/user_info')
@login_required
def user_info():
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email
        }
    })

@app.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    data = request.get_json()
    song_id = data.get('song_id')
    
    try:
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO favorites (user_id, song_id) VALUES (?, ?)",
            (current_user.id, song_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Song added to favorites'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Song already in favorites'})

@app.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    data = request.get_json()
    song_id = data.get('song_id')
    
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM favorites WHERE user_id = ? AND song_id = ?",
        (current_user.id, song_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Song removed from favorites'})

@app.route('/get_favorites')
@login_required
def get_favorites():
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id, s.title, s.artist, s.file_path 
        FROM songs s
        JOIN favorites f ON s.id = f.song_id
        WHERE f.user_id = ?
    ''', (current_user.id,))
    
    favorites = cursor.fetchall()
    conn.close()
    
    favorite_songs = [{
        'id': song[0],
        'title': song[1],
        'artist': song[2],
        'file_path': song[3]
    } for song in favorites]
    
    return jsonify({'success': True, 'favorites': favorite_songs})

@app.route('/save_preferences', methods=['POST'])
@login_required
def save_preferences():
    data = request.get_json()
    preferred_genre = data.get('preferred_genre')
    preferred_artist = data.get('preferred_artist')
    
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    
    # Check if preferences already exist
    cursor.execute("SELECT id FROM user_preferences WHERE user_id = ?", (current_user.id,))
    existing_prefs = cursor.fetchone()
    
    if existing_prefs:
        # Update existing preferences
        cursor.execute(
            "UPDATE user_preferences SET preferred_genre = ?, preferred_artist = ?, updated_at = ? WHERE user_id = ?",
            (preferred_genre, preferred_artist, datetime.now(), current_user.id)
        )
    else:
        # Insert new preferences
        cursor.execute(
            "INSERT INTO user_preferences (user_id, preferred_genre, preferred_artist) VALUES (?, ?, ?)",
            (current_user.id, preferred_genre, preferred_artist)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Preferences saved successfully'})

@app.route('/get_preferences')
@login_required
def get_preferences():
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT preferred_genre, preferred_artist FROM user_preferences WHERE user_id = ?",
        (current_user.id,)
    )
    
    prefs = cursor.fetchone()
    conn.close()
    
    preferences = {
        'preferred_genre': prefs[0] if prefs else None,
        'preferred_artist': prefs[1] if prefs else None
    }
    
    return jsonify({'success': True, 'preferences': preferences})

@app.route('/analyze', methods=['POST'])
def analyze_emotion():
    try:
        # Get image data from request
        data = request.get_json()
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64, prefix
        image_bytes = base64.b64decode(image_data)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect emotion
        emotion, confidence = detect_emotion(image_cv)
        
        return jsonify({
            'emotion': emotion,
            'confidence': confidence,
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        })

@app.route('/recommend', methods=['POST'])
def recommend_music():
    try:
        data = request.get_json()
        emotion = data['emotion'].lower()
        
        # Import recommendation function
        from ml_model.recommendation_engine import get_recommendations
        
        # Get recommendations
        recommendations = get_recommendations(emotion)
        
        return jsonify({
            'songs': recommendations,
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)