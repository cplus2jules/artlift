# Artlift _Spotify Cover Art Extractor_

A responsive web application that allows users to extract high-resolution artwork from Spotify playlists and albums.

## Features

- Extract high-quality cover art from Spotify playlists and albums
- Simple and intuitive user interface
- Spotify-inspired design
- Direct download functionality
- Responsive design for mobile and desktop

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Spotify Developer credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Copy your Client ID and Client Secret

4. Create a `.env` file:
   - Copy `.env.example` to `.env`
   - Fill in your Spotify credentials:
     ```
     SPOTIFY_CLIENT_ID=your_client_id_here
     SPOTIFY_CLIENT_SECRET=your_client_secret_here
     ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Copy a Spotify playlist or album URL
2. Paste it into the input field
3. Click "Get Artwork"
4. Download the high-resolution artwork

## Technologies Used

- Flask
- Spotipy (Spotify Web API)
- HTML/CSS/JavaScript
- Spotify Web API
