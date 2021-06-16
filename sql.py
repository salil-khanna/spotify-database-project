import mysql.connector
from mysql.connector import errorcode

class group_recommendations_db():
    def __init__(self):
        configs = {
            'user': 'root',
            'password': 'PASS',
            'database': 'group_recommendations',
            'raise_on_warnings': True
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


    def query_gets_attrs(self, query, query_args):
        """
        Helper method that executes a query. Hardcodes column values, so should only be used if the
        resulting SQL table has the column names of the Spotify song attributes and the table
        only has one row lol

        Args:
            query (string)
            query_args (tuple): arguments to format the SQL query properly

        Returns:
            avg_attrs (dictionary): dictionary where key is the song attribute and value is from the query
                                    dictionary values populated with 0 if query returns nothing.
        """
        self.cursor.execute(query, query_args)

        avg_attrs = {
            'accousticness': 0,
            'danceability': 0,
            'duration': 0,
            'energy': 0,
            'instrumentalness': 0,
            'key': 0,
            'loudness': 0,
            'mode': 0,
            'popularity': 0,
            'speechiness': 0,
            'tempo': 0,
            'time_signature': 0,
            'valence': 0
        }

        for (accousticness, danceability, duration, energy, instrumentalness,
             key, loudness, mode, popularity, speechiness, tempo, time_signature,
             valence) in self.cursor:

            if accousticness is None:
                # no songs were returned in this query -- no idea why it returns a NoneType row instead
                # of just an empty table
                return avg_attrs

            avg_attrs['accousticness'] = int(accousticness)
            avg_attrs['danceability'] = int(danceability)
            avg_attrs['duration'] = int(duration)
            avg_attrs['energy'] = int(energy)
            avg_attrs['instrumentalness'] = int(instrumentalness)
            avg_attrs['key'] = int(key)
            avg_attrs['loudness'] = int(loudness)
            avg_attrs['mode'] = int(mode)
            avg_attrs['popularity'] = int(popularity)
            avg_attrs['speechiness'] = int(speechiness)
            avg_attrs['tempo'] = int(tempo)
            avg_attrs['time_signature'] = int(time_signature)
            avg_attrs['valence'] = int(valence)
        return avg_attrs

    def get_user_top_tracks(self, s_user_id):
        """
        Retrieves a given user's top tracks.

        Args:
            s_user_id (int): a user's spotify id

        Returns:
            songs (list): user's top tracks represented as each track's spotify id
                            returns empty list if user doesn't exist.
        """

        query = ("""
        select s.spotify_id
        from top_track t join user u using (user_id)
        join song s using (song_id)
        where u.spotify_id = %s ;
        """)
        self.cursor.execute(query, (s_user_id,))

        songs = []
        for (spotify_id,) in self.cursor:
            songs.append(int(spotify_id))
        return songs

    def get_user_song_attr(self, s_user_id):
        """
        Retrieves a given user's average track attributes in the form of a dictionary.

        Args:
            s_user_id (int): a user's spotify id

        Returns:
            avg_attrs (dictionary): dictionary where key is the song attribute and value is the user's average
                                    returns dictionary where values are 0 if user doesn't exist.
        """

        query = ("""
        select avg(s.accousticness) accousticness,
            avg(s.danceability) danceability,
            avg(s.duration) duration,
            avg(s.energy) energy,
            avg(s.instrumentalness) instrumentalness,
            avg(s.key) `key`,
            avg(s.loudness) loudness,
            avg(s.mode) `mode`,
            avg(s.popularity) popularity,
            avg(s.speechiness) speechiness,
            avg(s.tempo) tempo,
            avg(s.time_signature) time_signature,
            avg(s.valence) valence
        from top_track t join song s using (song_id)
        join user u using (user_id)
        where u.spotify_id = %s ;
        """)
        return self.query_gets_attrs(query, (s_user_id,))

    def playlist_users_avg(self, playlist_id):
        """
        Returns the song attribute averages of all the users in a playlist.

        Args:
            playlist_id (int)

        Returns:
            avg_attrs (dictionary): dictionary where key is the song attribute and value is the user's average
                                    returns dictionary populated with 0's if playlist doesn't exist.
        """

        query = """
        select avg(pu.accousticness) accousticness, STDDEV(pu.accousticness),
            avg(pu.danceability) danceability,
            avg(pu.duration) duration,
            avg(pu.energy) energy,
            avg(pu.instrumentalness) instrumentalness,
            avg(pu.key) `key`,
            avg(pu.loudness) loudness,
            avg(pu.mode) `mode`,
            avg(pu.popularity) popularity,
            avg(pu.speechiness) speechiness,
            avg(pu.tempo) tempo,
            avg(pu.time_signature) time_signature,
            avg(pu.valence) valence
        from 
            (select t.user_id,
                avg(s.accousticness) accousticness,
                avg(s.danceability) danceability,
                avg(s.duration) duration,
                avg(s.energy) energy,
                avg(s.instrumentalness) instrumentalness,
                avg(s.key) `key`,
                avg(s.loudness) loudness,
                avg(s.mode) `mode`,
                avg(s.popularity) popularity,
                avg(s.speechiness) speechiness,
                avg(s.tempo) tempo,
                avg(s.time_signature) time_signature,
                avg(s.valence) valence
            from user_has_playlist up join top_track t on (up.user_id = t.user_id)
            join song s using (song_id)
            where up.playlist_id = %s
            group by t.user_id) as pu;
        """
        return self.query_gets_attrs(query, (playlist_id,))

    def users_in_playlist(self, playlist_id):
        """
        Returns a list of users that have access to a specific playlist.

        Args:
            playlist_id (int)

        Returns:
            users (list): spotify id's of users that have access to a playlist.
                            returns empty list if playlist doesn't exist.
        """

        query = ("""
        select u.spotify_id
        from user_has_playlist up join user u on (up.user_id = u.user_id)
        where playlist_id = %s ;
        """)
        self.cursor.execute(query, (playlist_id,))

        users = []
        for (spotify_id,) in self.cursor:
            users.append(int(spotify_id))
        return users

    def get_friends(self, s_user_id):
        """
        Returns a list of the Spotify IDs of a user's friends. List is empty if user doesn't exist.
        """
        query = ("""
        select 
            u.spotify_id id
            from friends f join user u on (f.user2_id = u.user_id)
        where f.user1_id in 
        (
            select user.user_id
            from user
            where user.spotify_id = %s );
        """)

        self.cursor.execute(query, (s_user_id,))

        friends = []
        for (id,) in self.cursor:
            friends.append(int(id))

        return friends

    def get_user_id_from_spotify_id(self, s_user_id):
        """
        Takes a user's Spotify ID and returns the user_id saved in the user table. Returns None if
        user doesn't exist.
        """
        query = ("""
        select u.user_id
        from user u
        where u.spotify_id = %s ;
        """)
        self.cursor.execute(query, (s_user_id,))
        for (user_id,) in self.cursor:
            return int(user_id)

    def get_song_id(self, spotify_id):
        """
        Takes a song's Spotify ID and returns the corresponding song_id from the song table.
        Returns None if song doesn't exist in database.
        """
        query = ("""
        select s.song_id
        from song s
        where s.spotify_id = %s ;
        """)
        self.cursor.execute(query, (spotify_id,))
        for (song_id,) in self.cursor:
            return int(song_id)

    def update_user_top_tracks(self, s_user_id, new_top_tracks):
        """
        Updates a user's top tracks by deleting all of that user's
        previous entries from the top_track table and inserting
        all new records.

        Args:
            s_user_id (int): user's Spotify ID
            new_top_tracks (list of tuples): [(song_id, rank), ....]
        """

        # delete relevant tracks
        query = ("delete from top_track where top_track.user_id = %s ;")
        self.cursor.execute(query, (s_user_id,))

        user_id = self.get_user_id_from_spotify_id(s_user_id)
        self.insert_top_tracks(user_id, new_top_tracks)

    def insert(self, query):
        self.cursor.execute(query)
        self.db.commit()


    def insert_many(self, query, data):
        self.cursor.executemany(query, data)
        self.db.commit()


    def insert_user(self, spotify_id):
        sql = f"INSERT INTO user (spotify_id) VALUES ({spotify_id})"
        self.insert(sql)


    def insert_friends(self, friends):
        # friends format: [(user_id1, user_id2), ....]
        sql = f"INSERT INTO friends VALUES (%s, %s)"
        self.insert_many(sql, friends)


    # insert_friends([(1, 6)])

    def insert_community_playlist(self, name, link, song_ids, user_id, friend_user_ids, is_public):
        # song_ids format: [1, 2, 3, ...]
        # user_ids format: [1, 2, 3, ...]
        inset_playlist = f'INSERT INTO playlist (name, link) VALUES ("{name}", "{link}")'
        self.insert(inset_playlist)

        id = self.cursor.lastrowid

        song_ids = [(s,) for s in song_ids]
        insert_songs = f'INSERT INTO playlist_has_song VALUES ({id}, %s)'
        self.insert_many(insert_songs, song_ids)

        user_ids = [(user_id,)]
        if is_public:
            user_ids += [(u,) for u in friend_user_ids]
        insert_users = f'INSERT INTO user_has_playlist VALUES ({id}, %s)'
        print(insert_users, user_ids)
        self.insert_many(insert_users, user_ids)


    # insert_community_playlist("test2", [1, 2], [1, 6], true)


    def insert_top_tracks(self, user_id, tracks):
        # tracks format: [(song_id, rank), ....]
        sql = f"INSERT INTO top_track VALUES ({user_id}, %s, %s)"
        self.insert_many(sql, tracks)


    # insert_top_tracks(1, [(1,2)])


    def insert_song(self, name,
                    spotify_id,
                    accousticness,
                    danceability,
                    duration,
                    energy,
                    instrumentalness,
                    key,
                    liveness,
                    loudness,
                    mode,
                    popularity,
                    speechiness,
                    tempo,
                    time_signature,
                    valence):
        sql = f'INSERT INTO song (' \
              f'song.name,' \
              f'spotify_id, ' \
              f'accousticness,' \
              f'danceability, ' \
              f'duration, ' \
              f'energy, ' \
              f'instrumentalness, ' \
              f'song.key, ' \
              f'liveness, ' \
              f'loudness, ' \
              f'mode, ' \
              f'popularity, ' \
              f'speechiness, ' \
              f'tempo, ' \
              f'time_signature, ' \
              f'valence' \
              f') VALUES (' \
              f'"{name}",' \
              f'"{spotify_id}",' \
              f'{accousticness},' \
              f'{danceability},' \
              f'{duration},' \
              f'{energy},' \
              f'{instrumentalness},' \
              f'{key},' \
              f'{liveness},' \
              f'{loudness},' \
              f'{mode},' \
              f'{popularity},' \
              f'{speechiness},' \
              f'{tempo},' \
              f'{time_signature},' \
              f'{valence}' \
              f')'
        self.insert(sql)

    def delete_playlist(self, user_spotify_id, playlist_name):
        playlist_id_query = f"SELECT distinct playlist_id " \
                            f"FROM playlist " \
                            f"join user_has_playlist " \
                            f"join user " \
                            f"where playlist_id = playlist_id " \
                            f"and name = \"{playlist_name}\" " \
                            f"and spotify_id = \"{user_spotify_id}\";"
        self.cursor.execute(playlist_id_query)
        result = self.cursor.fetchone()
        playlist_id = result[0]
        delete_songs = f"DELETE FROM playlist_has_song WHERE playlist_id = {playlist_id}"
        delete_user_access = f"DELETE FROM user_has_playlist WHERE playlist_id = {playlist_id}"
        delete_playlist = f"DELETE FROM playlist WHERE playlist_id = {playlist_id}"
        print(delete_songs)
        self.cursor.execute(delete_songs)
        self.cursor.execute(delete_user_access)
        self.cursor.execute(delete_playlist)
        self.db.commit()

    def remove_user(self, spotify_id):
        user_id_query = f"SELECT user_id from user where spotify_id = \"{spotify_id}\""
        self.cursor.execute(user_id_query)
        result = self.cursor.fetchone()
        user_id = result[0]
        delete_playlists = f"DELETE FROM user_has_playlist WHERE user_id = {user_id}"
        delete_top_track = f"DELETE FROM top_track WHERE user_id = {user_id}"
        delete_friends = f"DELETE FROM friends WHERE user1_id = {user_id} or  user2_id = {user_id}"
        delete_user = f"DELETE FROM user WHERE user_id = {user_id}"
        self.cursor.execute(delete_playlists)
        self.cursor.execute(delete_top_track)
        self.cursor.execute(delete_friends)
        self.cursor.execute(delete_user)
        self.db.commit()


    def close_db(self):
        self.db.close()