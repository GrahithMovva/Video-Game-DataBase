import psycopg2
from sshtunnel import SSHTunnelForwarder
import credentials
import funcs
username = credentials.username
password = credentials.password
dbName = credentials.dbName

def getall(curs):
    curs.execute('SELECT * FROM users')
    
    print(curs.fetchall())
   

def main():
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
            curs = conn.cursor()
            print("Database connection established")
        except:
            print("Connection failed")
            
        funcs.create_account(curs,'grahith','movva','gm','hello')
        conn.commit()
        getall(curs)
            
    
main()
