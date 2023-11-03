import random
import datetime


def create_account(conn, username, password, first_name, last_name):
    curs = conn.cursor()
    date = datetime.datetime.today()
    curs.execute("""
                INSERT INTO users (first_name, last_name, last_access_date, creation_date, username, password)
                VALUES (%s,%s,%s,%s,%s,%s)
                """, (first_name, last_name, date, date, username, password))
    conn.commit()


def create_collection(conn, username, collection_name):
    curs = conn.cursor()
    uid = get_uid(curs, username)
    curs.execute("""
                INSERT INTO collections (uid,collection_name)
                VALUES (%s,%s)
                """, (uid, collection_name))
    conn.commit()

"""
SELECT collection_name,SUM(time_played)FROM collections
                FULL OUTER JOIN  video_game_collections on video_game_collections.cid = collections.cid
                FULL OUTER JOIN user_plays on user_plays.vid = video_game_collections.vid
                FULL OUTER JOIN video_games on video_game_collections.vid = video_games.vid
                WHERE collections.uid = 214
                group by collection_name;

SELECT COUNT(vid) from video_game_collections
        INNER JOIN collections on video_game_collections.cid = collections.cid
        WHERE collections.uid = 214
"""

def get_collections(conn, username):
    curs = conn.cursor()
    uid = get_uid(curs, username)
    curs.execute(
                """SELECT collection_name,SUM(time_played)FROM collections
                FULL OUTER JOIN  video_game_collections on video_game_collections.cid = collections.cid
                FULL OUTER JOIN user_plays on user_plays.vid = video_game_collections.vid
                FULL OUTER JOIN video_games on video_game_collections.vid = video_games.vid
                WHERE collections.uid = %s
                group by collection_name""", (uid,)
                )

    first_half = curs.fetchall()
    second_part = []

    for i in range(len(first_half)):
        cid = get_cid_uid(curs,first_half[i][0],uid)
        curs.execute(
                    """SELECT COUNT(vid) from video_game_collections
                    INNER JOIN collections on video_game_collections.cid = collections.cid
                    WHERE collections.uid = %s
                    AND collections.cid = %s""", (uid,cid)
                    )

        second_part.append(curs.fetchall()[0])

    print("collection name   |  Number of video_games in collection  |   Total play time")
    for i in range(len(first_half)):
        number = 20
        first = ('{: >40}'.format(str(first_half[i][1])))
        second = ('{: >20}'.format(str(second_part[i][0])))
        print(first_half[i][0],f'{second}',f'{first}' )
    

def add_game_to_collection(conn, username, collection_name, game):
    curs = conn.cursor()
    uid = get_uid(curs, username)
    vid = get_vid(curs, game)
    if vid == -1:
        print("Game does not exist")
        return
    cid = get_cid(curs, collection_name, username)
    if cid == -1:
        print("Collection does not exist")
        return
    curs.execute("""
                SELECT * FROM user_platforms
                INNER JOIN video_game_platforms on user_platforms.pid = video_game_platforms.pid
                WHERE uid = %s
                AND vid = %s
                """, (uid, vid))
    
    if(len(curs.fetchall()) > 0):
        curs.execute("""
                    INSERT INTO video_game_collections(cid,vid)
                    VALUES (%s,%s)
                    """, (cid, vid))
        conn.commit()
    
    else:
        print("You do not own the platform the video game is based on")


def delete_game_from_collection(conn, username, collection_name, game):
    curs = conn.cursor()
    vid = get_vid(curs, game)
    if vid == -1:
        print("Game does not exist")
        return
    cid = get_cid(curs, collection_name, username)
    if cid == -1:
        print("Collection does not exist")
        return
    curs.execute("""
                DELETE FROM video_game_collections
                WHERE cid = %s and vid = %s
                """, (cid, vid))
    conn.commit()


def delete_collection(conn, username, collection_name):
    curs = conn.cursor()
    cid = get_cid(curs, collection_name, username)
    if cid == -1:
        print("Collection does not exist")
        return
    curs.execute("""
                DELETE FROM collections
                WHERE cid = %s
                """, (cid,))
    conn.commit()


def modify_collection_name(conn, username, collection_name, new_name):
    curs = conn.cursor()
    cid = get_cid(curs, collection_name, username)
    if cid == -1:
        print("Collection does not exist")
        return
    curs.execute("""
                UPDATE collections
                SET collection_name = %s
                WHERE cid = %s
                """, (new_name, cid))
    conn.commit()


