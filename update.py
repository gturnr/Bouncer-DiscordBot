import time, os
import urllib.request

script_location = 'https://raw.githubusercontent.com/guyturner797/Bouncer-DiscordBot/master/main.py'

print('updating BouncerBot...')
time.sleep(2)


print('pulling script')
try:
    response = urllib.request.urlopen(script_location)
    data = response.read()
    text = data.decode('utf-8')
    print('script pull completed')

except:
    print('pull failed. Reverting to current version')
    log = open('updatelog.txt', 'w')
    log.write('updated failed')
    log.close()
    os.system('python main.py')
    exit()

if os.path.exists('revisions/old.py') == True:
    os.remove('revisions/old.py')

os.rename('main.py', 'revisions/old.py')
updater = open('main.py', 'w')
updater.write(text)
updater.close()

log = open('updatelog.txt', 'w')
log.write('updated successfully')
log.close()
time.sleep(2)


os.system('python main.py')