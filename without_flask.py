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
        command = input("Awaiting a command: ")
        if "q" in command.lower():
            break
        
        if command == "user_info":
            print(sp.current_user())
        elif command == "-h" or command == "-help":
            print("Valid Command List:")
            print("    -h, --help               shows this help message")
            print("    -q, --quit               quits out of this application")
            print("    -st, --savedTracks       gets your saved tracks")
            print("    -tt, --topTracks         gets your top tracks")
            print("    -gf, --getFriends        gets your friends (you follow them, they follow you)")
            print("    -ff, --findFriends       find users of the application who have a similar music taste as you")
            print("    -cp, --createPlaylist    generates a playlist for you, public or private")
            print("    -dp, --deletePlaylist    deletes a playlist for you")
            print("    -ur, --un-register       un-registers and deletes your info from our application")
        elif command == "-st" or command == "--savedTracks":
            savedTracks()
        elif command == "-tt" or command == "--topTracks":
            topTracks()
        elif command == "-gf" or command == "--getFriends":
            get_friends()
        elif command == "-ff" or command == "--findFriends":
            findFriends()
        elif command == "-cp" or command == "--createPlaylist":
            create_playlist()
        elif command == "-dp" or command == "--deletePlaylist":
            delete_playlist()
        elif command == "-ur" or command == "--un-register":
            unregister()       
        else:
            print("Invalid command")
    print("Logging out now.....")
    print("Thank you for using SpotiStat!")

def savedTracks():
    trackNums = int(input("How many of your saved tracks would you like to view?"))
    results = sp.current_user_saved_tracks(trackNums)
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])

def topTracks():
    return

def get_friends():
    # friends = db.get_friends()
    # print(friends)
    return

def findFriends():
    return

def get_playlists():
    # db.get_playlist
    return

def get_playlist(playlist_name):
    # playlist = db.get_playlist()
    # print(playlist)
    return

def create_playlist():
    name = input("Enter a name for this playlist: ")
    user_ids = input("Enter the usernames of your friends to base this playlist on: ")
    is_public = input("Is this a public or private playlist? (Enter \"public\" or \"private\"): ")
    # min_max = db.get_min_and_max_song_features(user_ids)
    # recommendations = spotify.get_recommendations(min_max)
    # db.insert_playlist(recommendations, is_public)
    print(f"Playlist {name} created. SONGS IN PLAYLIST GO HERE")

def delete_playlist(playlist_name):
    # db.delete_playlist(playlist_name)
    print(f"Playlist {playlist_name} delete")

def unregister():
    return

if __name__ == '__main__':
    if (os.path.exists(f".spotifycache")):
        os.remove(f".spotifycache")
    main()