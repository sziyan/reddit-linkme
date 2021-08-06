# Reddit LinkMe Bot

This bot watches subreddit comments for the keyword `linkme: query1, query2` and replies with relevant information. 

This bot currently supports the following platforms:

- Google Play Store via web scraping their playstore pages
- iOS App Store via web scraping [The AppStore](https://theappstore.org/) and the web page of the app
- Steam/console games via [IGDB](https://www.igdb.com/) API

## Configuration

Before starting the bot, we have to configure our configuration file.

Create config.py in the root folder with the following content:

```python
class Config:
    #subreddit to monitor
    android = ['androidgaming', 'androidapps']
    ios = ['iosgaming', 'iosapps', 'applearcade']
    pc = ['gamesuggestion']
    subreddit = ios + android + pc

    #twitch api for IGDB
    twitch_client_id = ''
    twitch_client_secret = ''

    #reddit bot credentials
    username = ''
    password = ''
    client_id = ''
    client_secret = ''
   
   #additional configurations
    max_apps = 15

```

Obtain twitch & reddit API from the respective websites  