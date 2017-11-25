#!python3.6
import discord
import asyncio
import sqlite3



client = discord.Client()
commanderRole = 'permGroup'
permRoles = {}

def getServerPermRoles():
    #loads every server id and permgroup from file to a dictionary
    for server in client.servers:
        try:
            serverConfig = open('config/' + server.id, 'r')
            role = serverConfig.read()
            permRoles[server.id] = role 
        except:
            pass

    print(permRoles)




def get_all_members():
    users = []
    for server in client.servers:
        for member in server.members:
            users.append(member)
    return users


def playingStatus():
    numOfServers = len(client.servers)
    return(str(numOfServers))
    
def checkPermissions(author):
    userRoles = []
    print(author.server.roles)
    for y in author.roles:
        userRoles.append(str(y))
        print(y)
        print(y.id)
            
    if commanderRole in userRoles:
        return True
    else:
        return False
    

async def titleUpdater():
    while not client.is_closed:
        await client.wait_until_ready()
        await client.change_presence(game=discord.Game(name='Managing ' + playingStatus() + ' server(s)'))
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
@client.event
async def on_server_join(server):
    await client.send_message(message.channel, ('Hi there! My name is kickbot and I manage user roles and nicknames, and I can restore these details when someone mysteriously goes missing ;) To set me up the server owner needs to setup a role on the server with the users they want to have access to me. Then type "!setrole" and reply with the role name!'))

@client.event
async def on_message(message):
    

    #no bots can use server commands
    if message.author.bot == True:
        return
    
    if message.content.startswith('!update'):
        for channel in message.server.channels:
            
            print ('type - ' + str(channel.type))
            print('bob - ' + str(channel.is_default))
            if str(channel.type) == 'text':
                await client.send_message(channel, ('yay 1 channel!'))
                break

        await client.send_message(message.server.default_channel, ('default channel!'))
        
        if checkPermissions(message.author) == True:
            
            users = get_all_members()
            for user in users:
                print(user.display_name)

            await client.send_message(message.channel, ('update completed'))
        else:
            await client.send_message(message.channel, (message.author.mention +' You do not have the required permissions to run that command!'))

    if message.content.startswith('!setrole'):
        if message.author == message.server.owner:
            await client.send_message(message.channel, ('please enter the name of the role you wish to be granted bot permissions'))

            msg = await client.wait_for_message(author=message.author)
            print(msg.content)
            serverid = message.server.id

            #print(client.get_server(serverid).roles)
            backupfile = open('config/' + str(serverid), 'w')
            backupfile.write(msg.content)
            backupfile.close()

        else:
            await client.send_message(message.channel, ('You must be the server owner to do this! Tsk Tsk'))

    if message.content.startswith('!hi'):
        #await client.add_roles(message.author, '382129684260978700')
        await client.send_message(message.channel, (message.author.mention + ' hi'))



client.loop.create_task(titleUpdater())
client.run('TOKEN')
