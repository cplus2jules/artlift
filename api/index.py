from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI()

origins = [
    "https://artlift.vercel.app",
    "http://artlift.vercel.app",
    "http://localhost",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
        }
    )

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/static/{file_path:path}")
async def static_files(file_path: str):
    file_location = STATIC_DIR / file_path
    if not file_location.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_location))
sp = None

class SpotifyURL(BaseModel):
    url: str

def init_spotify():
    global sp
    try:
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        
        logger.info(f"Initializing Spotify client with ID: {client_id[:5]}...")
        
        if not client_id or not client_secret:
            logger.error("Missing Spotify credentials")
            return None
            
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=15)
        logger.info("Spotify client initialized successfully")
        return sp
    except Exception as e:
        logger.error(f"Spotify Client Configuration Error: {str(e)}")
        return None
sp = init_spotify()

@app.post("/get_cover")
async def get_cover(spotify_url: SpotifyURL):
    global sp
    
    # Log the incoming request
    logger.info(f"Received request for URL: {spotify_url.url}")
    
    if sp is None:
        sp = init_spotify()  # Try to reinitialize if not set
        if sp is None:
            logger.error("Failed to initialize Spotify client")
            raise HTTPException(status_code=500, detail="Spotify client not configured")

    if not spotify_url.url.strip():
        logger.error("Empty URL provided")
        raise HTTPException(status_code=400, detail="Please provide a Spotify URL")

    try:
        spotify_id = extract_spotify_id(spotify_url.url)
        if not spotify_id:
            logger.error(f"Invalid URL format: {spotify_url.url}")
            raise HTTPException(status_code=400, detail="Invalid Spotify URL format")

        try:
            logger.info(f"Fetching {'playlist' if 'playlist' in spotify_url.url.lower() else 'album'} with ID: {spotify_id}")
            if 'playlist' in spotify_url.url.lower():
                result = sp.playlist(spotify_id)
            else:
                result = sp.album(spotify_id)

            images = result.get('images', [])
            if not images:
                logger.error("No artwork found in response")
                raise HTTPException(status_code=404, detail="No artwork found")

            largest_image = max(images, key=lambda x: x['width'] if x['width'] else 0)
            logger.info(f"Successfully found artwork for: {result['name']}")
            
            return {
                'image_url': largest_image['url'],
                'name': result['name']
            }
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API Error: {str(e)}")
            if e.http_status == 404:
                raise HTTPException(status_code=404, detail="Playlist or album not found. Please check the URL and try again.")
            else:
                raise HTTPException(status_code=e.http_status, detail=f"Spotify API error: {str(e)}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

def extract_spotify_id(url: str) -> str:
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
