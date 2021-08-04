from api import utils as util
from api.GooglePlay import GooglePlay
from api.AppStore import AppStore
from bs4 import BeautifulSoup
import praw
from config import Config
import re
import markdown
import logging

logging.basicConfig(level=logging.INFO, filename='output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %I:%M:%S %p')
logging.info("Bot started successfully")
print('Bot started successfully')


reddit = praw.Reddit(
    client_id=Config.client_id,
    client_secret=Config.client_secret,
    password=Config.password,
    user_agent="GooglePlayLinks_Bot by u/PunyDev",
    username=Config.username,
)

link_me_regex = re.compile("\\blink[\s]*me[\s]*:[\s]*(.*?)(?:\.|;|$)", re.M | re.I)

def get_clean_comment(text):
    htmltext = markdown.markdown(text)
    soup = BeautifulSoup(htmltext, features="lxml")
    output = soup.get_text()
    return output

def get_no_apps(linkme_requests):
    app_count = 0
    for rq in linkme_requests:
        for item in rq.split(','):
            if item != '': #if not empty
                app_count += 1
    return app_count

def get_all_app_requests(linkme_requests):
    apps_list = []
    for rq in linkme_requests:
        for item in rq.split(","):
            if item != '': #if not empty
                apps_list.append(item)
    return apps_list

link_me_regex = re.compile("\\blink[\s]*me[\s]*:[\s]*(.*?)(?:\.|;|$)", re.M | re.I)

subreddit = reddit.subreddit(("+").join(Config.subreddit))

try:
    for comments in subreddit.stream.comments(skip_existing=True):
        if comments.author.name == Config.username:
            continue
        else:
            message = "" # creating blank message
            body = comments.body.lower()
            clean_text = get_clean_comment(body)
            link_me_requests = link_me_regex.findall(clean_text)
            #app_count = get_no_apps(link_me_requests) #number of apps in the linkme request
            app_list = get_all_app_requests(link_me_requests) #list of apps in the linkme request
            app_count = len(app_list)
            count = 1 #number of apps to search, changes accordingly if max apps has reached or not
            if app_count > 0:
                logging.info("{} is searching for {} app(s) in /r/{}: {}".format(comments.author.name, app_count,comments.subreddit.display_name, ",".join(app_list)))
                print("{} is searching for {} app(s): {}".format(comments.author.name, app_count, ",".join(app_list)))
            else: #no app being searched, by right its not possible
                continue
            if app_count > Config.max_apps:
                msg = "You have searched for {} apps. I will only link to the first {} apps.\n\n".format(app_count, Config.max_apps)
                message +=msg
                count = Config.max_apps #if exceed max number of apps, will only count 15
            else:
                count = app_count
            message+=util.generate_message(comments.subreddit.display_name, app_list, count)
            if message != "":
                comments.reply(message)
                logging.info('{} completed app search successfully.'.format(comments.author.name))
                print('{} completed app search successfully.'.format(comments.author.name))
            else:
                logging.info("{} searched for an empty game.".format(comments.author.name))
except praw.exceptions.APIException as api_exception:
    logging.error(
        "API Error: {} - {} - {}".format(api_exception.error_type, api_exception.field, api_exception.message))
    print(
        "API Error: {} - {} - {}".format(api_exception.error_type, api_exception.field, api_exception.message))
    pass
except praw.exceptions.ClientException:
    logging.error("Client Error: Client exception")
    pass
except praw.exceptions.PRAWException as e:
    logging.error("PRAW Error: {}".format(e))
    pass
except Exception as e:
    logging.error("Error: {}".format(e))
    pass