def rate_game(conn, username, game, rating):
    curs = conn.cursor()
    uid = get_uid(curs, username)
    vid = get_vid(curs, game)
    if vid == -1:
        print("Game does not exist")
        return
    curs.execute("""
                SELECT COUNT(*) FROM user_plays
                WHERE uid=%s AND vid = %s
                """,(uid,vid))
    
    if(curs.fetchall()[0][0] <= 0):
        print("You need to pla ythis game to rate this game")
        return
    
    curs.execute("""
                SELECT COUNT(*) FROM user_ratings
                WHERE uid = %s AND vid = %s
                """ , (uid,vid))
    
    if(len(curs.fetchall()) > 0):
        curs.execute("""
                    UPDATE user_ratings
                    SET star_rating = %s
                    WHERE uid = %s and vid= %s
                    """ , (rating, uid, vid))

    else:
        curs.execute("""
                INSERT INTO user_ratings (uid, vid, star_rating)
                VALUES (%s , %s, %s)
                """, (uid, vid, rating))
    
    conn.commit()


def play_game(conn, username, game, time_min):
    curs = conn.cursor()
    uid = get_uid(curs, username)
    vid = get_vid(curs, game)
    if vid == -1:
        print("Game does not exist")
        return
    curs.execute("""
                SELECT * FROM user_owns
                WHERE uid = %s AND vid = %s 
                """, (uid,vid))
    
    if(len(curs.fetchall()) > 0):
        curs.execute("""
                    INSERT INTO user_plays (uid,vid,time_played)
                    VALUES(%s,%s,%s)
                    """, (uid, vid, time_min))
        
        conn.commit()
    
    else:
        print("You do not own the game")


def play_game_random(conn, username, time_min):
    curs = conn.cursor()
    uid = get_uid(curs, username)
    curs.execute("""
                SELECT vid FROM user_owns
                WHERE uid = %s
                """, (uid,))
    video_games = curs.fetchall()
    if(len(video_games) > 0):
        vid = random.choice(video_games)
        curs.execute("""
                    INSERT INTO user_plays (uid,vid,time_played)
                    VALUES(%s,%s,%s)
                    """, (uid, vid, time_min))
        
        conn.commit()
    
    else:
        print("You do not own any games")


def follow(conn, username, f_username):
    curs = conn.cursor()
    uid = get_uid(curs, username)
    f_uid = get_uid(curs, f_username)
    curs.execute("""
                SELECT * FROM users
                WHERE uid = %s
                """, (f_uid,))

    if(len(curs.fetchall()) > 0):
        curs.execute("""
                    INSERT INTO user_followers (userid,followerid)
                    VALUES (%s,%s)
                    """, (f_uid, uid))
        conn.commit()
    
    else:
        print("User does not exist")


def unfollow(conn, username, f_username):
    curs = conn.cursor()
    uid = get_uid(curs, username)
    f_uid = get_uid(curs, f_username)

    curs.execute("""
                DELETE FROM user_followers
                WHERE userid = %s
                AND followerid = %s 
                """, (f_uid, uid))
    
    conn.commit()


def search_user(conn, username, email):
    curs = conn.cursor()
    curs.execute("""
                SELECT username FROM users
                INNER JOIN users_email on users.uid = users_email.uid
                WHERE email = %s
                """, (email,))
    for c in curs.fetchall():
        print(c[0])


