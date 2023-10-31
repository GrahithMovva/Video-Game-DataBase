import psycopg2
from sshtunnel import SSHTunnelForwarder
import json
import re
import funcs

credentials = json.load(open("credentials.json"))
username = credentials["username"]
password = credentials["password"]
dbName = "p320_07"


def not_implemented(*args):
    print("Not implemented")


functions_info = {
    "cra": [4, "cra  [username] | [password] | [first_name] | [last_name]", funcs.create_account],
    "crc": [2, "crc  [uid] | [collection_name]", funcs.create_collection],
    "getc": [1, "getc  [uid]", funcs.get_collections],
    "coladd": [3, "coladd  [uid] | [cid] | [vid]", funcs.add_game_to_collection],
    "coldelg": [3, "coldelg  [uid] | [cid] | [vid]", funcs.delete_game_from_collection],
    "coldel": [1, "coldel  [cid]", funcs.delete_collection],
    "colren": [2, "colren  [cid] | [new_name]", funcs.modify_collection_name],
    "rate": [3, "rate  [uid] | [vid] | [stars]", funcs.rate_game],
    "play": [3, "play  [uid] | [vid] | [minutes]", funcs.play_game],
    "playr": [2, "playr  [uid] | [minutes]", funcs.play_game_random],
    "fol": [2, "fol  [uid] | [f_uid]", funcs.follow],
    "unfol": [2, "unfol  [uid] | [f_uid]", funcs.unfollow],
    "login": [2, "login  [username] | [password]", not_implemented],
    "logout": [0, "logout", not_implemented],
}


def authenticate():
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("SSH tunnel established")
        params = {
            'database': dbName,
            'user': username,
            'password': password,
            'host': 'localhost',
            'port': server.local_bind_port
        }

        try:
            conn = psycopg2.connect(**params)
            print("Database connection established")
        except:
            print("Connection failed")
        start_session(conn)


def start_session(conn):
    # curs = conn.cursor()
    print("Type 'help' for a list of available functions or 'q' to exit")
    while True:
        names = functions_info.keys()
        x = str(input(">>> "))
        if x == "q":
            break
        arguments = re.split(" ", x)
        name = arguments[0]
        if name == "help":
            print("List of functions:")
            for f in names:
                print(functions_info[f][1])
            continue

        if name not in names:
            print("Invalid function '{}'".format(name))
            continue

        func = functions_info[name]
        if len(arguments) - 1 != func[0]:
            print("Incorrect usage")
            print("Usage: " + func[1])
            continue
        arguments[0] = conn
        try:
            func[2](*arguments)
        except Exception as e:
            print(e)
        conn.commit()


authenticate()
