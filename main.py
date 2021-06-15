import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time

auth = SpotifyOAuth('5a1e2b28b8a043b99d5a19ffb4d8a216',
                    'f31645c086aa4809a5fbaed43ef7ac30', "http://localhost:8000/callback", cache_path=".spotifycache", scope="user-library-read user-top-read playlist-modify-public")

token = auth.get_cached_token()['access_token']
if token is None:
    sp = spotipy.Spotify(auth_manager=auth)
else:
    sp = spotipy.Spotify(token, auth_manager=auth)


def main():
    print("Welcome to SpotiStat, an application used to connect your music taste with others around the globe!")

    print("Requesting login info now if not stored, come back to program when done...")
    time.sleep(2)
    userInfo = sp.current_user()['id']
    print(userInfo)
    topTracksList = topTracks()
    if len(topTracksList) < 20:
        print("Listen to more songs and then come back to our application :)")
        return
    topArtistsList = topArtists()
    topValues = analyzeVals(topTracksList) #use these values to generate similarity between users
    # if not db.checkUser(userInfo):
    #     db.addUser(userInfo)
    # db.addTopTracks(userInfo, topTracksList[:2])
    # db.addTopArtists(userInfo, topArtistsList[:2])
    # db.addTopValues(userInfo, topValues)

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
            print("    -gcp, --getCommunityPlaylist  gets the usernames of people in your community and the songs in the respective playlist")
            print("    -gyc, --getYourCommunities    gets the names of all your communities")
            print("    -dp, --deletePlaylist         deletes a playlist for you, not only from application, but spotify")
            print("    -ur, --un-register            un-registers and deletes your info from our application")

        elif command == "-gf" or command == "--getFriends":
            get_friends(userInfo)
        elif command == "-ff" or command == "--findFriends":
            findFriends(topValues, userInfo)
        elif command == "-cop" or command == "--createOwnPlaylist":
            name = create_own_playlist([userInfo], topArtistsList, topTracksList)
            print(f"Your own playlist '{name}' has been created! Check your Spotify account to confirm.")
        elif command == "-cgp" or command == "--createGroupPlaylist":
            create_group_playlist(topValues, userInfo, topArtistsList, topTracksList)
        elif command == "-gcp" or command == "--getCommunityPlaylist":
            get_community_playlist(userInfo)
        elif command == "-gyc" or command == "--getYourCommunities":
            get_your_communities(userInfo)        
        elif command == "-dp" or command == "--deletePlaylist":
            delete_playlist(userInfo)
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


def get_friends(userInfo):
    # friends = db.get_friends(userInfo) 
    for friend in friends:
        print(friend)
    return friends


def findFriends(topValues, userInfo):
    def withinX(percent): #the way it currently works is that as long as it is within a percent threshold for one category, they are included, might change this
        curVal = topValues[key]
        return curVal * (1 + percent) >= val and val <= curVal * (1 - percent)

    #users = db.get_users_except_friends_and_you(userInfo) <- and remove yourself here, as well as all your friends
    users = ['belle', 'evan', 'glen', 'caroline']
    top99 = []
    top90 = []
    top75 = []
    top50 = []
    for user in users:
        #userAverages = db.get_averages(user)
        for key, val in enumerate(userAverages):
            if withinX(.01):
                top99.add(user)
                break
            elif withinX(.1):
                top90.add(user)
                break
            elif withinX(.25):
                top75.add(user)
                break
            elif withinX(.5):
                top50.add(user)
                break

    return top99, top90, top75, top50


def get_your_communities(userInfo):
    # db.get_your_communities(userInfo)
    return


def get_community_playlist(userInfo):
    # playlist_name = input("What community playlist do you want to search for?: ")
    # playlist = db.get_playlist(userInfo, playlist_name), also retrieve the link for the playlist if any if user is in private, or any if public
    # print(playlist)
    return


def create_own_playlist(userInfo, topArtistsList, topTracksList):
    songsForRec = generate_recs(topArtistsList, topTracksList)

    name = input("Enter a name for this playlist: ")
    
    createAndPopulatePlayList(userInfo, name, songsForRec, True)
    
    return name

