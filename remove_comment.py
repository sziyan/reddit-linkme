import praw
import logging
import os

try:
    from config import Config
except:
    pass

## set config variables
try:
    client_id = Config.client_id or os.environ.get('CLIENT_ID')
    client_secret = Config.client_secret or os.environ.get('CLIENT_ID')
    password = Config.password or os.environ.get('PASSWORD')
    username = Config.username or os.environ.get('USERNAME')
    bot_owner = Config.bot_owner or os.environ.get('BOT_OWNER')
except AttributeError or NameError:
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_ID')
    password = os.environ.get('PASSWORD')
    username = os.environ.get('USERNAME')
    bot_owner = os.environ.get('BOT_OWNER')


reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    password=password,
    user_agent="{} by u/PunyDev".format(username),
    username=username
)

logging.basicConfig(level=logging.INFO, filename='output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %I:%M:%S %p')
logging.info("Streaming inbox for comment replies")
print('Streaming inbox for comment replies')

try:
    
    for message in reddit.inbox.stream(skip_existing=True):
        if message.was_comment is True:
             # General workflow:
            # 1. Stream for inbox that is a comment reply - done
            # 2. If is comment reply, check the comment message if contains !remove keyword. - done
            # 3. If contains keyword, check 1st level parent comment if its posted by our bot, get parent comment ID and comment author name as well
            # 4. Get 2nd layer of parent comment author name. If same as reply comment author, proceed to delete 1st level parent comment

            comment_id = message.id
            comment_author = message.author
            comment_body = message.body
        
            if '!remove' in comment_body:   #the comment replied has message body !remove
                firstLevelComment = reddit.comment(id=message.parent_id)    #1st level comment object
                firstLevelAuthor = firstLevelComment.author.name
                subreddit = firstLevelComment.subreddit.display_name
                if firstLevelAuthor == username: #signify message is posted by bot
                    secondLevelComment = reddit.comment(id=firstLevelComment.parent_id) #2nd level comment object
                    secondLevelAuthor = secondLevelComment.author.name
                    if secondLevelAuthor == comment_author.name or comment_author.name.lower() == bot_owner.lower():
                        firstLevelComment.delete()
                        logging.info('{} deleted comment in r/{}'.format(comment_author.name, subreddit))
                        print('{} deleted comment in r/{}'.format(comment_author.name, subreddit))     
                      
except Exception as e:
    logging.error('Inbox Streaming Error: {}'.format(e))
    print(e)