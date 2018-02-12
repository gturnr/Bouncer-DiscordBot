#!python3.6
import discord, asyncio, os, ast, random, time
import dbtools
from time import gmtime, strftime

client = discord.Client() #creates the Discord client

global spam_time
spam_time = 0 #creates a variable, later used to prevent spam and abuse of bot commands


def playingStatus(): #function to return the number of servers that the bot is currently running in
    numOfServers = len(client.servers)
    return(str(numOfServers))


def getAuth(): #opens a text file and loads the disocrd private key from it
    try:
        file = open('key.txt')
        key = file.readline()
        file.close()
        return key
    except: #if the file could not be opened, exits to prevent a non-authorised attempt at connecting to discord
        print('Failed to load key file... create a text file called "key.txt" with your auth key')
        exit()


def getServerChat(server): #function to recall the preffered server channel from local file storage
    try:
        channelID = dbtools.getServerConfig(int(server.id)) #gets the channel ID for a sever
        for pos, channel in enumerate(server.channels): #NEEDS CLEANING UP. gets the correct channel object from the channel id
            if str(channel.id) == str(channelID):
                return channel

    except :
        pass

    for channel in server.channels: #backup system if channel not yet set, returns first text channel in server (usually the oldest)
        if str(channel.type) == 'text':
            return channel


async def titleUpdater(): #function to update the 'playing' variable of the bot every X seconds with the correct number of servers
    while not client.is_closed:
        await client.wait_until_ready()
        await client.change_presence(game=discord.Game(name='Keeping ' + playingStatus() + ' server(s) in check'))
        await asyncio.sleep(120) #X value here


@client.event
async def on_ready(): #function to output the client name and id upon successful connection to Discord
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    '''
    for server in client.servers:
        for user in server.members:
            if int(user.discriminator) == 3983:
                await client.ban(user)'''


@client.event
async def on_member_remove(member): #function to run when a member keaves or is removed from a server
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+ ' | member: ' + str(member.id) + ' (' + str(member.name) + ') left server: ' + str(member.server.id))
    if member == client.user:
        return

    nickname = member.display_name #gets the members nickname (note: this will not always be a string type if member's nickname uses custom fonts or characters)
    strRoles = []
    for role in member.roles: #loops through all of the users roles and adds the role id to a list
        if str(role) != '@everyone': #ignores the role @everyone as this does not require reassignment later on
            strRoles.append(str(role.id))

    server_id = str(member.server.id) #gets the server id of the member

    dbtools.backupUser(server_id, member.id, nickname, strRoles)

    channel = getServerChat(member.server) #calls getServerChat function to return the preferred server channel
    await client.send_message(channel, ('Member ' + member.name + ' has left the server... configuration successfully backed up.')) ##outputs confirmation of backup
    await client.send_file(channel, 'bye.gif') #uploads a .gif file to the channel
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | member: ' + str(member.id) + ' (' + str(member.name) + ') successfully backed up')


@client.event
async def on_member_join(member): #function run upon a new user joining a server
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | new member: ' + str(member.id) + ' (' + str(member.name) + ') joined server: ' + str(member.server.id))
    if member == client.user == True:
        return

    channel = getServerChat(member.server)
    await client.send_message(channel, ('Welcome ' + member.mention + ' to the server!')) #welcome greating to the new member

    try: #will attempt to load member details
        nickname, roles = dbtools.getUser(member.server.id, member.id)

    except: #if there were no saved member config then the function exits
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | No saved details for new user')
        return

    await client.change_nickname(member, nickname) #changes the member nickname
    added_roles = [] #list for successful roles
    failed_roles = [] #list for failed roles
    for role in roles: #loops through every role in the list roles (from config file)
        for serverRole in member.server.roles: #loops through every role in the server, to append a role to the user you need the role object (not just the id)
            if str(serverRole.id) == role: #if the server role is matching then attempt to append the role to the user
                try:
                    await client.add_roles(member, serverRole) 
                    added_roles.append(serverRole) #adds the role to the list of successful roles
                except:
                    failed_roles.append(serverRole) #if the role could not be appended, add to the list of failed roles

            await asyncio.sleep(0.2)

    added_roles_str = ''
    failed_roles_str = ''
    failed_roles_str = ', '.join(map(str, failed_roles))
    added_roles_str = ', '.join(map(str, added_roles))

    if len(added_roles) != 0: #if there is at least one entry in the list
        await client.send_message(channel, ('Member ' + member.name + ' has been reassigned roles: ' + added_roles_str)) #outputs to the chat the roles that have been reassigned

    if len(failed_roles) != 0 :#if there is at least one entry in the list
        await client.send_message(channel, ('Please be aware! The following roles could not be reassigned: ' + failed_roles_str)) #outputs to the chat the roles that could not be reassigned (usually permission related issues)

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | reassigned member: ' + str(member.id) + ' (' + str(member.name) + ') with saved details...')

