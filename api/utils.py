from api.GooglePlay import GooglePlay
from api.AppStore import AppStore
from api.Games import Games
import urllib.parse
from bs4 import BeautifulSoup
import requests
import jellyfish
from config import Config
import logging
import json
import time

ACCESS_TOKEN = '' #set global variable so each linkme request will only use 1 access token -> Reduces time
to_refresh_time = 0 #time when we need to refresh token

logging.basicConfig(level=logging.INFO, filename='output.log', filemode='a',
                    format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %I:%M:%S %p')


def similar(a, b):
    return jellyfish.levenshtein_distance(a, b)

def refresh_token(): #generate access token for use with IGDB API
    global ACCESS_TOKEN
    global to_refresh_time
    auth_url = 'https://id.twitch.tv/oauth2/token'  #authorization URL
    auth_header = {'client_id': Config.twitch_client_id,
                   'client_secret': Config.twitch_client_secret, 'grant_type': 'client_credentials'}
    r = requests.post(auth_url, data=auth_header)
    reply = json.loads(r.text)
    access_token = reply.get('access_token')
    expires = reply.get('expires_in')
    ACCESS_TOKEN = access_token
    current_time = int(time.time()) 
    to_refresh_time = current_time + int(expires) - 5000  # set the time which we have to refresh token, offset by 5000 seconds in case

def ios_get_app_link(search):
    similarity_index = 99
    search = search.lstrip().rstrip().lower()
    result_list = []
    index = 0
    search_formatted = "-".join(search.split())
    url = 'https://theappstore.org/search.php?search={}&platform=software'.format(
        search_formatted)
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    # obtain all app title on the page
    app = soup.find_all('div', class_="appmain")
    for i in app[0:10]:  # create a list of apps in result
        result_list.append(i.find_all('div', class_='apptitle')[
                           0].contents[0].strip().lower())
    # if able to find the app from 1 of the result (must match exactly)
    if search in result_list:
        # find out the index of the item found
        index = result_list.index(search)
    else:
        try:
            for i in range(0, 10):  # loop through the list in case app is not 1st on list
                app_name = app[i].find_all('div', class_='apptitle')[
                    0].contents[0].strip()
                if search in app_name.lower():  # if first on list, or search query is in the name of 1st of the list exit loop
                    index = i
                    break
                else:
                    # use similarity index to determine which app is most likely the 1 we want
                    similarity = similar(app_name.lower(), search)
                    if similarity < similarity_index:
                        similarity_index = similarity
                        index = i
        except Exception as e:
            logging.error(e)
            pass
    app_main = soup.find_all('div', class_="appmain")[index]
    app_link = app_main.find_all('a')[0].get('href')
    app_link = app_link.split('/')
    app_link.pop(3)
    app_link = 'https://' + ('/').join(app_link[2:6])
    app_link = app_link.split('?')[0]
    return app_link


def android_get_app_link(search):
    search = search.lstrip().rstrip()
    index = 0
    search = search.lower()
    result_list = []
    similarity_index = 99  # set to an arbituary high value so that prediction will start
    url = 'https://play.google.com/store/search?q={}&c=apps'.format(
        urllib.parse.quote(search))
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    # obtain all app title on the page
    app = soup.find_all('div', class_='WsMG1c nnK0zc')
    for i in app[0:3]:  # create a list of 1st 3 apps in result
        result_list.append(i.contents[0].lower())
    if search in result_list:  # if able to find the app from 1 of the result
        # find out the index of the item found
        index = result_list.index(search)
    else:
        for i in range(0, 3):  # only list the first 3 apps
            app_name = app[i].contents[0]
            if search in app_name.lower():  # if the result contains the text of the search
                index = i
                break
            else:  # if still cant find text of search in app search, perform similarity check
                similarity = similar(app_name.lower(), search)
                if similarity < similarity_index:
                    similarity_index = similarity
                    index = i
    url_div = soup.find_all('div', class_='b8cIId f5NCO')[index].contents[0]
    url = 'https://play.google.com' + url_div.get('href')
    return url


def game_get_id(search):
    global ACCESS_TOKEN
    global to_refresh_time
    if to_refresh_time == 0:    #only happens when this is first start of the bot
        refresh_token()
        logging.info('No token exists. Token created!')
        print('No token exists. Token created!')
    else:   #bot already running
        current_time = int(time.time()) #get current time
        if current_time >= to_refresh_time: #time expires
            refresh_token()
            logging.info('Token expired. Refreshed token!')
            print('Token expired. Refreshed token!')

    search = search.lstrip().rstrip().lower()
    result_list = []
    index = 0
    similarity_index = 99 # set to an arbituary high value so that prediction will start
    bearer = 'Bearer {}'.format(ACCESS_TOKEN)
    header = {'Client-ID': Config.twitch_client_id,
              'Authorization': bearer}

    data = 'search "{}"; \n fields name;'.format(search)
    url = 'https://api.igdb.com/v4/games/'
    r = requests.post(url, headers=header, data=data)
    if len(json.loads(r.text)) > 0:
        result = json.loads(r.text)[0:3]
        for i in result:
            result_list.append(i.get('name').lower())
        if search in result_list: # if able to find the app from 1 of the result
            index = result_list.index(search) # find out the index of the item found
        
        else:
            for i in range(0,len(result_list)):
                game = result_list[i] #contains name in the result_list
                if search == game.lower():
                    index = i
                    break
                else:
                    similarity = similar(game, search)
                    if similarity < similarity_index:
                        similarity_index = similarity
                        index = i
        id = result[index].get('id')
        return id
    else:
        return None

def get_subreddit_type(subreddit):
    result = ''
    subreddit = subreddit.lower()
    if subreddit in Config.android:
        result = 'android'
    elif subreddit in Config.ios:
        result = 'ios'
    elif subreddit in Config.games:
        result = 'games'
    else:
        pass
    return result


def create_object(subreddit, search):
    subreddit_type = get_subreddit_type(subreddit)
    if subreddit_type == 'android':
        url = android_get_app_link(search)
        if 'https://play.google.com' not in url:
            return None
        else:
            return GooglePlay(url)
    elif subreddit_type == 'ios':
        url = ios_get_app_link(search)
        if 'apps.apple.com' not in url:
            return None
        else:
            return AppStore(url)
    elif subreddit_type == 'games':
        id = game_get_id(search)
        if id is not None:
            return Games(id)
    else:
        return None


def generate_message(subreddit, app_list, count):
    message = ''
    first_app = '' #cache first app in case it is the only app so dont need to request from API again -> Reduces time
    for i in range(0, count):
        app_search = app_list[i]
        app = create_object(subreddit, app_search)
        if i == 0:
            first_app = app #cache first app for use if there is only 1 app searched for adding description
        subreddit_type = get_subreddit_type(subreddit)
        if app is not None:
            if subreddit_type == 'android':
                message += android_gen_msg(app)
            elif subreddit_type == 'ios':
                message += ios_gen_msg(app)
            elif subreddit_type == 'games':
                message += games_gen_msg(app)
            else:
                logging.error(
                    'Error retrieving subreddit type from {}!'.format(subreddit))
        else:
            message += 'Unfortunately, I am unable to find {}. \n\nPerhaps try refining your search term.'.format(app_search)
    if count == 1:
        app = first_app 
        desc = app.get_desc
        if desc is not None:
            desc = desc.split(' ')
            desc = ' '.join(desc[0:35]).replace('\n', ' ') + ' ...'
            message += '> {}'.format(desc)

    if message != '':
        if subreddit_type == 'android':
            message += '\n\n --- \n\n**Legend:** \n\n'
            message += '🏠: Eligble for Family Library \n\n'
            message += '▶️: Available in Play Pass'

        elif subreddit_type == 'ios':
            message += '\n\n --- \n\n**Legend:** \n\n'
            message += '🏠: Eligble for Family Sharing \n\n'
            message += '🕹: Supports Game Center \n\n'
            message += '🎮: Supports Game Controller'

    # Append contact information and additional info
    #message+='--- \n\n **Update:** I am now able to detect `linkme` requests for both Android and iOS store! \n\n'
    message += '\n\n --- \n\n'
    message += '^(Wrong game/app? Reply to my comment with !remove and I will delete this comment) \n\n'
    message += '^(Only comment author can do this) \n\n'
    message += 'To summon me, use `linkme: appname1, appname2` \n\n'
    message += '^(Use the feedback button below if you want me to be enabled on your subreddit.)\n\n'
    message += '^(I currently support Google Play Store, iOS App Store & Steam requests.) \n\n'
    message += '|[Feedback]({})|PunyDev| \n\n'.format(
        'https://www.reddit.com/message/compose?to=PunyDev&subject=Feedback%20about%20linkme%20bot&message=')

    return message


def android_gen_msg(app):  # return message for 1 app each time
    msg = ''
    url = app.get_url
    if app.get_rating is not None:
        rating = str(app.get_rating) + ' ⭐️'
    else:
        rating = 'NA'
    price = app.get_price
    installs = app.get_installs
    if app.get_iap is True:
        price = '{} with IAP'.format(str(price))
    if app.get_size.lower() == 'varies with device':
        size = app.get_size
    else:
        size = app.get_size
    if app.get_playpass is True:
        play_pass = '▶️'
    else:
        play_pass = ''
    if app.get_family is True:
        family = '🏠'
    else:
        family = ''
    ## Prepare message ##
    msg = "**[{}]({})** | {} | {} | {} | {} {} \n\n".format(app.get_name,
                                                               url, rating, price, size, play_pass, family)
    return msg


def ios_gen_msg(app):  # return message for 1 app each time
    msg = ''
    url = app.get_url
    if app.get_rating is not None:
        rating = str(app.get_rating) + ' ⭐️'
    else:
        rating = 'NA'
    price = app.get_price
    if app.get_iap is True:
        price = '{} with IAP'.format(str(price))
    size = app.get_size
    if app.get_family is True:
        family = '🏠'
    else:
        family = ''
    if app.get_gamecenter is True:
        gamecenter = '🕹'
    else:
        gamecenter = ''
    if app.get_controller is True:
        controller = '🎮'
    else:
        controller = ''
    add_on = family + gamecenter + controller
    ## Prepare message ##
    msg = "**[{}]({})** | {} | {} | {} | {} \n\n".format(app.get_name,
                                                         url, rating, price, size, add_on)
    return msg

def games_gen_msg(app):
    msg = ''
    genres = []
    website_msg = []

    try:    #if official site exists, use official website, else use the URL provided by IGDB
        if 'Official' in app.get_website:
            url = app.get_website['Official']
        else:
            url = app.get_url
    except:
        url = app.get_url
    
    if app.get_rating is not None: #get rating
        rating = str(app.get_rating) + ' ⭐️'
    else:
        rating = 'NA'

    if app.get_platforms is not None: #get platform
        platforms = app.get_platforms
        if len(platforms) >= 5:
            platforms = (', ').join(platforms[0:5]) + ' & more'
        else:
            platforms = (', ').join(platforms)
    else:
        platforms = 'NA'

    if app.get_release_year is not None: #get release year
        release_year = app.get_release_year
    else:
        release_year = 'NA'

    if app.get_website is not None:    #get list of websites
        for key, value in app.get_website.items():
            website_msg.append('[{}]({})'.format(key,value))
        website_msg = (', ').join(website_msg) #join all websites in list into 1 string
    else:
        website_msg = 'NA'

    if app.get_genres is not None: #get genres
        for g in app.get_genres:
            if g == 'Role-playing (RPG)': #Convert string to 'RPG' as brackets will cause reddit markdown to ignore superscripts
                g = 'RPG'
            genres.append(g)
        genres = (', ').join(genres)
    else:
        genres = 'NA'
    category = app.get_category

    ## Prepare message ##
    msg = "**[{}]({})** | {} | **Platforms:** {} | **Release Year:** {} | \n\n ^(**Category:** {}) \n\n ^(**Links:** {}) \n\n ^(**Tags:** {})\n\n".format(app.get_name,
                                                         url, rating, platforms, release_year, category, website_msg, genres)
    return msg
