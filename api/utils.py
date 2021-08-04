from api.GooglePlay import GooglePlay
from api.AppStore import AppStore
import urllib.parse
from bs4 import BeautifulSoup
import requests
import jellyfish
from config import Config
import api
import logging

logging.basicConfig(level=logging.INFO, filename='output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %I:%M:%S %p')

def similar(a,b):
    return jellyfish.levenshtein_distance(a,b)

def ios_get_app_link(search):
    similarity_index = 99
    search = search.lstrip().rstrip().lower()
    result_list = []
    index = 0
    search_formatted = "-".join(search.split())
    url = 'https://theappstore.org/search.php?search={}&platform=software'.format(search_formatted)
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    app = soup.find_all('div', class_="appmain") #obtain all app title on the page
    for i in app[0:3]: #create a list of apps in result
        result_list.append(i.find_all('div', class_='apptitle')[0].contents[0].strip().lower())
    if search in result_list: #if able to find the app from 1 of the result
        index = result_list.index(search) #find out the index of the item found
    else:
        try:
            for i in range(0,3): # loop through the list in case app is not 1st on list
                app_name = app.find_all('div', class_='apptitle')[0].contents[0].strip()
                if search in app_name.lower(): #if first on list, or search query is in the name of 1st of the list exit loop
                    index = i
                    break
                else:
                    similarity = similar(app_name.lower(), search) #use similarity index to determine which app is most likely the 1 we want
                    if similarity < similarity_index:
                        similarity_index = similarity
                        index = i
        except:
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
    similarity_index = 99 #set to an arbituary high value so that prediction will start
    url = 'https://play.google.com/store/search?q={}&c=apps'.format(urllib.parse.quote(search))
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    app = soup.find_all('div', class_='WsMG1c nnK0zc') #obtain all app title on the page
    for i in app[0:3]:  #create a list of apps in result
        result_list.append(i.contents[0].lower())
    if search in result_list: #if able to find the app from 1 of the result
        index = result_list.index(search) #find out the index of the item found
    else:
        for i in range(0,3): #only list the first 3 apps
            app_name = app[i].contents[0]
            if search in app_name.lower(): # if the result contains the text of the search
                index = i
                break
            else: #if still cant find text of search in app search, perform similarity check
                similarity = similar(app_name.lower(), search)
                if similarity < similarity_index:
                    similarity_index = similarity
                    index = i
    url_div = soup.find_all('div', class_='b8cIId f5NCO')[index].contents[0]
    url = 'https://play.google.com' + url_div.get('href')
    return url

def get_subreddit_type(subreddit):
    result = ''
    if subreddit in Config.android:
        result = 'android'
    elif subreddit in Config.ios:
        result = 'ios'
    elif subreddit in Config.pc:
        result = 'pc'
    else:
        result = 'testing'
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
    else:
        url = ios_get_app_link(search)
        return AppStore.App(url) #for testing purposes, change as required

def generate_message(subreddit, app_list, count):
    message = ''
    for i in range(0, count):
        app_search = app_list[i]
        app = create_object(subreddit, app_search)
        subreddit_type = get_subreddit_type(subreddit)
        if app is not None:
            if subreddit_type == 'android':
                message+=android_gen_msg(app)
            elif subreddit_type == 'ios':
                message+=ios_gen_msg(app)
            else:
                logging.error('Error retrieving subreddit type from {}!'.format(subreddit))
        else:
            message+= 'I cannot find the app named {}'.format(app_search)
    if count == 1:
        app = create_object(subreddit, app_list[0])
        desc = app.get_desc
        desc = desc.split(' ')
        desc = ' '.join(desc[0:35]).replace('\n', ' ') + ' ...'
        message+= '> {}'.format(desc)
    
    if message != '':
        if subreddit_type == 'android':
            message+="\n\n --- \n\n**Legend:** \n\n ▶️: Available in Play Pass \n\n 🏠: Eligble for Family Library"
        elif subreddit_type == 'ios':
            #message+='\n\n --- \n\n Hi! I am new and might be rough around the edges. Kindly use the feedback button below to inform me of any issues. Thanks! \n\n'
            pass
    
    ## Append contact information and etc info
    #message+='--- \n\n **Update:** I am now able to detect `linkme` requests for both Android and iOS store! \n\n'
    message+='\n\n --- \n\n'
    message+='^(I am a bot which retrieves information about your games or apps for you, to the best of my ability.)\n\n'
    message+='To summon me, use `linkme: appname1, appname2` \n\n'
    message+='^(Use the feedback button below if you want me to be enabled on your subreddit.)\n\n'
    message+='^(I currently support Google Play Store & iOS App Store requests.) \n\n'
    message+='|[Feedback]({})|PunyDev| \n\n'.format('https://www.reddit.com/message/compose?to=PunyDev&subject=Feedback%20about%20linkme%20bot&message=')

    return message

def android_gen_msg(app):   #return message for 1 app each time
    msg = ''
    url = app.get_url
    if app.get_rating is not None:
        rating = app.get_rating
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
    msg = "**[{}]({})** | {} ⭐️ | {} | {} | {} {} \n\n".format(app.get_name,url,rating,price, size, play_pass, family)
    return msg

def ios_gen_msg(app): #return message for 1 app each time
    msg = ''
    url = app.get_url
    if app.get_rating is not None:
        rating = app.get_rating
    else:
        rating = 'NA'
    price = app.get_price
    if app.get_iap is True:
        price = '{} with IAP'.format(str(price))
    size = app.get_size
    ## Prepare message ##
    msg = "**[{}]({})** | {} | {} | {} \n\n".format(app.get_name,url,rating,price, size)
    return msg