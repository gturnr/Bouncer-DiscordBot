import time, os
import urllib.request

script_location = 'https://raw.githubusercontent.com/guyturner797/Bouncer-DiscordBot/master/main.py'


print('updating BouncerBot...')
time.sleep(2)

try:
    print('pulling script')
    response = urllib.request.urlopen(script_location)
    data = response.read()
    text = data.decode('utf-8')
    print('script pull completed')
    os.rename('main.py', 'old.py')
    updater = open('main.py', 'w')
    updater.write(text)
    updater.close()

except:
    print('pull failed. Reverting to current version')



log = open('updatelog.txt', 'w')

log.close()
time.sleep(2)


os.system('python main.py')