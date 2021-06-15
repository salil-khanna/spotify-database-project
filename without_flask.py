import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

auth = SpotifyOAuth('5a1e2b28b8a043b99d5a19ffb4d8a216',
                    'f31645c086aa4809a5fbaed43ef7ac30', "http://localhost:8000/callback", cache_path=".spotifycache", scope="user-library-read user-top-read playlist-modify-public")


# token = auth.get_cached_token()
sp = spotipy.Spotify(auth_manager=auth)
# do not store users top tracks in databases, instead top values


def main():
    print("Welcome to SpotiStat, an application used to connect your music taste with others around the globe!")

    print("Requesting login info now if not stored...")
    userInfo = sp.current_user()['id']
    topTracksList = topTracks()
    topArtistsList = topArtists()
    topValues = analyzeVals(topTracksList) #use these values to generate similarity between users
    # store the top 10 artists, and top 15 songs in the database to be accessed by another users when logged in to determine similarity, and generating group playlists
    print("Use -h or --help to see a list of valid commands...")

    while True:
        command = input("Awaiting a command: \n")
        if "q" in command.lower():
            break

        if command == "user_info":
            print(sp.current_user())
        elif command == "-h" or command == "--help":
            print("Valid Command List:")
            print("    -h, --help                    shows this help message")
            print("    -q, --quit                    quits out of this application")
            print("    -gf, --getFriends             gets your friends on SpotiStat")
            print("    -ff, --findFriends            find users of the application who have a similar music taste as you")
            print("    -cop, --createOwnPlaylist     generates a playlist based around only your tastes")
            print("    -cgp, --createGroupPlaylist   generates a playlist for you around users, public or private")
            print("    -dp, --deletePlaylist         deletes a playlist for you, not only from application, but spotify")
            print("    -ur, --un-register            un-registers and deletes your info from our application")

        elif command == "-gf" or command == "--getFriends":
            get_friends()
        elif command == "-ff" or command == "--findFriends":
            findFriends()
        elif command == "-cop" or command == "--createOwnPlaylist":
            name = create_own_playlist(userInfo, topArtistsList, topTracksList)
            print(f"Your own playlist {name} has been created! Check your Spotify account to confirm.")
        elif command == "-cgp" or command == "--createGroupPlaylist":
            create_group_playlist()
        elif command == "-dp" or command == "--deletePlaylist":
            delete_playlist(userInfo)
        elif command == "-ur" or command == "--un-register":
            unregister()
        else:
            print("Invalid command")
    print("Logging out now.....")
    print("Thank you for using SpotiStat!")


def topTracks():
    results = sp.current_user_top_tracks()
    tracks = []

    for item in results['items']:
        trackID = item['id']
        tracks.append(trackID)
    return tracks

def extractIDFromTracks(extractTracks):
    tracks = []

    for grouping in extractTracks:
        for item in grouping['tracks']:
            trackID = item['id']
            tracks.append(trackID)
    return tracks

def topArtists():
    results = sp.current_user_top_artists()
    artists = []

    for item in results['items']:
        artistID = item['id']
        artists.append(artistID)
    return artists


def analyzeVals(topTracksList):
    audioDict = {'danceability': 0, 'energy': 0,
                 'loudness': 0, 'liveness': 0, 'valence': 0, 'tempo': 0}
    if len(topTracksList) == 0:
        return audioDict
    results = sp.audio_features(topTracksList)
    for song in results:
        audioDict['danceability'] += song['danceability']
        audioDict['energy'] += song['energy']
        audioDict['loudness'] += song['loudness']
        audioDict['liveness'] += song['liveness']
        audioDict['valence'] += song['valence']
        audioDict['tempo'] += song['tempo']

    for key in audioDict.keys():
        audioDict[key] /= len(topTracksList)
    return audioDict


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


def create_own_playlist(userInfo, topArtistsList, topTracksList):
    listTracks = []
    print("Generating recommendations...")
    for i in range(2, 21, 2):
        listTracks.append(sp.recommendations(seed_tracks=topTracksList[i-2:i], seed_artists=topArtistsList[i-2:i], limit=3))
    songsForRec = list(set(extractIDFromTracks(listTracks)))

    name = input("Enter a name for this playlist: ")
    val = sp.user_playlist_create(userInfo, name, public=True, collaborative=False, description='')
    sp.user_playlist_add_tracks(userInfo, val['id'], songsForRec, position=None)

    
    return name


def create_group_playlist():
    name = input("Enter a name for this playlist: ")
    user_ids = input(
        "Enter the usernames of your friends to base this playlist on: ")
    is_public = input(
        "Is this a public or private playlist? (Enter \"public\" or \"private\"): ")

    # show 3 friends, 7 random, : 10 users and then something public about their listening history, enter indices of users you want to make playlist with

    # min_max = db.get_min_and_max_song_features(user_ids)
    # recommendations = spotify.get_recommendations(min_max)
    # db.insert_playlist(recommendations, is_public)
    #also store the link of playlist in database
    print(f"Playlist {name} created. SONGS IN PLAYLIST GO HERE")


def delete_playlist(userInfo):
    playlist_name = input("What playlist do you want to delete?: ")

    # db.delete_playlist(playlist_name)

    allPlaylists = sp.current_user_playlists(limit=50, offset=0)
    for playList in allPlaylists['items']:
        if playlist_name == playList['name']:
            sp.user_playlist_unfollow(userInfo, playList['id'])
            print(f"Playlist {playlist_name} has been deleted!")
            return
    print(f"Playlist {playlist_name} can not be found...")


def unregister():
    # db.remove_user_info(userID)
    return


if __name__ == '__main__':
    # if (os.path.exists(f".spotifycache")):
    #     os.remove(f".spotifycache")
    main()
