# Reddit LinkMe Bot

This bot watches subreddit comments for the keyword `linkme: query1, query2` and replies with relevant information. 

This bot currently supports the following platforms:

- Google Play Store via web scraping their playstore pages
- iOS App Store via web scraping [The AppStore](https://theappstore.org/) and the web page of the app
- Steam/console games via [IGDB](https://www.igdb.com/) API

## Configuration

Before starting the bot, we have to create our configuration file.

Create config.py in the root folder with the following content:

Subreddits under android will be returned with results from Google Play Store

Subreddits under ios will be returned with results from Apple App Store

Subreddits under pc will be returned with results from IGDB

```python
class Config:
    #subreddits to monitor
    android = ['android']
    ios = ['ios']
    pc = ['steam']
    subreddit = ios + android + pc

    #twitch api for IGDB
    twitch_client_id = ''
    twitch_client_secret = ''

    #reddit bot credentials
    username = ''   #reddit bot username
    password = ''   #reddit bot password
    client_id = ''
    client_secret = ''
   
   #additional configurations
    max_apps = 15   #max number of app/games queries to retrieve per comment
    bot_owner = ''  #reddit username of bot owner. Used to overwrite deletion of bot comment replies with !remove

```

Obtain twitch client ID and secret [here](https://api-docs.igdb.com/#authentication)

Obtain reddit client ID and secret using scrip with instructions [here](https://praw.readthedocs.io/en/stable/getting_started/authentication.html)

Install dependencies in requirements.txt

`pip install -r requirements.txt`

Finally, start the bot in your console

`python app.py`

## Invoking the bot
The bot will monitor all subreddits in the configuration file, and depending on which category the subreddit is in, will reply with different information.

Reply to a submission or comment with `linkme: game1, app1`