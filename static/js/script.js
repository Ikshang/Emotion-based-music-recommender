// Global variables
let videoStream = null;
let isCameraOn = false;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const startCamBtn = document.getElementById('start-cam');
const stopCamBtn = document.getElementById('stop-cam');
const emotionLabel = document.getElementById('emotion-label');
const confidenceElement = document.getElementById('confidence');
const songList = document.getElementById('song-list');
const noRecommendations = document.getElementById('no-recommendations');
const audioPlayer = document.getElementById('audio-player');
const nowPlaying = document.getElementById('now-playing');
const refreshBtn = document.getElementById('refresh-btn');
const authSection = document.getElementById('auth-section');
const userSection = document.getElementById('user-section');
const appSection = document.getElementById('app-section');
const favoritesSection = document.getElementById('favorites-section');
const userName = document.getElementById('user-name');
const userEmail = document.getElementById('user-email');
const logoutBtn = document.getElementById('logout-btn');
const favoritesBtn = document.getElementById('favorites-btn');
const preferencesBtn = document.getElementById('preferences-btn');
const favoritesList = document.getElementById('favorites-list');
const noFavorites = document.getElementById('no-favorites');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    startCamBtn.addEventListener('click', startCamera);
    stopCamBtn.addEventListener('click', stopCamera);
    captureBtn.addEventListener('click', captureEmotion);
    refreshBtn.addEventListener('click', refreshRecommendations);
    logoutBtn.addEventListener('click', logout);
    favoritesBtn.addEventListener('click', showFavorites);
    preferencesBtn.addEventListener('click', showPreferences);
    document.getElementById('save-preferences').addEventListener('click', savePreferences);
    
    // Set up form submissions
    document.getElementById('login-form').addEventListener('submit', login);
    document.getElementById('register-form').addEventListener('submit', register);
    
    // Initially disable capture button
    captureBtn.disabled = true;
    stopCamBtn.disabled = true;
    
    // Check if user is already logged in
    checkLoginStatus();
});

// Check if user is logged in
function checkLoginStatus() {
    fetch('/user_info')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showUserSection(data.user);
            } else {
                showAuthSection();
            }
        })
        .catch(error => {
            console.error('Error checking login status:', error);
            showAuthSection();
        });
}

// Show authentication section
function showAuthSection() {
    authSection.classList.remove('d-none');
    userSection.classList.add('d-none');
    appSection.classList.add('d-none');
    favoritesSection.classList.add('d-none');
}

// Show user section
function showUserSection(user) {
    authSection.classList.add('d-none');
    userSection.classList.remove('d-none');
    appSection.classList.remove('d-none');
    favoritesSection.classList.add('d-none');
    
    userName.textContent = user.username;
    userEmail.textContent = user.email;
    
    // Load user preferences
    loadPreferences();
}

// Login function
function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            checkLoginStatus();
        } else {
            alert('Login failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Login failed. Please try again.');
    });
}

// Register function
function register(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Registration successful. Please login.');
            document.getElementById('login-tab').click();
        } else {
            alert('Registration failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Registration failed. Please try again.');
    });
}

// Logout function
function logout() {
    fetch('/logout')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAuthSection();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Show favorites
function showFavorites() {
    appSection.classList.add('d-none');
    favoritesSection.classList.remove('d-none');
    
    fetch('/get_favorites')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayFavorites(data.favorites);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Display favorites
function displayFavorites(favorites) {
    favoritesList.innerHTML = '';
    
    if (favorites.length === 0) {
        noFavorites.classList.remove('d-none');
        return;
    }
    
    noFavorites.classList.add('d-none');
    
    favorites.forEach(song => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        listItem.innerHTML = `
            <div>
                <strong>${song.title}</strong><br>
                <small class="text-muted">${song.artist}</small>
            </div>
            <div>
                <button class="btn btn-sm btn-outline-primary play-btn me-2" data-path="${song.file_path}">
                    Play
                </button>
                <button class="btn btn-sm btn-outline-danger remove-favorite-btn" data-id="${song.id}">
                    Remove
                </button>
            </div>
        `;
        
        favoritesList.appendChild(listItem);
    });
    
    // Add event listeners
    document.querySelectorAll('.play-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const songPath = this.getAttribute('data-path');
            playSong(songPath, this);
        });
    });
    
    document.querySelectorAll('.remove-favorite-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const songId = this.getAttribute('data-id');
            removeFavorite(songId, this.closest('li'));
        });
    });
}

// Remove favorite
function removeFavorite(songId, listItem) {
    fetch('/remove_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ song_id: songId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            listItem.remove();
            
            // Check if there are any favorites left
            if (favoritesList.children.length === 0) {
                noFavorites.classList.remove('d-none');
            }
        } else {
            alert('Failed to remove favorite: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to remove favorite. Please try again.');
    });
}

// Show preferences modal
function showPreferences() {
    const modal = new bootstrap.Modal(document.getElementById('preferencesModal'));
    modal.show();
}

