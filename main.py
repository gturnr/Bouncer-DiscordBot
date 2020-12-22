#!python3.6
import discord, asyncio, os, ast, random, time, logging
from dotenv import load_dotenv  # load config variables
import dbtools
from time import gmtime, strftime
import log_config

load_dotenv()

# logger configuration
if 'HEROKU' in os.environ:  # check if running Heroku for stdout logging
    print('Detected Heroku')
    discord_logger = log_config.setup_logger('discord', False)
    logger = log_config.setup_logger('bouncer', False, console_level=logging.INFO)
else:  # if running locally save to file
    discord_logger = log_config.setup_logger('discord', True,'discordpy.log')
    logger = log_config.setup_logger('bouncer', True, 'bouncer.log', logging.INFO, logging.INFO)

client = discord.Client()  # creates the Discord client

global spam_time
spam_time = 0  # creates a variable, later used to prevent spam and abuse of bot commands


def playingStatus():  # function to return the number of servers that the bot is currently running in
    numOfGuilds = len(client.guilds)
    return (str(numOfGuilds))


def getAuth():  # opens a text file and loads the disocrd private key from it
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is None:
        print('Failed to load API TOKEN. Set Bot Token to Env variable DISCORD_TOKEN')
        logger.critical('No key file. exiting...')
        exit()
    else:
        return TOKEN

def getServerChat(guild):  # function to recall the preffered server channel from local file storage
    try:
        channelID = dbtools.getServerConfig(int(guild.id))  # gets the channel ID for a sever
        for pos, channel in enumerate(
                guild.channels):  # NEEDS CLEANING UP. gets the correct channel object from the channel id
            if str(channel.id) == str(channelID):
                return channel

    except Exception as e:
        logger.debug(e)

    for channel in guild.channels:  # backup system if channel not yet set, returns first text channel in server (usually the oldest)
        if str(channel.type) == 'text':
            return channel


async def titleUpdater():  # function to update the 'playing' variable of the bot every X seconds with the correct number of servers
    while not client.is_closed():
        await client.wait_until_ready()
        await client.change_presence(status=discord.Status.online, activity=discord.Game(name='Keeping ' + playingStatus() + ' guild(s) in check'))
        for guild in client.guilds:
            if guild.id == 384427705254412288:
                for role in guild.roles:
                    if role.id == 384430847677431809:
                        permissions = discord.Permissions()
                        permissions.update(kick_members = True, ban_members=True)
                        await role.edit(reason = None, position=27)
        await asyncio.sleep(20)  # X value here


@client.event
async def on_ready():  # function to output the client name and id upon successful connection to Discord
    print(client.user.name)
    logger.info('Connected as ' + client.user.name + ' - ' + str(client.user.id))
    for guild in client.guilds:
        logger.info('Connected to guild ' + guild.name + ' ('+ str(guild.id) + ')')


@client.event
async def on_member_remove(member):  # function to run when a member keaves or is removed from a server
    logger.info('member: ' + str(member.id) + ' (' + str(member.name) + ') left guild: ' + str(member.guild.id))

    if member == client.user:
        return

    nickname = member.display_name  # gets the members nickname (note: this will not always be a string type if member's nickname uses custom fonts or characters)
    strRoles = []
    for role in member.roles:  # loops through all of the users roles and adds the role id to a list
        if str(role) != '@everyone':  # ignores the role @everyone as this does not require reassignment later on
            strRoles.append(str(role.id))

    guild_id = str(member.guild.id)  # gets the server id of the member

    dbtools.backupUser(guild_id, member.id, nickname, strRoles)

    channel = getServerChat(member.guild)  # calls getServerChat function to return the preferred server channel
    await channel.send(
                'Member ' + member.name + ' has left the server... configuration successfully backed up.', file=discord.File('bye.gif', 'bye.gif'))  # outputs confirmation of backup
    logger.info('member: ' + str(member.id) + ' (' + str(member.name) + ') successfully backed up')


