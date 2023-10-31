import psycopg2
from sshtunnel import SSHTunnelForwarder
import json
import re
import funcs


credentials = json.load(open("credentials.json"))
username = credentials["username"]
password = credentials["password"]
dbName = "p320_07"


def not_implemented(curs):
    print("Not implemented")


functions_info = {
    "cra":      [5, "Usage: cra  [Email] | [Username] | [Password] | [first_name] | [last_name]", funcs.create_account],
    "addplat":  [1, "Usage: addplat  [platform] ", not_implemented],
    "crc":      [1, "Usage: crc  [collection_name]", not_implemented],
    "coladd":   [2, "Usage: coladd  [collection_name] | [game]", not_implemented],
    "coldelg":  [2, "Usage: coldelg  [collection_name] | [game]", not_implemented],
    "coldel":   [1, "Usage: coldel  [collection_name]", not_implemented],
    "colren":   [2, "Usage: colren  [collection_name] | [new_name]", not_implemented],
    "rate":     [2, "Usage: rate  [game] | [stars]", not_implemented],
    "fol":      [1, "Usage: fol  [username]", not_implemented],
    "unfol":    [1, "Usage: unfol  [username]", not_implemented],
    "login":    [2, "Usage: login  [username] | [password]", not_implemented],
    "logout":   [0, "Usage: logout", not_implemented],
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
    curs = conn.cursor()
    print("Type 'help' for a list of available functions or 'q' to exit")
    while True:
        names = functions_info.keys()
        x = str(input(">>> "))
        if x == "q":
            break
        args = re.split(" ", x)

        if args[0] == "help":
            print("List of function usages:")
            for f in names:
                print(functions_info[f][1])
            continue

        if args[0] not in names:
            print("Invalid function '{}'".format(x))
            continue

        func = functions_info[args[0]]
        if len(args)-1 != func[0]:
            print("Incorrect usage")
            print(func[1])
            continue
        args[0] = curs
        func[2](args)
        conn.commit()


authenticate()
