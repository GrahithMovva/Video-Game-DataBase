# import functions.py
import re

functions_info = {
    "help":     [0, "Usage: help"],
    "cra":      [5, "Usage: cra  [Email] | [Username] | [Password] | [first_name] | [last_name]"],
    "addplat":  [1, "Usage: addplat  [platform] "],
    "crc":      [1, "Usage: crc  [collection_name]"],
    "coladd":   [2, "Usage: coladd  [collection_name] | [game]"],
    "coldelg":  [2, "Usage: coldelg  [collection_name] | [game]"],
    "coldel":   [1, "Usage: coldel  [collection_name]"],
    "colren":   [2, "Usage: colren  [collection_name] | [new_name]"],
    "rate":     [2, "Usage: rate  [game] | [stars]"],
    "fol":      [1, "Usage: fol  [username]"],
    "unfol":    [1, "Usage: unfol  [username]"],
    "login":    [2, "Usage: login  [username] | [password]"],
    "logout":   [0, "Usage: logout"],
}


def do_query(string):
    print("Done!")


def authenticate():
    return None


def start_session():
    x = ""
    print("Type help for a list of available functions or 'q' to exit")
    while x != "q":
        names = functions_info.keys()
        x = str(input(">>> "))
        args = re.split(" ", x)

        if args[0] not in names:
            print("Invalid function '{}'".format(x))
            continue

        func = functions_info[args[0]]
        if len(args)-1 != func[0]:
            print("Incorrect usage")
            print(func[1])
            continue

        if args[0] == "help":
            print("List of function usages:")
            for f in names:
                print(functions_info[f][1])
            continue
        do_query(x)


start_session()
