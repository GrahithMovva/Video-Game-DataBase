import psycopg2
from sshtunnel import SSHTunnelForwarder
import json
import re
import funcs

credentials = json.load(open("credentials.json"))
USERNAME = credentials["username"]
PASSWORD = credentials["password"]
DBNAME = "p320_07"
UID = -1
USER = None


def login(conn, username, password):
    uid = funcs.login(conn, username, password)
    if uid != -1:
        globals()["UID"] = uid
        globals()["USER"] = username
        print("Logged in as", username)
    else:
        print("Incorrect username or password")


def logout(*args):
    globals()["UID"] = -1
    globals()["USER"] = None
    print("Logged out successfully")


functions_info = {
    "login": [2, "login\t\t\t[username] | [password]", login],
    "create_acc": [4, "create_acc\t\t[username] | [password] | [first_name] | [last_name]", funcs.create_account],
    "profile": [0, "profile", funcs.show_profile],
    "create_col": [1, "create_col\t\t[collection_name]", funcs.create_collection],
    "get_col": [0, "get_col", funcs.get_collections],
    "col_add": [2, "col_add\t\t\t[collection] | [game]", funcs.add_game_to_collection],
    "col_del_game": [2, "col_del_game\t[collection] | [game]", funcs.delete_game_from_collection],
    "col_del": [1, "col_del\t\t\t[collection]", funcs.delete_collection],
    "col_rename": [2, "col_rename\t\t[collection] | [new_name]", funcs.modify_collection_name],
    "plat_add": [1, "plat_add\t\t[platform]", funcs.add_platform],
    "game_add": [1, "game_add\t\t[game]", funcs.add_game],
    "rate": [2, "rate\t\t\t[game] | [stars]", funcs.rate_game],
    "play": [2, "play\t\t\t[game] | [minutes]", funcs.play_game],
    "playr": [1, "playr\t\t\t[minutes]", funcs.play_game_random],
    "search": [1, "search\t\t\t[email]", funcs.search_user],
    "fol": [1, "fol\t\t\t\t[username]", funcs.follow],
    "unfol": [1, "unfol\t\t\t[username]", funcs.unfollow],
    "logout": [0, "logout", logout],
    "search_game": [4, "search_game\t\t[search_by] | [string] | [order_by] | [asc/desc]", funcs.search_video_games],
    "pop_games" : [0, "pop_games", funcs.get_trending_games],
    "fol_games" : [0, "fol_games", funcs.get_follower_games],
    "mon_games" : [0, "mon_games", funcs.get_trending_games_month],
    "rec_games" : [0, "rec_games", funcs.recommended_games],
}


def authenticate():
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=USERNAME,
                            ssh_password=PASSWORD,
                            remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("SSH tunnel established")
        params = {
            'database': DBNAME,
            'user': USERNAME,
            'password': PASSWORD,
            'host': 'localhost',
            'port': server.local_bind_port
        }

        try:
            conn = psycopg2.connect(**params)
            print("Database connection established")
            start_session(conn)
        except:
            print("Connection failed")


def start_session(conn):
    print("Type 'help' for a list of available functions or 'q' to exit")
    while True:
        names = list(functions_info.keys())
        if UID == -1:
            names = names[:2]
        else:
            names = names[2:]
        x = str(input(">>> "))
        if x == "q":
            break
        if len(x.strip()) == 0:
            continue
        arguments = [e[0] if e[0] else e[1] for e in re.findall(r'"([^"]+)"|([^ ]+)', x)]
        name = arguments[0]
        if name == "help":
            print("List of functions:")
            for f in names:
                print(functions_info[f][1])
            if UID == -1:
                print("Login to see other functions")
            continue

        if name not in names:
            print(f"Invalid function '{name}'")
            continue

        func = functions_info[name]
        if len(arguments) - 1 != func[0]:
            print("Incorrect usage")
            print("Usage: " + func[1])
            continue
        arguments[0] = conn
        if USER is not None:
            arguments.insert(1, USER)
        try:
            func[2](*arguments)
        except Exception as e:
            print(e)
        conn.commit()


authenticate()