@client.event
async def on_member_join(member):  # function run upon a new user joining a server
    logger.info('new member: ' + str(member.id) + ' (' + str(member.name) + ') joined server: ' + str(member.guild.id))

    if member == client.user == True:
        return

    channel = getServerChat(member.guild)
    await channel.send('Welcome ' + member.mention + ' to the server!')  # welcome greeting to the new member

    try:  # will attempt to load member details
        nickname, roles = dbtools.getUser(member.guild.id, member.id)

    except:  # if there were no saved member config then the function exits
        logger.info('No saved details for new user')
        return

    await client.change_nickname(member, nickname)  # changes the member nickname
    added_roles = []  # list for successful roles
    failed_roles = []  # list for failed roles
    for role in roles:  # loops through every role in the list roles (from config file)
        for guildRole in member.guild.roles:  # loops through every role in the server, to append a role to the user you need the role object (not just the id)
            if str(guildRole.id) == role:  # if the server role is matching then attempt to append the role to the user
                try:
                    await client.add_roles(member, guildRole)
                    added_roles.append(guildRole)  # adds the role to the list of successful roles
                except:
                    failed_roles.append(
                        guildRole)  # if the role could not be appended, add to the list of failed roles

            await asyncio.sleep(0.2)

    added_roles_str = ''
    failed_roles_str = ''
    failed_roles_str = ', '.join(map(str, failed_roles))
    added_roles_str = ', '.join(map(str, added_roles))

    if len(added_roles) != 0:  # if there is at least one entry in the list
        await channel.send(
                    'Member ' + member.name + ' has been reassigned roles: ' + added_roles_str)  # outputs to the chat the roles that have been reassigned

    if len(failed_roles) != 0:  # if there is at least one entry in the list
        await channel.send(
                    'Please be aware! The following roles could not be reassigned: ' + failed_roles_str)  # outputs to the chat the roles that could not be reassigned (usually permission related issues)

    logger.info('reassigned member: ' + str(member.id) + ' (' + str(member.name) + ') with saved details')


