import requests
from bs4 import BeautifulSoup
import json

import logging

logging.basicConfig(level=logging.INFO, filename='output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %I:%M:%S %p')

class GooglePlay:
    def __init__(self, url) :
        self._url = url
        r = requests.get(self._url)
        data = r.text
        self._soup = BeautifulSoup(data, 'html.parser')

    @property
    def get_url(self):
        return self._url + '&referrer=utm_source%3Dreddit-LinkMe_Bot'   #append for app developers to track where the traffic is coming from

    @property
    def get_name(self):
        try:
            return self._soup.find_all('h1', class_='AHFaub')[0].contents[0].text
        except Exception as e:
            logging.warning('Playstore get_name: {}'.format(e))
            return 'NA'
    
    @property
    def get_price(self):
        # price = self._soup.find_all('span', class_='oocvOe')[0].find_all('meta')[-1].get('content')
        # if price == '0':
        #     price = 'Free'
        # return price
        try:
            script = json.loads(self._soup.find_all('script', type='application/ld+json')[0].contents[0])
            price = script.get('offers')[0].get('price')
            if price == '0':
                price = 'Free'
            else:
                price = '$' + price
            return price
        except Exception as error:
            logging.warning('Playstore get_price: {}'.format(error))

    @property
    def get_iap(self):
        try:
            self._soup.find_all('div', class_='bSIuKf')[0].contents[0]
            return True
        except IndexError:
            return False
        except Exception as e:
            logging.warning('Playstore get_iap: {}'.format(e))

    @property
    def get_rating(self):
        try:
            return self._soup.find_all('div', class_="BHMmbe")[0].contents[0]
        except IndexError:
            return None
        except Exception as e:
            logging.warning('Playstore get_rating: {}'.format(e))

    @property
    def get_playpass(self):
        us_url = self._url + '&gl=us'
        r = requests.get(us_url)
        data = r.text
        playpass_soup = BeautifulSoup(data, 'html.parser')
        try:
            playpass_soup.find_all('span', class_='s5dR5e')[0].contents[0]
            return True
        except IndexError:
            return False
        except Exception as e:
            logging.warning('Playstore get_playpass: {}'.format(e))

    @property
    def get_desc(self):
        # try:
        #     return self._soup.find_all('div', attrs={'jsname':'sngebd'})[0].text
        # except IndexError:
        #     return 'NA'
        try:
            script = json.loads(self._soup.find_all('script', type='application/ld+json')[0].contents[0])
            return script.get('description')
        except Exception as e:
            logging.warning('Playstore get_desc: {}'.format(e))
            return 'NA'

    @property
    def get_installs(self):
        index = 0
        family = False
        summary_title = self._soup.find_all('div', class_='BgcNfc')
        if summary_title[0].text.lower() == 'eligible for family library':
            family = True
        for i in range(0, len(summary_title)):
            if summary_title[i].text.lower() == 'installs':
                index = i
                continue
        installs = self._soup.find_all('div', class_='IQ1z0d')
        
        for i in range(0,len(installs)):
            try:
                if family:
                    return installs[index+2].find_all('span', class_='htlgb')[0].text
                else:
                    return installs[index*2].find_all('span', class_='htlgb')[0].text
            except Exception as e:
                logging.warning('Playstore get_installs: {}'.format(e))

    
    @property
    def get_size(self):
        index = 0
        summary_title = self._soup.find_all('div', class_='BgcNfc')
        for i in range(0, len(summary_title)):
            if summary_title[i].text.lower() == 'size': #get which index is the size filed in the list
                index = i
                continue
        size = self._soup.find_all('div', class_='IQ1z0d')
        for i in range(0,len(size)):
            try:
                size = size[index+2].find_all('span', class_='htlgb')[0].text
                if size.lower() == 'varies with device':
                    return size
                else:
                    return size + 'B'
            except Exception as e:
                logging.warning('Playstore get_size: {}'.format(e))

    @property
    def get_family(self):
        family = False
        try:
            summary_title = self._soup.find_all('div', class_='BgcNfc')
            if summary_title[0].text.lower() == 'eligible for family library':
                family = True
            return family
        except Exception as e:
            logging.warning('Playstore get_name: {}'.format(e))
            return 'NA'
    