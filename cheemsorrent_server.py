#Last updated: June 2 2021
#some server implementations are are not included

# Error [1] Raised inside apicall() [user is notified]
# Error [2] Raised inside telegram_webhook() [main] excluding time check and request.get_json() [user notified if chat_id was obtained]
# Error [3] Rasied inside telegram_webhook() [main] on request.get_json() [user not notified]

from flask import Flask, request
import telepot
import urllib3
from urllib.request import Request, urlopen
import json


firstmsg = 'Make sure you have a Torrent CLIENT installed in your device before opening the downloaded Torrent file\n\
If you don\'t have a Torrent CLIENT, download one from here: https://freeappsforme.com/torrent-apps/\n\
\nIf you are unable to download the Torrent file, use a VPN! https://protonvpn.com\n\n-'

secondmsg = 'Make sure you have read the terms (send /terms) before using this bot.\n\n\
So which movie\'s torrent files should I search for? Send me a name (eg. Oslo, casino royale, tintin)'

found_msg = 'Wooof!! I found some links\nYou can download the Torrent file by clicking on the link\nUse a VPN if you are unable to download'
ntfound_msg = 'No Torrent links found. Make sure you are sending the name in proper format (refer the movie\'s imdb or wikipedia page). \nIf still not found, maybe the movie \
is not available in YTS server.'

terms = "This bot makes API requests to YTS for getting Torrent links and solely acts as a bridge between the user and the YTS site. \
Torrenting movies (protected media) is illegal in most countries and by using this bot you may violate the piracy laws in your region. \
Devs are not responsible for any copyright, piracy lawsuites, legal claims arising from user using this bot. The bot cannot be entitled under illegal distribution piracy act as user \
is completely, at their own wish, using this bot for getting the Torrent links which could also have been obtained by accessing the YTS sites from any browser by the same user. \
So filing a lawsuite against the devs will be same as filing a lawsuite against the browser through which user was accessing the YTS sites. The dev does not encourage piracy. \
This bot was meant to help individuals who cannot afford a subscription based service for watching movies."

server_error = 'Server error occurred. Admin was notified.\nPlease try again later.'

#####################################################################################################################################################################################################

#Removed for security concerns
#secret = ""
#bot = telepot.Bot()
#bot.setWebhook("".format(secret), max_connections=1)
#adminID =  #admin chatID



#--------------------------YTS-------------------------------
def YTSapi(a,b,c,d):
    #from YTS API documentation [https://yts.mx/api]
    main = 'https://yts.mx/api/v2/list_movies.json'
    query_term = '?query_term=' + str(a) #[a] Used for movie search, matching on: Movie Title/IMDb Code, Actor Name/IMDb Code, Director Name/IMDb Code
    limit = '&limit=' + str(b)           #[b] The limit of results per page that has been set
    sort_by = '&sort_by=' + str(c)       #[c] Sorts the results by choosen value
    order = '&order=' + str(d)           #[d] Orders the results by either Ascending or Descending order

    #YTS server not ordering the result, so order is commented
    temp = main+query_term+limit+sort_by#+order
    print('Link: ' + temp)
    return temp



#apicall() -> Makes API querys
def apicall(chat_id,name):
    try:
        #Searh result limit set to 10, Sorted by download_count in ascending order
        query_link = YTSapi(name,10,'download_count','asc')
        req = Request(query_link,headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data_json = json.loads(webpage)

        if data_json['data']['movie_count'] > 0:

            for name in data_json['data']['movies']:
                temp = name['title_long']  + '\n'

                for torr in name['torrents']:
                    temp+='----------\nDownload ' + torr['quality'] + ' [' + torr['type'] + '] Torrent file:' + '\n' + torr['url'] + '\nSize: ' +  torr['size'] + '\n'

                bot.sendMessage(chat_id, temp)
            return 'OK'
        else:
            return 'NA'
    except:
        return query_link #return query link

#----------------------------------------

global msg

app = Flask(__name__)
@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    global msg

    try:
        msg = request.get_json()

    except:
        bot.sendMessage(adminID, 'Error raised inside telegram_webhook() [main] | msg = request.get_json() [3]') # error code 3
        return 'OK'

    try:
        if "message" in msg:
            chat_id = 0 # clear id
            chat_id = msg["message"]["chat"]["id"]

            if "text" in msg["message"]: # only text allowed
                temp2 = msg["message"]["text"].strip().replace(' ','%') #Search query cannot have spaces and is replaced by '%'

            #----------From file---------------

            #--------------New user----------------
                if temp2 == '/start':
                    bot.sendMessage(chat_id, firstmsg)
                    bot.sendMessage(chat_id, secondmsg)
                    return 'OK'

                if temp2 == '/terms':
                    bot.sendMessage(chat_id, terms)
                    return 'OK'


            #-------------Starting search----------------------
                bot.sendMessage(chat_id, 'Searching for links!\nGive me some time...')
                temp = apicall(chat_id, temp2)
                if temp == 'NA':
                    bot.sendMessage(chat_id, ntfound_msg)

                elif temp == 'OK':
                    bot.sendMessage(chat_id, found_msg)

                else:
               #----------------------------------notify error to admin----------------------------------
                    print('Error occurred in apicall()')
                    bot.sendMessage(chat_id, server_error + ' [1]') # error code 1
                    bot.sendMessage(adminID, 'exception raised in apicall()\nQuery Link:\n' + temp + ' [1]\n')


            else:
                bot.sendMessage(chat_id, "Only send text messages")

    except:
        print('Error occurred inside telegram_webhook() [main]')

        # check if chat_id was obtained
        if chat_id != 0:
            bot.sendMessage(chat_id, server_error + ' [2]') # error code 2
        bot.sendMessage(adminID, 'exception raised inside telegram_webhook() [main] [2]')
        bot.sendMessage(adminID, msg)

    return "OK"
