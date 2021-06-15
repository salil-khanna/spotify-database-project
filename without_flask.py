import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

scope = "user-library-read"
auth = SpotifyOAuth('5a1e2b28b8a043b99d5a19ffb4d8a216',
                    'f31645c086aa4809a5fbaed43ef7ac30', "http://localhost:8000/callback", cache_path=".spotifycache", scope="user-library-read user-top-read")

sp = spotipy.Spotify(auth_manager=auth)


def main():
    print("Welcome to SpotiStat, an application used to connect your music taste with others around the globe!")
    print("Use -h or --help to see a list of valid commands...")
    while True:
        command = input()
        if "q" in command.lower():
            break
        
        if command == "user_info":
            print(sp.current_user())
        elif command == "saved_tracks":
            savedTracks()
        else:
            print("invalid command")
    print("Thank you for using SpotiStat!")

def savedTracks():
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])


if __name__ == '__main__':
    if (os.path.exists(f".spotifycache")):
        os.remove(f".spotifycache")
    main()