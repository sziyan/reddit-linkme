from config import Config
import requests
import json
from datetime import datetime
import api.utils


class Games:
    def __init__(self, id):
        self._id = id
        access_token = api.utils.ACCESS_TOKEN
        bearer = 'Bearer {}'.format(access_token)
        self._header = {'Client-ID': Config.twitch_client_id, 'Authorization': bearer}
        payload = 'fields *; \nwhere id = {};'.format(self._id)
        url = 'https://api.igdb.com/v4/games/'
        r = requests.post(url, headers=self._header, data=payload)
        self._result = json.loads(r.text)[0]
    
    def send_request(self, url, payload):
        r = requests.post(url, headers=self._header, data=payload)
        return json.loads(r.text)[0]
    
    def categorize(self,id):
        if id == 1:
            name = 'Official'
        elif id == 2:
            name = 'Wikia'
        elif id == 13:
            name = 'Steam'
        elif id == 16:
            name = 'Epic Games'
        elif id == 17:
            name = 'GOG' 
        return name

    @property
    def get_id(self):
        return self._id

    @property
    def get_name(self):
        return self._result.get('name')
        
    @property
    def get_desc(self):
        try:
            return self._result.get('summary')
        except:
            return None

    @property
    def get_genres(self):
        try:
            genres_list = []
            url = 'https://api.igdb.com/v4/genres'
            genres = self._result.get('genres')
            for g in genres:
                payload = 'fields name; \nwhere id = {};'.format(g)
                result = self.send_request(url, payload)
                genres_list.append(result.get('name'))
            if len(genres_list) > 0:
                return genres_list
            else:
                return None
        except:
            return None

    @property
    def get_platforms(self):
        platforms = []
        url = 'https://api.igdb.com/v4/platforms/'
        try:
            platform_ids = self._result.get('platforms')
            for id in platform_ids:
                payload = 'fields abbreviation,websites; \nwhere id = {};'.format(id)
                result = self.send_request(url, payload)
                platforms.append(result.get('abbreviation'))
            if len(platforms) != 0:
                return platforms
            else:
                return None
        except:
            return None

    @property
    def get_website(self):
        allowed_category = [1, 2, 13, 16,17]
        website_list = self._result.get('websites')
        websites = {}
        url = 'https://api.igdb.com/v4/websites'
        try:
            for id in website_list:
                payload = 'fields category, url; \nwhere id = {};'.format(id)
                result = self.send_request(url, payload)
                category_id = result.get('category')
                if category_id in allowed_category:
                    category_name = self.categorize(category_id)
                    websites[category_name] = result.get('url')
            return websites
        except:
            return None

    @property
    def get_url(self):
        return self._result.get('url')

    @property
    def get_rating(self):
        try:
            return int(round(self._result.get('aggregated_rating'),0))
        except:
            return None

    @property
    def get_release_year(self):
        try:
            r = self._result.get('first_release_date')
            return datetime.utcfromtimestamp(r).strftime('%Y')
        except:
            return None

    @property
    def get_keywords(self):
        try:
            keyword_list = self._result.get('keywords')
            keywords = []
            url = 'https://api.igdb.com/v4/keywords'
            for id in keyword_list:
                payload = 'fields name; \n where id = {};'.format(id)
                result = self.send_request(url, payload)
                keywords.append(result.get('name'))
            if len(keywords) > 0:
                return keywords
            else:
                return None
        except:
            return None

    @property
    def get_category(self):
        try:
            category_id = self._result.get('category')
            id_name = {0: 'Main Game',
            1:'DLC',
            2:'Expansion',
            3:'Bundle',
            8:'Remake',
            9: 'Remaster',
            11: 'Port'}
            if category_id in id_name:
                return id_name[category_id]
            else:
                return 'Others'
        except:
            return 'Others'