def search_video_games(conn, username, search_by, searcher, sort_by, sort_order):
    cur = conn.cursor()
    query = """
    SELECT
    vg.title AS video_game_name,
    p.platform_name AS platform,
    string_agg(c.contributor_name, ', ') AS developers,
    string_agg(cp.contributor_name, ', ') AS publisher,
    g.genre_name AS genre,
    MAX(vgp.plat_release_date) AS release_date,
    MAX(vgp.price_on_plat) AS price,
    vg.esrb AS age_rating,
    MAX(ur.star_rating) AS user_rating,
    sum(up.time_played) AS playtime

    FROM
        p320_07.video_games vg
    JOIN
        p320_07.video_game_platforms vgp ON vg.vid = vgp.vid
    JOIN
        p320_07.platforms p ON vgp.pid = p.pid
    LEFT JOIN
        p320_07.video_game_developers vgd ON vg.vid = vgd.vid
    LEFT JOIN
        p320_07.contributors c ON vgd.conid = c.conid
    LEFT JOIN
        p320_07.video_game_publishers vgp_pub ON vg.vid = vgp_pub.vid
    LEFT JOIN
        p320_07.contributors cp ON vgp_pub.conid = cp.conid
    LEFT JOIN
        p320_07.video_game_genre vgg ON vg.vid = vgg.vid
    LEFT JOIN
        p320_07.genre g ON vgg.gid = g.gid
    LEFT JOIN
        p320_07.user_ratings ur ON vg.vid = ur.vid
    INNER JOIN
        p320_07.user_plays up ON vg.vid = up.vid
    """

    if search_by == "name":
        query += f"WHERE vg.title ILIKE '%{searcher}%' "
    elif search_by == "platform":
        query += f"WHERE p.platform_name ILIKE '%{searcher}%' "
    elif search_by == "release_date":
        query += f"WHERE vgp.plat_release_date = '{searcher}' "
    elif search_by == "developer":
        query += f"WHERE c.contributor_name ILIKE '%{searcher}%' "
    elif search_by == "price":
        query += f"WHERE vgp.price_on_plat = '{searcher}' "
    elif search_by == "genre":
        query += f"WHERE g.genre_name ILIKE '%{searcher}%' "
    else:
        print("Invalid search by term")
        return
    query += "GROUP BY vg.title, p.platform_name, vg.esrb, g.genre_name "
    if sort_by == "name":
        query += "ORDER BY vg.title "
    elif sort_by == "price":
        query += "ORDER BY price "
    elif sort_by == "genre":
        query += "ORDER BY genre "
    elif sort_by == "year":
        query += "ORDER BY release_date "
    else:
        print("Invalid order by term")
        return

    if sort_order != "asc" and sort_order != "desc":
        print("Invalid sort order")
        return
    query += f"{sort_order}, vg.title ASC, MAX(vgp.plat_release_date) ASC"
    cur.execute(query)
    for c in cur.fetchall():
        print(c)


def login(conn, username, password):
    cursor = conn.cursor()
    date = datetime.datetime.today()
    uid = get_uid(cursor, username)
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM users
        WHERE uid = {uid}
        AND password = '{password}'""")
    if cursor.fetchall()[0][0] == 1:
        cursor.execute("""
                       UPDATE users
                       SET last_access_date = %s
                       WHERE uid = %s
                       """ , (date,uid))
        return uid
    return -1


def get_uid(cursor, username):
    cursor.execute(f"""
        SELECT uid
        FROM users
        WHERE username ='{username}'""")
    result = cursor.fetchall()
    if len(result) != 1:
        return -1
    return result[0][0]


def get_cid(cursor, collection_name, username):
    cursor.execute(f"""
        SELECT cid
        FROM collections
        WHERE collection_name = '{collection_name}'
        AND uid = {get_uid(cursor, username)}""")
    result = cursor.fetchall()
    if len(result) != 1:
        return -1
    return result[0][0]


def get_vid(cursor, video_game):
    cursor.execute(f"""
         SELECT vid FROM video_games
         WHERE title = '{video_game}'""")
    result = cursor.fetchall()
    if len(result) != 1:
        return -1
    return result[0][0]

def get_cid_uid(cursor, collection_name, uid):
    cursor.execute(f"""
        SELECT cid
        FROM collections
        WHERE collection_name = '{collection_name}'
        AND uid = {uid}""")
    
    result = cursor.fetchall()
    return result[0][0]

def show_profilr(curs,uid):

    curs.execute("""
                SELECT COUNT(*) FROM collections
                WHERE uid = %s
                """ , (uid,))
    
    number_of_collections = curs.fetchall()[0][0]

    curs.execute("""
                SELECT COUNT(*) FROM user_followers
                WHERE uid = %s
                """ , (uid,))
    
    number_of_followers = curs.fetchall()[0][0]

    curs.execute("""
                SELECT COUNT(*) FROM user_followers
                WHERE followerid = %s
                """ , (uid,))
    
    follows = curs.fetchall()[0][0]

    curs.execute("""
                SELECT title from video_games
                INNER JOIN user_ratings on user_ratings.vid = video_games.vid
                WHERE uid = %s
                ORDER BY star_rating DESC
                LIMIT 10
                """,(uid,))
    
    top_games = curs.fetchall()

    