from flask import Flask, redirect, url_for, session, request, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import time

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Spotify credentials
CLIENT_ID = '74f384c1133d4c628e8786c706b2575b'
CLIENT_SECRET = '8fad1a53eda04fa99534dc7e95baf266'
REDIRECT_URI = 'http://localhost:3000/callback'

# Spotify OAuth setup
scope = "user-library-read"

def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        return None

    # Check if token has expired
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if is_expired:
        sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                                client_secret=CLIENT_SECRET,
                                redirect_uri=REDIRECT_URI,
                                scope=scope)
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    return token_info

@app.route('/')
def index():
    """Home page with login button."""
    return render_template('index.html')

@app.route('/login')
def login():
    """Redirect user to Spotify login."""
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope=scope)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Spotify's OAuth callback."""
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope=scope)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    print("Token info: ", token_info)
    session['token_info'] = token_info
    return redirect(url_for('display_tracks'))

@app.route('/tracks')
def display_tracks():
    """Fetch and display user's saved tracks."""
    token_info = get_token()
    if not token_info:
        return redirect(url_for('index'))

    sp = Spotify(auth=token_info['access_token'])
    results = sp.current_user_saved_tracks(limit=50)
    tracks = [{'name': item['track']['name'], 'artist': item['track']['artists'][0]['name']}
              for item in results['items']]

    return render_template('tracks.html', tracks=tracks)

if __name__ == '__main__':
    app.run(port=3000, debug=True)