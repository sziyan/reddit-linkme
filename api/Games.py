from config import Config
import requests
import json
from datetime import datetime


class Games:
    def __init__(self, id, access_token):
        self._id = id
        bearer = 'Bearer {}'.format(access_token)
        self._header = {'Client-ID': Config.twitch_client_id, 'Authorization': bearer}
        payload = 'fields *; \nwhere id = {};'.format(self._id)
        url = 'https://api.igdb.com/v4/games/'
        r = requests.post(url, headers=self._header, data=payload)
        self._result = json.loads(r.text)[0]
    
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
    def get_platforms(self):
        platforms = []
        url = 'https://api.igdb.com/v4/platforms/'
        platform_ids = self._result.get('platforms')
        for id in platform_ids:
            payload = 'fields abbreviation,websites; \nwhere id = {};'.format(id)
            r = requests.post(url, headers=self._header, data=payload)
            result = json.loads(r.text)[0]
            platforms.append(result.get('abbreviation'))
        if len(platforms) != 0:
            platforms = (', ').join(platforms)
            return platforms
        else:
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
                r = requests.post(url, headers=self._header, data=payload)
                result = json.loads(r.text)[0]
                category_id = result.get('category')
                if category_id in allowed_category:
                    category_name = self.categorize(category_id)
                    websites[category_name] = result.get('url')
            return websites
        except:
            return None
    
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


