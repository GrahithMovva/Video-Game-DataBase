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
                SELECT * FROM user_owns
                WHERE uid = %s
                """ , (uid,))
    
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
                SELECT * FROM user_owns
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
                    INSERT INTO user_follows (userid,followerid)
                    VALUES (%s,%s)
                    """ , (f_uid,uid))
        conn.commit()
    
    else:
        print("User does not exist")

def unfollow(conn,uid,f_uid):
    curs = conn.cursor()
    curs.execute("""
                DELETE FROM user_follows
                WHERE userid = %s
                AND followerid = %s 
                """ , (f_uid,uid))
    
    conn.commit()