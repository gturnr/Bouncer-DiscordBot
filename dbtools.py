import sqlite3, ast

global c, conn
conn = sqlite3.connect('bouncerData.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY, serverID INT, chatID INT)')
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, userID INT, serverID INT, nickname TEXT, roles TEXT)')


def writeServerConfig(server, chat):
    c.execute("SELECT * FROM servers WHERE serverID=?", (server,))
    if len(c.fetchall()) == 0:
        c.execute('INSERT INTO servers(serverID, chatID) VALUES(?,?)', (server, chat))
    else:
        c.execute("UPDATE servers SET chatID = ? WHERE serverID = ?", (chat, server))
    conn.commit()


def getServerConfig(server):
    c.execute("SELECT * FROM servers WHERE serverID=?", (server,))
    result = c.fetchall()
    return result[0][2]


def backupUser(server, user, nick, roles):
    c.execute("SELECT * FROM users WHERE serverID=? AND userID=?", (server, user))
    if len(c.fetchall()) == 0:
        c.execute('INSERT INTO users(userID, serverID, nickname, roles) VALUES(?,?,?,?)', (user, server, nick.encode('UTF-8'), str(roles)))
    else:
        c.execute("UPDATE users SET nickname=? AND roles=? WHERE serverID=? AND userID=?", (nick.encode('UTF-8'), str(roles), server, user))
    conn.commit()


def getUser(server, user):
    c.execute("SELECT * FROM users WHERE serverID=? AND userID=?", (int(server), int(user)))
    result = c.fetchall()
    nick = result[0][3].decode('UTF-8')
    roles = ast.literal_eval(result[0][4])
    return nick, roles



#backupUser(10, 5, 'j̴i̴g̴g̴l̴e̴', [1,2,45])
#getUser(10, 5)

#conn.close()
