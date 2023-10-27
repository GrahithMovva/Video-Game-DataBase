# import functions.py

def do_query(string):
    return None


def authenticate():
    return None


def start_session():
    x = ""
    while x != "q":
        x = str(input("Pick a query or type help for a list of available queries"))
        if x == help:
            print("List of available functions:")
            continue
        do_query(x)

