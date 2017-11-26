import sqlite3

global c, conn
conn = sqlite3.connect('bouncerData.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY, serverID INT, chatID INT)')
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, userID INT, serverID INT, nickname BLOB, roles TEXT)')

def writeServerConfig(server, chat):
    c.execute("SELECT * FROM servers WHERE serverID=?", (server,))
    if len(c.fetchall()) == 0:
        c.execute('INSERT INTO servers(serverID, chatID) VALUES(?,?)', (int(server), int(chat)))
    else:
        c.execute("UPDATE servers SET chatID = ? WHERE serverID = ?",(chat, server))
    conn.commit()

def getServerConfig(server):
    c.execute("SELECT * FROM servers WHERE serverID=?", (server,))
    result = c.fetchall()
    print(result[0])

writeServerConfig(10, 5)
conn.close()