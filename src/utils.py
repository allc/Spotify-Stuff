import requests
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, API_ENDPOINT


def exchange_code(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('https://accounts.spotify.com/api/token', data=data,
                      headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
    r.raise_for_status()
    return r.json()