def generate_recs(topArtistsList, topTracksList):
    listTracks = []
    print("Generating recommendations...")
    for i in range(2, 21, 2):
        listTracks.append(sp.recommendations(seed_tracks=topTracksList[i-2:i], seed_artists=topArtistsList[i-2:i], limit=3))
    songsForRec = list(set(extractIDFromTracks(listTracks)))
    return songsForRec

def createAndPopulatePlayList(userInfo, name, songsForRec, publicVal):
    for user in userInfo:
        # should it be collaborative? personally i think yes
        val = sp.user_playlist_create(user, name, public=publicVal, collaborative=False, description='')
        sp.user_playlist_add_tracks(user, val['id'], songsForRec, position=None)
    return


def create_group_playlist(topValues, userInfo, topArtistsList, topTracksList):

    #have to figure out what happens if you have less than 3 friends, or maybe less than 7 users in table, also need to do all the error checking if user types bad inputs
    name = input("Enter a name for this community playlist: ")

    friends = get_friends() # <= print out this list in the get_friends method
    user_ids = input(
        "Select 3 of your friends to base this playlist on (indices with spaces): ")
    user_ids = user_ids.split()
    user_ids = [int(i) for i in user_ids]
    selected_friends = []
    for i in user_ids:
        selected_friends.append(friends[i-1])
    
    top99, top90, top75, top50 = findFriends(topValues)   
     # show 3 friends, 6 random + 1 yourself, : 10 users and then something public about their listening history, enter indices of users you want to make playlist with
     # so maybe get rid of findFriends method and instead show blob about all users? or maybe only show blob of top similarity users, idk blobs for everyone seems like alot
    count = 1
    count = printNames(top99, 99, count)
    count = printNames(top90, 90, count)
    count = printNames(top75, 75, count)
    count = printNames(top50, 50, count)

    megaList = top99 + top90 + top75 + top50
    random_ids = input(
        "Select 6 random users to base this playlist on (indices with spaces): ")
    random_ids = random_ids.split()
    random_ids = [int(i) for i in random_ids]
    selected_random = []
    for i in random_ids:
        selected_random.append(megaList[i-1])


    communityList = selected_friends + selected_random
    communityArtists = []
    communityTracks = []

    #add values of those selected
    for person in communityList: 
        #top2Artists = db.get_top_artists(person)[:2]
        #top2Tracks = db.get_top_tracks(person)[:2]
        communityArtists += top2Artists
        communityTracks += top2Tracks

    #add values of yourself
    communityArtists += topArtistsList[:2]
    communityTracks += topTracksList[:2]

    communityList.append(userInfo) #add yourself to community list


    is_public = input(
        "Is this a public or private playlist? (Enter \"public\" or \"private\"): ")

    recSongs = generate_recs(communityArtists, communityTracks)

    createAndPopulatePlayList(communityList, name, recSongs, is_public)

    # db.insert_playlist(recommendations, is_public), add value to database
    #also store the link of playlist in database
    print(f"Playlist has been created for all users in the community '{name}'!")

def printNames(listType, percent, count):
    print(f"Users that have a {percent}% music similarity with you:")
    for i in listType:
        print(f"{count}. {i}")
        count += 1
    return count

def delete_playlist(userInfo):
    playlist_name = input("What playlist do you want to delete?: ")

    # db.delete_playlist(userInfo, playlist_name)

    allPlaylists = sp.current_user_playlists(limit=50, offset=0)
    for playList in allPlaylists['items']:
        if playlist_name == playList['name']:
            sp.user_playlist_unfollow(userInfo, playList['id'])
            print(f"Playlist '{playlist_name}' has been deleted!")
            return
    print(f"Playlist '{playlist_name}' can not be found...")


def unregister(userID):
    
    confirm = input("Are you sure you want to un-register (yes/no)?: ")
    if "y" not in confirm.lower():
        return False

    # db.remove_user_info(userID)
    if (os.path.exists(f".spotifycache")):
        os.remove(f".spotifycache")
    return True


if __name__ == '__main__':
    main()
