from flask import Flask, render_template, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure Spotify client
client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=15)

def extract_spotify_id(url):
    try:
        if 'playlist' in url:
            if '/playlist/' in url:
                return url.split('/playlist/')[1].split('?')[0].split('/')[0]
            elif ':playlist:' in url:
                return url.split(':playlist:')[1]
        elif 'album' in url:
            if '/album/' in url:
                return url.split('/album/')[1].split('?')[0].split('/')[0]
            elif ':album:' in url:
                return url.split(':album:')[1]
        return None
    except Exception:
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_cover', methods=['POST'])
def get_cover():
    spotify_url = request.json.get('url', '').strip()
    
    if not spotify_url:
        return jsonify({'error': 'Please provide a Spotify URL'}), 400

    try:
        spotify_id = extract_spotify_id(spotify_url)
        if not spotify_id:
            return jsonify({'error': 'Invalid Spotify URL format'}), 400

        try:
            if 'playlist' in spotify_url.lower():
                result = sp.playlist(spotify_id)
            else:
                result = sp.album(spotify_id)
            images = result.get('images', [])
            if not images:
                return jsonify({'error': 'No artwork found'}), 404

            largest_image = max(images, key=lambda x: x['width'] if x['width'] else 0)
            
            return jsonify({
                'image_url': largest_image['url'],
                'name': result['name']
            })
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                return jsonify({'error': 'Playlist or album not found. Please check the URL and try again.'}), 404
            else:
                return jsonify({'error': f'Spotify API error: {str(e)}'}), e.http_status
                
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
