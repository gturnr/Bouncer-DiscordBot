# Bouncer-DiscordBot

A bot written in Python for Discord, a VoIP application designed for gaming communities. This bot saves member roles and nicknames when leaving a server, and reassigns them when rejoining, thus saving server administrators from having to manually reassign them.

## Getting started
1) Install discord.py using
```
python3 -m pip install -U discord.py
```
2) create a client at https://discordapp.com/developers/applications/me
Make sure to select 'create bot user' towards the bottom of the configuration page

3) Create a text file called 'key.txt' in the project directory and put the private key inside it.

4) Run the script and add the bot to your server using:
https://discordapp.com/oauth2/authorize/?permissions=8&scope=bot&client_id=YOUR_CLIENT_ID_HERE

5) Finally append the bot role so it is above all the roles you want it to manage and give it administrator permissions.

## Commands
Current list of bot commands

| Command | Function | Permissions |
| ------ | ---- | ---- |
| !setchat | Saves the default chat for the server | Can only be run by the server owner | 
| !russianroulette | Randomly kicks a member from a voice channel | Any member in a voice channel, limited to every 60 seconds |
| !unban | Allows a kicked user to ask the owner to unban them | kicked user |
| !kick | Kicks a user in the server (eg !kick 3245) | Can only be run by the server owner |
| !testchat | Validates that setchat worked correctly | server owner |
| !update | used to put the latest git commit of the bot and restart | Bot owner |