// Load preferences
function loadPreferences() {
    fetch('/get_preferences')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('preferred-genre').value = data.preferences.preferred_genre || '';
                document.getElementById('preferred-artist').value = data.preferences.preferred_artist || '';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Save preferences
function savePreferences() {
    const preferredGenre = document.getElementById('preferred-genre').value;
    const preferredArtist = document.getElementById('preferred-artist').value;
    
    fetch('/save_preferences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            preferred_genre: preferredGenre, 
            preferred_artist: preferredArtist 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Preferences saved successfully!');
            bootstrap.Modal.getInstance(document.getElementById('preferencesModal')).hide();
        } else {
            alert('Failed to save preferences: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to save preferences. Please try again.');
    });
}

// Refresh recommendations
function refreshRecommendations() {
    if (emotionLabel.textContent !== 'None') {
        getRecommendations(emotionLabel.textContent);
    }
}

// Start camera
async function startCamera() {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        video.srcObject = videoStream;
        isCameraOn = true;
        
        // Enable/disable buttons
        captureBtn.disabled = false;
        stopCamBtn.disabled = false;
        startCamBtn.disabled = true;
    } catch (err) {
        console.error('Error accessing camera:', err);
        alert('Could not access camera. Please check permissions.');
    }
}

// Stop camera
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        isCameraOn = false;
        
        // Enable/disable buttons
        captureBtn.disabled = true;
        stopCamBtn.disabled = true;
        startCamBtn.disabled = false;
        
        // Reset emotion label
        emotionLabel.textContent = 'None';
        confidenceElement.textContent = '0%';
    }
}

// Capture emotion from camera
function captureEmotion() {
    if (!isCameraOn) {
        alert('Please start the camera first.');
        return;
    }
    
    // Draw video frame to canvas
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert canvas to base64
    const imageData = canvas.toDataURL('image/jpeg');
    
    // Send to server for emotion analysis
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update emotion label
            emotionLabel.textContent = data.emotion;
            emotionLabel.className = `badge bg-${getEmotionColor(data.emotion)}`;
            confidenceElement.textContent = `${(data.confidence * 100).toFixed(2)}%`;
            
            // Get music recommendations
            getRecommendations(data.emotion);
        } else {
            console.error('Error analyzing emotion:', data.error);
            alert('Error analyzing emotion. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error analyzing emotion. Please try again.');
    });
}

// Get music recommendations based on emotion
function getRecommendations(emotion) {
    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ emotion: emotion })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayRecommendations(data.songs);
        } else {
            console.error('Error getting recommendations:', data.error);
            alert('Error getting recommendations. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error getting recommendations. Please try again.');
    });
}

// Display recommendations
function displayRecommendations(songs) {
    // Clear previous recommendations
    songList.innerHTML = '';
    noRecommendations.classList.add('d-none');
    
    if (songs.length === 0) {
        noRecommendations.textContent = 'No recommendations found for this emotion.';
        noRecommendations.classList.remove('d-none');
        return;
    }
    
    // Add each song to the list
    songs.forEach(song => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        listItem.innerHTML = `
            <div>
                <strong>${song.title}</strong><br>
                <small class="text-muted">${song.artist}</small>
            </div>
            <div>
                <button class="btn btn-sm btn-outline-primary play-btn me-2" data-path="${song.file_path}">
                    Play
                </button>
                <button class="btn btn-sm btn-outline-success favorite-btn" data-id="${song.id}">
                    ♥
                </button>
            </div>
        `;
        
        songList.appendChild(listItem);
    });
    
    // Add event listeners to play buttons
    document.querySelectorAll('.play-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const songPath = this.getAttribute('data-path');
            playSong(songPath, this);
        });
    });
    
    // Add event listeners to favorite buttons
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const songId = this.getAttribute('data-id');
            addFavorite(songId, this);
        });
    });
}

// Add to favorites
function addFavorite(songId, button) {
    fetch('/add_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ song_id: songId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.classList.remove('btn-outline-success');
            button.classList.add('btn-success');
            button.disabled = true;
            button.textContent = '✓';
        } else {
            alert('Failed to add to favorites: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to add to favorites. Please try again.');
    });
}

// Play a song
function playSong(songPath, button) {
    // Update now playing text
    const songItem = button.closest('.list-group-item');
    const songTitle = songItem.querySelector('strong').textContent;
    const artistName = songItem.querySelector('.text-muted').textContent;
    nowPlaying.textContent = `${songTitle} by ${artistName}`;
    
    // Set audio source and play
    audioPlayer.src = songPath;
    audioPlayer.play();
    
    // Visual feedback
    document.querySelectorAll('.play-btn').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    
    button.classList.remove('btn-outline-primary');
    button.classList.add('btn-primary');
}

// Helper function to get color based on emotion
function getEmotionColor(emotion) {
    const colorMap = {
        'happy': 'success',
        'sad': 'info',
        'angry': 'danger',
        'surprise': 'warning',
        'neutral': 'secondary',
        'fear': 'dark',
        'disgust': 'dark'
    };
    
    return colorMap[emotion.toLowerCase()] || 'primary';
}