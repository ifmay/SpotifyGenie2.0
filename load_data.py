import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import csv

# Set your credentials
CLIENT_ID = '1346cfb41cc748ccbf22394985a55d3e'
CLIENT_SECRET = '98b6c41c0696447198652300d8d25d14'
REDIRECT_URI = 'http://localhost:3000/callback'

# Spotify OAuth
scope = "playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

# Fetch user's playlists
playlists = sp.current_user_playlists()
all_tracks = []

# Function to fetch all tracks from a playlist
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# Iterate through each playlist
for playlist in playlists['items']:
    playlist_id = playlist['id']
    playlist_name = playlist['name']
    print(f"Fetching tracks from playlist: {playlist_name}")
    tracks = get_playlist_tracks(playlist_id)
    all_tracks.extend(tracks)

print(f"Total tracks fetched: {len(all_tracks)}")

# Export to JSON
with open('spotify_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_tracks, json_file, ensure_ascii=False, indent=4)

# Export to CSV
with open('spotify_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Playlist Name', 'Track Name', 'Artist', 'Album', 'Release Date'])

    track_count = 0
    for item in all_tracks:
        track = item['track']
        if track:  # Check if track is not None
            name = track['name']
            artist = track['artists'][0]['name']
            album = track['album']['name']
            release_date = track['album']['release_date']
            playlist_name = next((pl['name'] for pl in playlists['items'] if pl['id'] == item['added_by']['id']), 'Unknown')
            writer.writerow([playlist_name, name, artist, album, release_date])
            track_count += 1
            print(f"Written track {track_count}: {name} by {artist} in playlist {playlist_name}")

print(f'Total tracks written to CSV: {track_count}')
