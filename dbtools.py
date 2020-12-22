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
c.execute('''CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY, serverID INT, chatID INT)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, userID INT, serverID INT, nickname TEXT, roles TEXT)''')
conn.commit()

def writeServerConfig(server, chat):
    c.execute("SELECT * FROM servers WHERE serverID=?", (int(server),))
    if len(c.fetchall()) == 0:
        c.execute('INSERT INTO servers(serverID, chatID) VALUES(?,?)', (int(server), int(chat)))
    else:
        c.execute("UPDATE servers SET chatID = ? WHERE serverID = ?", (chat, server))
    conn.commit()


def getServerConfig(server):
    try:
        c.execute("SELECT * FROM servers WHERE serverID=?", (server,))
        result = c.fetchall()
        return result[0][2]
    except:
        return


def backupUser(server, user, nick, roles):
    c.execute("SELECT * FROM users WHERE serverID=? AND userID=?", (server, user))
    if len(c.fetchall()) == 0:
        c.execute('INSERT INTO users(userID, serverID, nickname, roles) VALUES(?,?,?,?)', (user, server, str(nick.encode('UTF-8')), str(roles)))
    else:
        c.execute('DELETE FROM users WHERE userID = ?', (user,))
        c.execute('INSERT INTO users(userID, serverID, nickname, roles) VALUES(?,?,?,?)', (user, server, str(nick.encode('UTF-8')), str(roles)))
    conn.commit()


def getUser(server, user):
    try:
        c.execute("SELECT * FROM users WHERE serverID=? AND userID=?", (int(server), int(user)))
        result = c.fetchall()
        nick = ast.literal_eval(result[0][3]).decode('UTF-8')
        roles = ast.literal_eval(result[0][4])
        return nick, roles
    except:
        return


def closeConnection():
    conn.close()
