import mysql.connector
from mysql.connector import errorcode


class group_recommendations_db:
    def __init__(self):

        # Insert your own parameters
        configs = {
            "user": "ycf3tf27xqesjn36",
            "password": "asael031kb97unup",
            "host": "l0ebsc9jituxzmts.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
            "database": "okuegiqutb19vini",
            "raise_on_warnings": True,
        }
        try:
            self.db = mysql.connector.connect(**configs)
            self.cursor = self.db.cursor(buffered=True)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def get_user_top_tracks(self, s_user_id):
        """
        Retrieves a given user's top tracks.

        Args:
            s_user_id (int): a user's spotify id

        Returns:
            songs (list): user's top tracks represented as each track's spotify id
                            returns empty list if user doesn't exist.
        """

        query = """
        select tt.song_spotify_id
        from top_track tt
        where tt.user_spotify_id = %s
        order by tt.rank;
        """
        self.cursor.execute(query, (s_user_id,))

        songs = []
        for (spotify_id,) in self.cursor:
            songs.append(spotify_id)
        return songs

    def users_in_playlist(self, playlist_id):
        """
        Returns a list of users that have access to a specific playlist.

        Args:
            playlist_id (int)

        Returns:
            users (list): spotify id's of users that have access to a playlist.
                            returns empty list if playlist doesn't exist.
        """

        query = """
        select up.user_spotify_id
        from user_has_playlist up
        where up.playlist_spotify_id = %s ;
        """
        self.cursor.execute(query, (playlist_id,))

        users = []
        for (spotify_id,) in self.cursor:
            users.append(spotify_id)
        return users

    def get_friends(self, s_user_id):
        """
        Returns a list of the Spotify IDs of a user's friends. List is empty if user doesn't exist.
        """
        query = """
        select distinct u.spotify_id
        from user u
        where u.spotify_id in (
        select f.user_spotify_id1
        from friends f
        where f.user_spotify_id2 = %s )
        or u.spotify_id in (
        select f.user_spotify_id2
        from friends f
        where f.user_spotify_id1 = %s );
        """

        self.cursor.execute(query, (s_user_id, s_user_id))

        friends = []
        for (id,) in self.cursor:
            friends.append(id)

        return friends

    def get_song(self, song_spotify_id):
        """
        Takes a song's Spotify ID and returns the song's attribtues
        """
        query = """
        select *
        from song s
        where s.spotify_id = %s ;
        """
        self.cursor.execute(query, (song_spotify_id,))
        result = self.cursor.fetchone()
        return result

    def get_artist(self, artist_spotify_id):
        """
        Takes an artists's Spotify ID and returns the artist
        """
        query = """
        select *
        from artist a
        where a.spotify_id = %s ;
        """
        self.cursor.execute(query, (artist_spotify_id,))
        result = self.cursor.fetchone()
        return result

    def update_user_top_tracks(self, s_user_id, new_top_tracks):
        """
        Updates a user's top tracks by deleting all of that user's
        previous entries from the top_track table and inserting
        all new records.

        Args:
            s_user_id (int): user's Spotify ID
            new_top_tracks (list of tuples): [(rank, song_id), ....]
        """

        # delete relevant tracks
        query = "delete from top_track where top_track.user_spotify_id = %s ;"
        self.cursor.execute(query, (s_user_id,))
        self.db.commit()

        self.insert_top_tracks(s_user_id, new_top_tracks)
        self.db.commit()

    def get_users_except_friends_and_you(self, user_id, friends_list):
        """
        Args:
            user_id (string): spotify user id
            friends_list (list of strings): list of spotify id's of users that are friends with you
        Returns:
            users_list (list of strings): returns list of spotify id's
        """
        # query = (
        #     """
        # select u.spotify_id
        # from user u where u.spotify_id not in ( \"
        # """
        #     + user_id
        #     + '", '
        #     + ", ".join(f'"{friend}"' for friend in friends_list)
        #     + ");"
        # )
        # print(query)

        if len(friends_list) == 0:
            query = (
                """
            select u.spotify_id
            from user u where u.spotify_id != \""""
                + user_id
                + '";'
            )
        else:
            query = (
                """
            select u.spotify_id
            from user u where u.spotify_id not in
            """
                + '( "'
                + user_id
                + '", '
                + ", ".join(f'"{friend}"' for friend in friends_list)
                + ");"
            )
        self.cursor.execute(query)

        users_list = []

        for (spotify_id,) in self.cursor:
            users_list.append(spotify_id)
        return users_list

    def get_user_top_artists(self, s_user_id):
        """
        Retrieves a given user's top tracks.

        Args:
            s_user_id (int): a user's spotify id

        Returns:
            songs (list): user's top artists represented as each track's spotify id
        """

        query = """
        select ta.artist_spotify_id
        from top_artist ta
        where ta.user_spotify_id = %s
        order by ta.rank;
        """
        self.cursor.execute(query, (s_user_id,))

        songs = []
        for (spotify_id,) in self.cursor:
            songs.append(spotify_id)
        return songs

    def getPlaylistLink(self, playlist_id):
        """
        Retrieves the link of the specified playlist.

        Args:
            playlist_id (string)

        Returns:
            playlist_link (string)
        """

        query = """
        select p.link
        from playlist p
        where p.spotify_id = %s;
        """

        self.cursor.execute(query, (playlist_id,))

        for (link,) in self.cursor:
            return link

    def is_public_list(self, playlist_name):
        """
        Retrieves the link of the specified playlist.

        Args:
            playlist_name (string)

        Returns:
            public (boolean)
        """

        query = """
        select p.public
        from playlist p
        where p.name = %s;
        """

        self.cursor.execute(query, (playlist_name,))

        for (public,) in self.cursor:
            return public == "1"

    def get_your_playlists(self, user_id):
        """
        Args:
            user_id (string): Spotify ID
        Returns:
            playlists (list of strings): list of playlist ids
        """

        query = """
        select p.spotify_id
        from user_has_playlist up join playlist p on (up.playlist_spotify_id = p.spotify_id)
        where up.user_spotify_id = %s ;
        """
        self.cursor.execute(query, (user_id,))

        playlists = []

        for (spotify_id,) in self.cursor:
            playlists.append(spotify_id)

        return playlists

    def update_user_top_artists(self, s_user_id, new_top_artists):
        """
        Updates a user's top artists by deleting all of that user's
        previous entries from the top_artists table and inserting
        all new records.

        Args:
            s_user_id (int): user's Spotify ID
            new_top_artists (list of tuples): [(rank, artist_id), ....]
        """

        # delete relevant artists

        query = "delete from top_artist where top_artist.user_spotify_id = %s ;"
        self.cursor.execute(query, (s_user_id,))
        self.db.commit()

        self.insert_top_artists(s_user_id, new_top_artists)
        self.db.commit()

    def insert(self, query):
        self.cursor.execute(query)
        self.db.commit()

    def insert_many(self, query, data):
        self.cursor.executemany(query, data)
        self.db.commit()

    def insert_user(self, spotify_id):
        sql = f'INSERT INTO user VALUES ("{spotify_id}")'
        self.insert(sql)

    def user_id_exists(self, spotify_id):
        query = f' SELECT EXISTS(SELECT * FROM user WHERE spotify_id = "{spotify_id}")'
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] == 1

    def insert_friends(self, friends):
        # friends format: [(user_spotify_id1, user-spotify_id1), ....]
        sql = f"INSERT INTO friends VALUES (%s, %s)"
        self.insert_many(sql, friends)

    # insert_friends([(1, 6)])

    def insert_community_playlist(
        self,
        playlist_name,
        spotify_playlist_id,
        song_spotify_ids,
        user_spotify_id,
        friend_user_ids,
        link,
        is_public,
    ):
        # song_ids format: ["1", "2", "3", ...]
        # user_ids format: ["1", "2", "3", ...]
        inset_playlist = f'INSERT INTO playlist VALUES ("{spotify_playlist_id}", "{playlist_name}", "{link}", {is_public})'
        self.insert(inset_playlist)

        song_ids = [(s,) for s in song_spotify_ids]
        insert_songs = (
            f'INSERT INTO playlist_has_song VALUES ("{spotify_playlist_id}", %s)'
        )
        self.insert_many(insert_songs, song_ids)

        user_ids = [(user_spotify_id,)]
        if is_public:
            user_ids += [(u,) for u in friend_user_ids]
        insert_users = (
            f'INSERT INTO user_has_playlist VALUES (%s, "{spotify_playlist_id}")'
        )
        self.insert_many(insert_users, user_ids)

    # insert_community_playlist("test2", [1, 2], [1, 6], true)

    def insert_top_tracks(self, user_spotify_id, tracks):
        # tracks format: [(rank, song_id), ....]

        sql = f'INSERT INTO top_track VALUES ( %s, "{user_spotify_id}", %s)'
        self.insert_many(sql, tracks)

    def insert_artist(self, artist_spotify_id):
        if self.get_artist(artist_spotify_id):
            # artist already exists
            return

        sql = f'INSERT INTO artist VALUES ("{artist_spotify_id}")'
        self.insert(sql)

    def insert_top_artists(self, user_spotify_id, tracks):
        # artist format: [(rank, spotify_artist_id), ....]
        sql = f'INSERT INTO top_artist (user_spotify_id, top_artist.rank, artist_spotify_id) VALUES ("{user_spotify_id}", %s, %s)'
        self.insert_many(sql, tracks)

    # insert_top_tracks(1, [(1,2)])

    def insert_song(self, spotify_id):

        if self.get_song(spotify_id):
            # song already exists
            return

        sql = f"INSERT INTO song  VALUES (" f'"{spotify_id}"' f")"

        self.insert(sql)

    def delete_playlist(self, spotify_playlist_id):
        delete_songs = f'DELETE FROM playlist_has_song WHERE playlist_spotify_id = "{spotify_playlist_id}"'
        delete_user_access = f'DELETE FROM user_has_playlist WHERE playlist_spotify_id = "{spotify_playlist_id}"'
        delete_playlist = (
            f'DELETE FROM playlist WHERE spotify_id = "{spotify_playlist_id}"'
        )
        self.cursor.execute(delete_songs)
        self.cursor.execute(delete_user_access)
        self.cursor.execute(delete_playlist)
        self.db.commit()

    def remove_user(self, spotify_user_id):
        delete_playlists = (
            f'DELETE FROM user_has_playlist WHERE user_spotify_id = "{spotify_user_id}"'
        )
        delete_top_track = (
            f'DELETE FROM top_track WHERE user_spotify_id = "{spotify_user_id}"'
        )
        delete_top_artist = (
            f'DELETE FROM top_artist WHERE user_spotify_id = "{spotify_user_id}"'
        )
        delete_friends = f'DELETE FROM friends WHERE user_spotify_id1 = "{spotify_user_id}" or  user_spotify_id2 = "{spotify_user_id}"'
        delete_user = f'DELETE FROM user WHERE spotify_id = "{spotify_user_id}"'
        self.cursor.execute(delete_playlists)
        self.cursor.execute(delete_top_track)
        self.cursor.execute(delete_top_artist)
        self.cursor.execute(delete_friends)
        self.cursor.execute(delete_user)
        self.db.commit()

    def close_db(self):
        self.cursor.close()
        self.db.close()
