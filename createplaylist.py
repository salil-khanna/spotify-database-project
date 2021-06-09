import os

from spotifyclient import SpotifyClient
from flask import Flask, request, redirect
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
auth = SpotifyOAuth('5a1e2b28b8a043b99d5a19ffb4d8a216',
                    'f31645c086aa4809a5fbaed43ef7ac30', "http://localhost:8000/callback", cache_path=".spotifycache", scope="user-library-read")


@app.route("/")
def index():
    

    token_info = auth.get_cached_token()
    if not token_info:
        # If there isn't a cached token then you will be redirected to a page where you will be asked to login to spotify
        # After that procceed to /callback
        auth_url = auth.get_authorize_url()
        return redirect(auth_url)

    token = token_info['access_token']
    
    spotify_client = SpotifyClient("BQBg9199b6ehn_s_-t3VZBU8DviMkO4vkpTRgVlznzKmsmc9qeNwA8_MG0PNZ9alwmZ0YrZGoboYGkQ3Vu8qVwreDmUw87XoTrjEFLv5IWgISB9t4qmflJtOWcOgLGyT0E8Je_-eRxpNJZ530xG9bEg19oTOVMhC7vSKJwj1CmgNfwfzChLv2LEj4w88oajaTl_IwA7zaw2BkReUZ8F8adl1RJ4twurdI9zTrTK8TjBloCK7Z_xGxQCXV4OcdfoRY9z84umSnAfRM0dYp1A",
                                   "salil9")

    # get last played tracks
    num_tracks_to_visualise = int(input("How many tracks would you like to visualise? "))
    last_played_tracks = spotify_client.get_last_played_tracks(num_tracks_to_visualise)

    print(f"\nHere are the last {num_tracks_to_visualise} tracks you listened to on Spotify:")
    for index, track in enumerate(last_played_tracks):
        print(f"{index+1}- {track}")

    # choose which tracks to use as a seed to generate a playlist
    indexes = input("\nEnter a list of up to 5 tracks you'd like to use as seeds. Use indexes separated by a space: ")
    indexes = indexes.split()
    seed_tracks = [last_played_tracks[int(index)-1] for index in indexes]

    # get recommended tracks based off seed tracks
    recommended_tracks = spotify_client.get_track_recommendations(seed_tracks)
    print("\nHere are the recommended tracks which will be included in your new playlist:")
    for index, track in enumerate(recommended_tracks):
        print(f"{index+1}- {track}")

    # get playlist name from user and create playlist
    playlist_name = input("\nWhat's the playlist name? ")
    playlist = spotify_client.create_playlist(playlist_name)
    print(f"\nPlaylist '{playlist.name}' was created successfully.")

    # populate playlist with recommended tracks
    spotify_client.populate_playlist(playlist, recommended_tracks)
    print(f"\nRecommended tracks successfully uploaded to playlist '{playlist.name}'.")


@app.route("/callback")
def callback():
    url = request.url
    code = auth.parse_response_code(url)
    token = auth.get_access_token(code)
    print(token)
    # Once the get_access_token function is called, a cache will be created making it possible to go through the route "/" without having to login anymore
    return redirect("/")

if __name__ == '__main__':
    app.run(port=8000, host="localhost", debug=True)