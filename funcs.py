
import datetime


def create_account(curs, first_name, last_name,username, password):
    date = datetime.datetime.today()
    curs.execute("""
                INSERT INTO users (first_name, last_name, last_access_date, creation_date, username, password)
                VALUES (%s,%s,%s,%s,%s,%s)
                """, (first_name,last_name,date,date,username,password))
    
def create_collection(curs,uid,collection_name):
    curs.execute("""
                INSERT INTO collections (uid,collection_name)
                VALUES (%s,%s)
                """, (uid,collection_name))


def get_collections(curs, uid):
    curs.execute(
                """SELECT (collection_name),count(video_games.vid),SUM(time_played)FROM video_game_collections
                INNER JOIN collections on video_game_collections.cid = collections.cid
                INNER JOIN user_plays on user_plays.vid = video_game_collections.vid
                INNER JOIN video_games on video_game_collections.vid = video_games.vid
                WHERE collections.uid = %s
                GROUP BY collection_name""", uid
                )
    
    return curs.fetchall()

def add_game_to_collection(curs,cid, vid):
    curs.execute()

