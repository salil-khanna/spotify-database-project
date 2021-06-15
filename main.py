import os

from flask import Flask, request, redirect
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import requests

app = Flask(__name__)
auth = SpotifyOAuth('5a1e2b28b8a043b99d5a19ffb4d8a216',
                    'f31645c086aa4809a5fbaed43ef7ac30', "http://localhost:8000/callback", cache_path=".spotifycache", scope="user-library-read user-top-read")


# @app.route("/")
def index():
    token_info = auth.get_cached_token()
    if not token_info:
        # If there isn't a cached token then you will be redirected to a page where you will be asked to login to spotify
        # After that procceed to /callback
        auth_url = auth.get_authorize_url()
        return callback()

    token = token_info['access_token']

    # the main access point for all requests and such
    sp = spotipy.Spotify(token)

    top_tracks = sp.current_user_top_tracks()

    # print(top_tracks)
    
    features = sp.audio_features(['06AKEBrKUckW0KREUWRnvT'])
    print(features)


    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])
        
    return f"You now have an access token : {token}\n Please go back to the command line interface."


# @app.route("/callback")
def callback():
    url = request.url
    code = auth.parse_response_code(url)
    token = auth.get_access_token(code)
    # Once the get_access_token function is called, a cache will be created making it possible to go through the route "/" without having to login anymore
    return index()


if __name__ == '__main__':
    if (os.path.exists(f".spotifycache")):
        os.remove(f".spotifycache")
    index()
    app.run(port=8000, host="localhost", debug=True)
