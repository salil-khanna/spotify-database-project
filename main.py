import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time
from sql import group_recommendations_db
import math

auth = SpotifyOAuth(
    "5a1e2b28b8a043b99d5a19ffb4d8a216",
    "f31645c086aa4809a5fbaed43ef7ac30",
    "http://localhost:8000/callback",
    cache_path=".spotifycache",
    scope="user-library-read user-top-read playlist-modify-public playlist-modify-private playlist-read-collaborative",
)

token = auth.get_cached_token()
if token is None:
    sp = spotipy.Spotify(auth_manager=auth)
else:
    sp = spotipy.Spotify(token["access_token"], auth_manager=auth)

db = group_recommendations_db()


def main():
    print(
        "Welcome to SpotiStat, an application used to connect your music taste with others around the globe!"
    )

    print("Requesting login info now if not stored, come back to program when done...")
    time.sleep(2)
    userInfo = sp.current_user()["id"]
    topTracksList = topTracks()
    print(f"Hello, {sp.current_user()['display_name']}!")
    topArtistsList = topArtists()
    if len(topTracksList) < 10 or len(topArtistsList) < 10:
        print(
            "Listen to more songs and artists and then come back to our application :)"
        )
        return
    topValues = analyzeVals(topTracksList)
    exists = db.user_id_exists(userInfo)

    copyTrackList = []
    for idx, id in enumerate(topTracksList):
        copyTrackList.append((idx + 1, id))

    copyArtistList = []
    for idx, id in enumerate(topArtistsList):
        copyArtistList.append((idx + 1, id))

    if not exists:
        db.insert_user(userInfo)
        for track in topTracksList:
            db.insert_song(track, "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        for artist in topArtistsList:
            db.insert_artist(artist)
        db.insert_top_tracks(userInfo, copyTrackList)
        db.insert_top_artists(userInfo, copyArtistList)
    else:
        for track in topTracksList:
            db.insert_song(track, "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        for artist in topArtistsList:
            db.insert_artist(artist)
        db.update_user_top_tracks(userInfo, copyTrackList)
        db.update_user_top_artists(userInfo, copyArtistList)

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
            print(
                "    -ff, --findFriends            find users of the application who have a similar music taste as you"
            )
            print(
                "    -cop, --createOwnPlaylist     generates a playlist based around only your tastes"
            )
            print(
                "    -cgp, --createGroupPlaylist   generates a playlist for you around users, public or private"
            )
            print(
                "    -gcp, --getCommunityPlaylist  gets the usernames of people in your community and the songs in the respective playlist"
            )
            print(
                "    -gyc, --getYourCommunities    gets the names of all your communities"
            )
            print(
                "    -dp, --deletePlaylist         deletes a playlist for you, not only from application, but spotify"
            )
            print(
                "    -lo, --logout                 logs you out of the application, requiring you to sign in again"
            )
            print(
                "    -ur, --un-register            un-registers and deletes your info from our application"
            )

        elif command == "-gf" or command == "--getFriends":
            get_friends(userInfo)
        elif command == "-ff" or command == "--findFriends":
            findFriends(topValues, userInfo)
        elif command == "-cop" or command == "--createOwnPlaylist":
            name = create_own_playlist(userInfo, topArtistsList, topTracksList)
            print(
                f"Your own playlist '{name}' has been created! Check your Spotify account to confirm."
            )
        elif command == "-cgp" or command == "--createGroupPlaylist":
            create_group_playlist(topValues, userInfo, topArtistsList, topTracksList)
        elif command == "-gcp" or command == "--getCommunityPlaylist":
            get_community_playlist(userInfo)
        elif command == "-gyc" or command == "--getYourCommunities":
            get_your_communities(userInfo)
        elif command == "-dp" or command == "--deletePlaylist":
            delete_playlist(userInfo)
        elif command == "-lo" or command == "--logout":
            logout()
            break
        elif command == "-ur" or command == "--un-register":
            answer = unregister(userInfo)
            if answer:
                print("Sad to see you go :(")
                break
        else:
            print("Invalid command")
    print("Logging out now.....")
    print("Thank you for using SpotiStat!")


def topTracks():
    results = sp.current_user_top_tracks()
    tracks = []

    for item in results["items"]:
        trackID = item["id"]
        tracks.append(trackID)
    return tracks


def extractIDFromTracks(extractTracks):
    tracks = []

    for grouping in extractTracks:
        for item in grouping["tracks"]:
            trackID = item["id"]
            tracks.append(trackID)
    return tracks


def topArtists():
    results = sp.current_user_top_artists()
    artists = []

    for item in results["items"]:
        artistID = item["id"]
        artists.append(artistID)
    return artists


def analyzeVals(topTracksList):
    audioDict = {
        "acousticness": 0,
        "danceability": 0,
        "energy": 0,
        "instrumentalness": 0,
        "liveness": 0,
        "speechiness": 0,
        "valence": 0,
        "tempo": 0,
    }
    if len(topTracksList) == 0:
        return audioDict
    results = sp.audio_features(topTracksList)
    for song in results:
        audioDict["acousticness"] += song["acousticness"]
        audioDict["danceability"] += song["danceability"]
        audioDict["energy"] += song["energy"]
        audioDict["instrumentalness"] += song["instrumentalness"]
        audioDict["liveness"] += song["liveness"]
        audioDict["speechiness"] += song["speechiness"]
        audioDict["valence"] += song["valence"]
        audioDict["tempo"] += song["tempo"]

    for key in audioDict.keys():
        audioDict[key] /= len(topTracksList)
    # print(audioDict)
    return audioDict


def get_friends(userInfo):
    friends = db.get_friends(userInfo)
    if len(friends) == 0:
        print("You have no friends!")
    else:
        for idx, friend in enumerate(friends):
            print(f"{idx + 1}. {friend}")
    return friends


def findFriends(topValues, userInfo):
    allUserDisplays = []

    print("Check out these users!")
    print("spotify_id          similarity          top 3 artists          top track")
    for row in allUserDisplays:
        print("{:< 20} {: <20} {: <20} {: <20}".format(*row))
    users = db.get_users_except_friends_and_you(userInfo, get_friends(userInfo))
    for user in users:
        userDisplay = []
        userDisplay.append(user)
        topartist = sp.artist(db.get_user_top_artists(user)[1])
        toptrack = sp.track(db.get_user_top_tracks(user)[1])
        userAverage = analyzeVals(db.get_user_top_tracks(user))
        score = pow(userAverage["acousticness"] - topValues["acousticness"], 2)
        +pow(userAverage["danceability"] - topValues["danceability"], 2)
        +pow(userAverage["energy"] - topValues["energy"], 2)
        +pow(userAverage["instrumentalness"] - topValues["instrumentalness"], 2)
        +pow(userAverage["liveness"] - topValues["liveness"], 2)
        +pow(userAverage["speechiness"] - topValues["speechiness"], 2)
        +pow(userAverage["valence"] - topValues["valence"], 2)
        +pow((userAverage["tempo"] - topValues["tempo"]) / 1000, 2)
        print(f"{user}        {(1-score)*100}%")
    return


def get_your_communities(userInfo):
    playlists = db.get_your_playlists(userInfo)
    print("The playlists you are a part of include: ")
    for idx, playlist in enumerate(playlists):
        print(f"{idx + 1}. {playlist}")
    return


def get_community_playlist(userInfo):
    playlist_name = input("What community playlist do you want to search for?: ")
    playlist_users = db.users_in_playlist(
        playlist_name
    )  # also retrieve the link for the playlist if any if user is in private, or any if public
    isPublic = db.is_public_list(playlist_name)
    if userInfo in playlist_users:
        link = db.getPlaylistLink(playlist_name)
        print(f"The link for '{playlist_name}' is {link} with users: ")
        for user in playlist_users:
            print(user)
    elif isPublic:
        link = db.getPlaylistLink(playlist_name)
        print(f"The link for '{playlist_name}' is {link} with users: ")
        for user in playlist_users:
            print(user)
    elif not isPublic:
        print("Sorry, the playlist is private")
    else:
        print("Invalid community name.")

    return


def create_own_playlist(userInfo, topArtistsList, topTracksList):
    songsForRec = generate_recs(topArtistsList, topTracksList)

    name = input("Enter a name for this playlist: ")

    createAndPopulatePlayList([], name, songsForRec, True, userInfo)

    return name


def generate_recs(topArtistsList, topTracksList):
    listTracks = []
    print("Generating recommendations...")
    length = len(topTracksList)
    indexer = math.floor(length / 10)
    for i in range(indexer, length + 1, indexer):
        listTracks.append(
            sp.recommendations(
                seed_tracks=topTracksList[i - indexer : i],
                seed_artists=topArtistsList[i - indexer : i],
                limit=3,
            )
        )  # add more info for recommendations, min and max values
    songsForRec = list(set(extractIDFromTracks(listTracks)))
    return songsForRec


def createAndPopulatePlayList(communityList, name, songsForRec, publicVal, userInfo):
    val = sp.user_playlist_create(
        userInfo,
        name,
        public=(len(communityList) == 0),
        collaborative=(len(communityList) != 0),
        description="",
    )
    sp.user_playlist_add_tracks(userInfo, val["id"], songsForRec, position=None)
    for member in communityList:
        priv = sp.user_playlist_create(
            member, name, public=publicVal, collaborative=False, description=""
        )
        sp.user_playlist_add_tracks(member, priv["id"], songsForRec, position=None)
    return val["external_urls"]["spotify"], val["id"]


def create_group_playlist(topValues, userInfo, topArtistsList, topTracksList):

    # have to figure out what happens if you have less than 3 friends, or maybe less than 7 users in table, also need to do all the error checking if user types bad inputs
    name = input("Enter a name for this community playlist: ")

    satisfy = 2
    friends = get_friends(userInfo)
    if len(friends) == 0 and len(megaList) == 0:
        print(
            "Unable to create group playlist..., listen to more songs or wait for more users to join the application!"
        )
        return

    selected_friends = []
    if len(friends) == 0:
        print(
            "Select your friends. Wait..., your friends list is empty! Moving onto other users..."
        )
    else:
        user_ids = input(
            "Select 1 or 2 of your friends to base this playlist on (indice(s) with spaces): "
        )
        user_ids = user_ids.split()
        while len(user_ids) > 2 or len(user_ids) < 1:
            user_ids = input("Please choose a valid set of indice(s): ")
            user_ids = user_ids.split()
            try:
                user_ids = [int(i) for i in user_ids]
            except ValueError:
                user_ids = []
            for i in user_ids:
                if i > len(friends) or i < 1:
                    print("Some indice is out of bounds...")
                    break
        for i in user_ids:
            selected_friends.append(friends[i - 1])
        satisfy -= len(selected_friends)

    selected_random = []
    if len(megaList) < satisfy:
        print("There are not enough users that are similar to you...")
    else:
        count = 1
        count = printNames(top99, 99, count)
        count = printNames(top90, 90, count)
        count = printNames(top75, 75, count)
        count = printNames(top50, 50, count)

        random_ids = input(
            f"Select {satisfy} random users to base this playlist on (indices with spaces): "
        )
        random_ids = random_ids.split()

        while len(random_ids) != satisfy:
            random_ids = input(f"Please choose {satisfy} valid indices: ")
            random_ids = random_ids.split()
            try:
                random_ids = [int(i) for i in random_ids]
            except ValueError:
                random_ids = []
            for i in random_ids:
                if i > len(megaList) or i < 1:
                    print("Some indice is out of bounds...")
                    break

        random_ids = [int(i) for i in random_ids]
        for i in random_ids:
            selected_random.append(megaList[i - 1])

    communityList = selected_friends + selected_random
    communityArtists = []
    communityTracks = []

    # add values of those selected
    amount = math.floor(20 / (len(communityList) + 1))
    for person in communityList:
        top4Artists = db.get_user_top_artists(person)[:amount]
        top4Tracks = db.get_user_top_tracks(person)[:amount]
        communityArtists += top4Artists
        communityTracks += top4Tracks

    # add values of yourself
    communityArtists += topArtistsList[:amount]
    communityTracks += topTracksList[:amount]

    is_public = input(
        'Is this a public or private playlist? (Enter "public" or "private"): '
    )
    if "public" in is_public:
        is_public = True
    else:
        is_public = False

    recSongs = generate_recs(communityArtists, communityTracks)

    playlistLink, playlistId = createAndPopulatePlayList(
        communityList, name, recSongs, is_public, userInfo
    )

    become_friends = input(
        'Do you want to become friends with randoms on this list? (Enter "yes" or "no"): '
    )
    if "yes" in become_friends:
        become_friends = True
    else:
        become_friends = False

    if become_friends:
        db.insert_friends(selected_random)  # update it so selected_random is a tuple

    listFriends = db.get_friends(userInfo)
    db.insert_community_playlist(
        name, playlistId, recSongs, userInfo, listFriends, playlistLink, is_public
    )
    print(
        f"Playlist has been created for all users in the community '{name}'! Visit here: {playlistLink}"
    )


def printNames(listType, percent, count):
    print(f"Users that have a {percent}% music similarity with you:")
    for i in listType:
        print(f"{count}. {i}")
        count += 1
    return count


def delete_playlist(userInfo):
    playlist_name = input("What playlist do you want to delete?: ")

    allPlaylists = sp.current_user_playlists(limit=50, offset=0)
    for playList in allPlaylists["items"]:
        if playlist_name == playList["name"]:
            sp.user_playlist_unfollow(userInfo, playList["id"])
            print(f"Playlist '{playlist_name}' has been deleted!")
            playlists = db.get_your_playlists(playlist_name)

            if playlist_name in playlists:
                db.delete_playlist(userInfo, playlist_name)
            return

    print(f"Playlist '{playlist_name}' can not be found...")


def logout():
    if os.path.exists(f".spotifycache"):
        os.remove(f".spotifycache")


def unregister(userID):

    confirm = input("Are you sure you want to un-register (yes/no)?: ")
    if "y" not in confirm.lower():
        return False

    db.remove_user(userID)
    logout()
    return True


if __name__ == "__main__":
    main()
