import random
import datetime

def create_account(conn, first_name, last_name,username, password):
    curs = conn.cursor()
    date = datetime.datetime.today()
    curs.execute("""
                INSERT INTO users (first_name, last_name, last_access_date, creation_date, username, password)
                VALUES (%s,%s,%s,%s,%s,%s)
                """, (first_name,last_name,date,date,username,password))
    conn.commit()
    
def create_collection(conn,uid,collection_name):
    curs = conn.cursor()
    curs.execute("""
                INSERT INTO collections (uid,collection_name)
                VALUES (%s,%s)
                """, (uid,collection_name))
    conn.commit()

def get_collections(conn, uid):
    curs = conn.cursor()
    curs.execute(
                """SELECT (collection_name),count(video_games.vid),SUM(time_played)FROM video_game_collections
                INNER JOIN collections on video_game_collections.cid = collections.cid
                INNER JOIN user_plays on user_plays.vid = video_game_collections.vid
                INNER JOIN video_games on video_game_collections.vid = video_games.vid
                WHERE collections.uid = %s
                GROUP BY collection_name""", (uid,)
                )
    
    return curs.fetchall()

def add_game_to_collection(conn,uid,cid,vid):
    curs = conn.cursor()
    curs.execute("""
                SELECT * FROM user_platforms
                INNER JOIN video_game_platforms on user_platforms.pid = video_game_platforms.pid
                WHERE uid = %s
                AND vid = %s
                """ , (uid,vid))
    
    if(len(curs.fetchall()) > 0 ):
        curs.execute("""
                    INSERT INTO video_game_collections(cid,vid)
                    VALUES (%s,%s)
                    """ , (cid,vid))
        conn.commit()
    
    else:
        print("You do not own the video game")

def delete_game_from_collection(conn,uid,cid,vid):
    curs = conn.cursor()
    curs.execute("""
                DELETE FROM video_game_collections
                WHERE cid = %s and vid = %s
                """ , (cid, vid))
    conn.commit()
    
def delete_collection(conn,cid):
    curs = conn.cursor()
    curs.execute("""
                DELETE FROM collections
                WHERE cid = %s
                """ , (cid,))
    conn.commit()

def modify_collection_name(conn,cid,new_name):
    curs = conn.cursor()
    curs.execute("""
                UPDATE collections
                SET collection_name = %s
                WHERE cid = %s
                """ , (new_name,cid))
    conn.commit()

def rate_game(conn,uid,vid,rating):
    curs = conn.cursor()
    curs.execute("""
                INSERT INTO user_ratings (uid, vid, star_rating)
                VALUES (%s , %s, %s)
                """, (uid,vid,rating))
    
    conn.commit()

def play_game(conn,uid,vid,time_min):
    curs = conn.cursor()
    curs.execute("""
                SELECT * FROM user_owns
                WHERE uid = %s
                """ , (uid,))
    
    if(len(curs.fetchall()) > 0 ):
        curs.execute("""
                    INSERT INTO user_plays (uid,vid,time_played)
                    VALUES(%s,%s,%s)
                    """ , (uid,vid,time_min))
        
        conn.commit()
    
    else:
        print("You do not own the game")

def play_game_random(conn,uid,time_min):
    curs = conn.cursor()
    curs.execute("""
                SELECT vid FROM user_owns
                WHERE uid = %s
                """ , (uid,))
    video_games = curs.fetchall()
    if(len(video_games) > 0):
        vid = random.choice(video_games)
        curs.execute("""
                    INSERT INTO user_plays (uid,vid,time_played)
                    VALUES(%s,%s,%s)
                    """ , (uid,vid,time_min))
        
        conn.commit()
    
    else:
        print("You do not own any games")


def follow(conn, uid, f_uid):
    curs = conn.cursor()
    
    curs.execute("""
                SELECT * FROM users
                WHERE uid = %s
                """, ( f_uid,))

    if(len(curs.fetchall()) > 0):
        curs.execute("""
                    INSERT INTO user_followers (userid,followerid)
                    VALUES (%s,%s)
                    """ , (f_uid,uid))
        conn.commit()
    
    else:
        print("User does not exist")

def unfollow(conn,uid,f_uid):
    curs = conn.cursor()
    curs.execute("""
                DELETE FROM user_followers
                WHERE userid = %s
                AND followerid = %s 
                """ , (f_uid,uid))
    
    conn.commit()


def search_user(conn,email):
    curs = conn.cursor()
    curs.execute("""
                SELECT username FROM users
                INNER JOIN users_email on users.uid = users_email.uid
                WHERE email = %s
                """ , (email,))
    
    return curs.fetchall()


def search_video_games(conn, name=None, platform=None, release_date=None, developer=None, price=None, genre=None, sort_by=None, sort_order='asc'):
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

    query2 = """
    GROUP BY
        vg.title, p.platform_name, vg.esrb, g.genre_name
    ORDER BY
        vg.title,
        MAX(vgp.price_on_plat),
        MAX(vgp.plat_release_date),
        MAX(ur.star_rating),
        MAX(ur.star_rating) DESC;
        """

    # if name:
    #     query += f"name ILIKE '%{name}%'"
    # if platform:
    #     query += f"platform ILIKE '%{platform}%'"
    # if release_date:
    #     query += f"release_date = '{release_date}'"
    # if developer:
    #     query += f"developer ILIKE '%{developer}%'"
    # if price:
    #     query += f"price = {price}"
    # if genre:
    #     query += f"genre ILIKE '%{genre}%'"
    # if sort_by:
    #     query += f" ORDER BY {sort_by} {sort_order}, name ASC, release_date ASC"
    # else:
    #     query += " ORDER BY name ASC, release_date ASC"
# WHERE
#     vg.title ILIKE 'Minecraft' AND vg.esrb ILIKE 'E'
    if name:
        query += f"WHERE vg.title ILIKE '%{name}%'"
    if platform:
        query += f"WHERE p.platform_name ILIKE '%{platform}%'"
    if release_date:
        query += f"WHERE MAX(vgp.plat_release_date) = '{release_date}'"
    if developer:
        query += f"WHERE c.contributor_name ILIKE '%{developer}%'"
    if price:
        query += f"WHERE MAX(vgp.price_on_plat) = {price}"
    if genre:
        query += f"WHERE g.genre_name ILIKE '%{genre}%'"
    if sort_by:
        query += f" ORDER BY {sort_by} {sort_order}, vg.title ASC, MAX(vgp.plat_release_date) ASC"
    else:
        query += " ORDER BY vg.title ASC, MAX(vgp.plat_release_date) ASC"

    cur.execute(query+query2)
    results = cur.fetchall()

    return results

    