from flask import Flask, request, redirect
from spotipy.oauth2 import SpotifyOAuth
import requests
import spotipy

app = Flask(__name__)
auth = SpotifyOAuth('5a1e2b28b8a043b99d5a19ffb4d8a216',
                    'f31645c086aa4809a5fbaed43ef7ac30', "http://localhost:8000/callback", cache_path=".spotifycache", scope="user-library-read")




# Routes
@app.route("/")
def index():
    token_info = auth.get_cached_token()
    if not token_info:
        # If there isn't a cached token then you will be redirected to a page where you will be asked to login to spotify
        # After that procceed to /callback
        auth_url = auth.get_authorize_url()
        return redirect(auth_url)

    token = token_info['access_token']
    # At this point you can now create a Spotifiy instance with
    #spotipy.client.Spotify(auth=token)

    headers = {
    'Authorization': 'Bearer {val}'.format(val=token),
    # 'Accept': 'application/json',
    # 'Content-Type': 'application/json'
    }

    # base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/'

    # Track ID from the URI
    track_id = '6y0igZArWVi6Iz0rj35c1Y'

    # actual GET request with proper header
    #change the dataType to be in an if statement for the user to determine what data they want to find
    dataType = 'me/player/devices'
    r = requests.get(BASE_URL + dataType, headers=headers)
    print(token)
    r = r.json()
    print(r)


    return f"You now have an access token : {token}"


@app.route("/callback")
def callback():
    print("Hello")
    url = request.url
    code = auth.parse_response_code(url)
    token = auth.get_access_token(code)
    # Once the get_access_token function is called, a cache will be created making it possible to go through the route "/" without having to login anymore
    return redirect("/")

if __name__ == '__main__':
    app.run(port=8000, host="localhost", debug=True)