@client.event
async def on_message(message):
    # no bots can use server commands
    if message.author.bot == True:
        return

    if message.content.startswith('!setchat'): #if the server owner is trying to set the bot default chat
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | !setchat - server: ' + str(message.server.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')
        print(message.author.id)
        if message.author == message.server.owner or str(message.author.id) == '158639538468683776': #checks if the message is from the server owner
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | !setchat Authenticated')
            dbtools.writeServerConfig(int(message.server.id), int(message.channel.id))
            await client.send_message(message.channel, ('Default text chat saved!')) #outputs confirmation to the chat

        else:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | !setchat denied...')
            await client.send_message(message.channel, ('Tsk Tsk! You need to be the owner to run this command!')) #outputs error (permissions)

    #russian roulette game. Will identify the voice channel of the member (host) who sent the message, and all other members in the call. It will then randomly select a 
    #member in the call and kick them (as well as generating an invite and sending it to the kicked member). This also invokes the backup/restore feature of the bot.
    #An anti-spam function has been included - the feature can only be called every X seconds
    if message.content.startswith('!russianroulette'):
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | !russianroulette - server: ' + str(message.server.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')
        global spam_time
        run_time = time.time()
        difference  = run_time - spam_time

        if difference > 60: #change this value to change the time limit (seconds)
            spam_time = time.time()

            voice_channel = message.author.voice.voice_channel #gets the host voice channel
            if voice_channel is None:
                await client.send_message(message.channel, ("You can only run this command when in a voice channel!"))

            else:
                await client.send_message(message.channel, ("I'm choosing a victim..."))
                await asyncio.sleep(1) #pauses for 1 second
                await client.send_message(message.channel, ("Bang!"))

                invite = await client.create_invite(message.channel, max_age=600) #generates an invite that lasts 10 minutes
                all_members = message.server.members
                valid_members = []
                for member in all_members:
                    if member.bot != True and (member != member.server.owner): #checks the member is not a bot and is not the server owner
                        if member.voice.voice_channel == voice_channel: #checks if the member is in the voice channel of the host
                            valid_members.append(member)
        
                userVal = random.randint(0, len(valid_members)-1) #picks a random member
                await client.send_message(message.channel, ("Bad luck " + valid_members[userVal].name)) 
                await client.send_message(valid_members[userVal], "Bad luck! rejoin here: " + invite.url) #DMs the member a sever invite
                await client.kick(valid_members[userVal]) #kicks the member from the server

        else:
            await client.send_message(message.channel, ("Please wait before running this command again!"))

    if message.content.startswith('!update'):
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | !update - server: ' + str(message.server.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')
        if str(message.author.id) == '158639538468683776':
            await client.send_message(message.channel, ("Handing over to update script..."))
            try:
                os.system('python update.py')
                exit()
            except:
               await client.send_message(message.channel, ("Error, could not run update script"))
        else:
            await client.send_message(message.channel, ("You are not my father..."))

    if message.content.startswith('!testchat'):
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | !testchat - server: ' + str(message.server.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')
        channel = getServerChat(message.server)
        await client.send_message(channel, ('All good'))

    if message.content.startswith('!kick'):
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | !kick ' + message.content + ' - server: ' + str(message.server.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')
        
        if message.author == message.server.owner or str(message.author.id) == '158639538468683776':
            channel = getServerChat(message.server)
            try:
                userDiscriminator = message.content.split(' ', 1)[1]
                userDiscriminator = int(userDiscriminator)
                for member in message.server.members:
                    if member.bot != True and (member != member.server.owner):
                        if int(member.discriminator) == userDiscriminator:
                            invite = await client.create_invite(message.channel, max_age=600)
                            await client.send_message(member, "Rejoin here: " + invite.url)
                            await client.send_message(channel, ('Kicked user ' + str(member.name)))
                            await client.kick(member)
                            

            except:
                pass
        else:
            channel = getServerChat(message.server)
            await client.send_message(channel, ('Tsk Tsk! You do not have permission to do that ;)'))


@client.event
async def on_server_join(server): #function to run when the bot joins a new server
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' | Joined server: ' + str(message.server.id))
    channel = getServerChat(server)
    await client.send_message(channel, ('Hi there! My name is kickbot and I manage user roles and nicknames, I can restore these details when someone mysteriously goes missing ;) Here is the deal - to set me up edit my role so it is above the roles you want me to be able to manage! I also need nickname and role permissions! Finally, the server owner needs to type "!setchat" in the text chat you want this bot to use'))


client.loop.create_task(titleUpdater()) #creates a task to update the 'playing' status
client.run(getAuth()) #runs the client using the Discord bot token in the file 'key.txt'
