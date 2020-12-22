# import sqlite3  ## LEGACY FOR LOCAL INSTALLATION
import ast, os, psycopg2
import urllib.parse as urlparse
global c, conn

url = urlparse.urlparse(os.getenv('DATABASE_URL'))
conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
            )

c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY, serverID BIGINT, chatID BIGINT)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, userID BIGINT, serverID BIGINT, nickname TEXT, roles TEXT)''')
conn.commit()

def writeServerConfig(server, chat):
    c.execute("SELECT * FROM servers WHERE serverID = %s", [int(server)])
    if len(c.fetchall()) == 0:
        c.execute('INSERT INTO servers(serverID, chatID) VALUES(%s,%s)', [int(server), int(chat)])
    else:
        c.execute("UPDATE servers SET chatID = %s WHERE serverID = %s", [chat, server])
    conn.commit()


def getServerConfig(server):
    try:
        c.execute("SELECT * FROM servers WHERE serverID=%s", [server])
        result = c.fetchall()
        return result[0][2]
    except:
        return


def backupUser(server, user, nick, roles):
    c.execute("SELECT * FROM users WHERE serverID=%s AND userID=%s", [server, user])
    if len(c.fetchall()) == 0:
        c.execute('INSERT INTO users(userID, serverID, nickname, roles) VALUES(%s,%s,%s,%s)', [user, server, str(nick.encode('UTF-8')), str(roles)])
    else:
        c.execute('DELETE FROM users WHERE userID = %s', [user])
        c.execute('INSERT INTO users(userID, serverID, nickname, roles) VALUES(%s,%s,%s,%s)', (user, server, str(nick.encode('UTF-8')), str(roles)))
    conn.commit()


def getUser(server, user):
    try:
        c.execute("SELECT * FROM users WHERE serverID=%s AND userID=%s", [int(server), int(user)])
        result = c.fetchall()
        nick = ast.literal_eval(result[0][3]).decode('UTF-8')
        roles = ast.literal_eval(result[0][4])
        return nick, roles
    except:
        return


def closeConnection():
    conn.close()