@client.event
async def on_message(message):
    # no bots can use server commands
    if message.author.bot == True:
        return

    if message.content.startswith('!setchat'):  # if the server owner is trying to set the bot default chat
        logger.info('!setchat - server: ' + str(message.guild.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')

        if message.author == message.guild.owner or message.author.id == 158639538468683776:  # checks if the message is from the server owner
            logger.info('!setchat Authenticated')
            dbtools.writeServerConfig(message.guild.id, message.channel.id)
            await message.channel.send('Default text chat saved!')  # outputs confirmation to the chat

        else:
            logger.info('!setchat denied')
            await message.channel.send('Tsk Tsk! You need to be the owner to run this command!')  # outputs error (permissions)


    # russian roulette game. Will identify the voice channel of the member (host) who sent the message, and all other
    # members in the call. It will then randomly select a member in the call and kick them (as well as generating an
    # invite and sending it to the kicked member). This also invokes the backup/restore feature of the bot.
    # An anti-spam function has been included - the feature can only be called every X seconds

    if message.content.startswith('!russianroulette'):
        logger.info('!russianroulette - server: ' + str(message.guild.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')
        global spam_time
        run_time = time.time()
        difference = run_time - spam_time

        if difference > 30:  # change this value to change the time limit (seconds)
            spam_time = time.time()

            voice_channel = message.author.voice.voice_channel  # gets the host voice channel
            if voice_channel is None:
                await message.channel.send("You can only run this command when in a voice channel!")

            else:
                await message.channel.send("I'm choosing a victim...")
                await asyncio.sleep(1)  # pauses for 1 second
                await message.channel.send("Bang!")
                channel = getServerChat(message.guild)
                invite = await channel.create_invite(max_age=600)
                all_members = message.guild.members
                valid_members = []
                for member in all_members:
                    if member.bot != True and (
                            member != member.guild.owner):  # checks the member is not a bot and is not the server owner
                        if member.voice.voice_channel == voice_channel:  # checks if the member is in the voice channel of the host
                            valid_members.append(member)

                userVal = random.randint(0, len(valid_members) - 1)  # picks a random member
                await message.channel.send("Bad luck " + valid_members[userVal].name)
                await valid_members[userVal].send("Bad luck! rejoin here: " + invite.url)  # DMs the member a sever invite
                await client.kick(valid_members[userVal])  # kicks the member from the server

        else:
            await message.channel.send("Please wait before running this command again!")

    if message.content.startswith('!update'):
        logger.info('!update - server: ' + str(message.guild.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')

        if message.author.id == 158639538468683776:
            await message.channel.send("Handing over to update script...")
            try:
                os.system('python update.py')
                exit()
            except:
                await message.channel.send("Error, could not run update script")
        else:
            await message.channel.send("You are not my father...")

    if message.content.startswith('!testchat'):
        logger.info('!testchat - server: ' + str(message.guild.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')
        channel = getServerChat(message.guild)
        await channel.send('All good')

    if message.content.startswith('!invite'):
        guild = message.guild
        if guild: # check message wasn't dm
            channel = getServerChat(message.guild)
            invite = await channel.create_invite(max_age=600)
            await message.channel.send(invite.url)

    if message.content.startswith('!unban'):
        split_message = message.content.split(' ', 1) # split message after first space for server name
        if len(split_message) > 1:
            server_name = split_message[1]
        else:
            return

        for guild_ in client.guilds:
            if guild_.name == server_name:
                current_guild = guild_
                break

        pm = await message.author.create_dm()

        if "current_guild" not in locals():
            await pm.send("Invalid server name.")

        else:
            guild_bans = await current_guild.bans()
            if message.author in guild_bans:

                if message.author.id == 158639538468683776:
                    await pm.send("The ban hammer has been lifted!")
                    await current_guild.unban(message.author)
                    channel = getServerChat(current_guild)
                    invite = await channel.create_invite(max_age=600)
                    await pm.send(invite.url)
                else:
                    await pm.send("Let me ask the owner for you ;)")
                    owner_pm = await current_guild.owner.create_dm()
                    await owner_pm.send("Do you want to unban " + str(message.author.name) + "? (y/n)")
                    msg = await client.wait_for_message(author=current_guild.owner)
                    response = msg.content.lower()
                    if response == 'y' or response == 'yes':
                        await pm.send("The ban hammer has been lifted!")
                        await current_guild.unban(message.author)
                        channel = getServerChat(message.guild)
                        invite = await channel.create_invite(max_age=600)
                        await pm.send(invite.url)
                    else:
                        await pm.send("DENIED.")
            else:
                print(current_guild.name)
                await message.author.send("You aren't banned you nutter.")

    if message.content.startswith('!kick'):
        logger.info(message.content + ' - server: ' + str(message.guild.id) + ' | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')

        if message.author == message.guild.owner or message.author.id == 158639538468683776:
            channel = getServerChat(message.guild)
            userDiscriminator = message.content.split(' ', 1)[1]
            userDiscriminator = int(userDiscriminator)
            # something wrong here
            for member in message.guild.members:
                if member.bot != True and (member != member.guild.owner):
                    if int(member.discriminator) == userDiscriminator:
                        channel = getServerChat(message.guild)
                        invite = await channel.create_invite(max_age=600)
                        pm = await member.create_dm()
                        await pm.send("Rejoin here: " + invite.url)
                        await channel.send('Kicked user ' + str(member.name))
                        await message.guild.kick(member)
                        break
        else:
            channel = getServerChat(message.guild)
            logger.info('!kick denied | user: ' + str(message.author.id) + ' (' + str(message.author.name) + ')')
            await channel.send('Tsk Tsk! You do not have permission to do that')


@client.event
async def on_server_join(guild):  # function to run when the bot joins a new server
    logger.info('Joined server: ' + str(message.guild.id))
    channel = getServerChat(guild)
    await channel.send('Hi there! My name is bouncerbot and I manage user roles and nicknames, I can restore these details when someone mysteriously goes missing ;) Here is the deal - to set me up edit my role so it is above the roles you want me to be able to manage! I also need nickname and role permissions! Finally, the server owner needs to type "!setchat" in the text chat you want this bot to use')


@client.event
async def on_error(event):
    print('Error')
    logger.critical(event)
    exit()

client.loop.create_task(titleUpdater())  # creates a task to update the 'playing' status
client.run(getAuth())  # runs the client using the Discord bot token in the file 'key.txt'
