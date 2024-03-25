from dotenv import load_dotenv
from os import getenv
import secrets

load_dotenv()

DEBUG = getenv('DEBUG', 'False') == 'True'
API_ENDPOINT = 'https://api.spotify.com/v1'
CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')
REDIRECT_URI = getenv('REDIRECT_URI') or 'http://localhost:5000/spotify-oauth2'
SECRET_KEY = getenv('SECRET_KEY') or secrets.token_urlsafe(16)
