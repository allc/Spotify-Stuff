from flask import Flask, render_template, session, request, redirect, make_response
from config import DEBUG, API_ENDPOINT, CLIENT_ID, REDIRECT_URI, SECRET_KEY
from utils import exchange_code
import requests
import io
import zipfile
import json

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/')
def index():
    spotify_aurhotize_url = 'https://accounts.spotify.com/authorize?client_id=%s&response_type=code&redirect_uri=%s' % (CLIENT_ID, REDIRECT_URI)
    return render_template('index.html', spotify_aurhotize_url=spotify_aurhotize_url)

@app.route('/spotify-oauth2')
def spotify_oauth2():
    exchange_code_result = exchange_code(request.args.get('code'))
    # SPOTIFY TOKEN IS STORED IN SESSION COOKIE UNENCRYPTED!
    session['spotify_access_token'] = exchange_code_result['access_token']
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'spotify_access_token' not in session:
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/me')
def user():
    if 'spotify_access_token' not in session:
        return redirect('/')
    r = requests.get('%s/me' % API_ENDPOINT,
                                 headers={'Authorization': 'Bearer %s' % session['spotify_access_token']})
    r.raise_for_status()
    return r.json()

@app.route('/me/playlists')
def my_playlists():
    #TODO: deal with paging
    if 'spotify_access_token' not in session:
        return redirect('/')
    r = requests.get('%s/me/playlists' % API_ENDPOINT,
                                 headers={'Authorization': 'Bearer %s' % session['spotify_access_token']})
    r.raise_for_status()
    return r.json()

@app.route('/playlist/<playlist_id>')
def playlist(playlist_id):
    #TODO: deal with paging
    if 'spotify_access_token' not in session:
        return redirect('/')
    r = requests.get('%s/playlists/%s' % (API_ENDPOINT, playlist_id),
                                 headers={'Authorization': 'Bearer %s' % session['spotify_access_token']})
    r.raise_for_status()
    return r.json()

@app.route('/archive')
def archive():
    if 'spotify_access_token' not in session:
        return redirect('/')
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        me = user()
        zip_file.writestr('me.json', json.dumps(me))
        for i, image in enumerate(me['images']):
            r = requests.get(image['url'])
            zip_file.writestr('me_images_%d_%d_%d.jpg' % (i, image['height'], image['width']), r.content)
        playlists = my_playlists()
        zip_file.writestr('playlists.json', json.dumps(playlists))
        for playlist_ in playlists['items']:
            playlist_data = playlist(playlist_['id'])
            print(playlist_data)
            zip_file.writestr('playlist_%s.json' % playlist_['name'], json.dumps(playlist_data))
            if playlist_data['images']:
                for i, image in enumerate(playlist_data['images']):
                    r = requests.get(image['url'])
                    zip_file.writestr('playlist_images_%s_%d_%d_%d.jpg' % (playlist_['name'], i, image['height'] or 0, image['width'] or 0), r.content)
    zip_buffer.seek(0)
    response = make_response(zip_buffer.read())
    response.headers.set('Content-Type', 'zip')
    response.headers.set('Content-Disposition', 'attachment', filename='spotify-archive.zip')
    return response
    
if __name__ == '__main__':
    app.run(debug=DEBUG)
