from bs4 import BeautifulSoup
import requests
import json
import re
import logging

logging.basicConfig(level=logging.INFO, filename='output.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %I:%M:%S %p')

class AppStore:
    def __init__(self, url):
        self._url = url
        r = requests.get(self._url)
        data = r.text
        self._soup = BeautifulSoup(data, 'html.parser')
    
    @property
    def get_url(self):
        return self._url
   
    @property
    def get_rating(self):
        try:
            rating_votes = self._soup.find_all('figcaption', class_='we-rating-count star-rating__count')[0].contents[0]
            rating_votes = re.findall('([\w\W]+) Ratings', rating_votes)[0]
            rating_votes = rating_votes.split('•')
            score = rating_votes[0]
            rating = score.split()[0]
            return rating
        except IndexError:
            return None
        except Exception as e:
            logging.warning('Appstore get_rating: {}'.format(e))

    @property
    def get_price(self):
        try:
            price = self._soup.find_all('li', class_='inline-list__item inline-list__item--bulleted app-header__list__item--price')[0].contents[0]
        except IndexError:
            price = 'Apple Arcade'
        return price

    @property
    def get_iap(self):
        try:
            self._soup.find_all('li', class_='inline-list__item inline-list__item--bulleted app-header__list__item--in-app-purchase')[0].contents[0]
            return True
        except IndexError:
            return False
        except Exception as e:
            logging.warning('Appstore get_iap: {}'.format(e))

    @property
    def get_desc(self):
        try:
            desc = self._soup.find_all('script', class_="ember-view")[0].contents[0]
            desc = json.loads(desc)
            return desc.get('description')
        except IndexError:
            return None
        except Exception as e:
            logging.warning('Appstore get_desc: {}'.format(e))

    @property
    def get_subtitle(self):
        try:
            subtitle = self._soup.find_all('h2', class_="product-header__subtitle app-header__subtitle")[0].contents[0].strip()
            return subtitle
        except IndexError:
            return None
        except Exception as e:
            logging.warning('Appstore get_subtitle: {}'.format(e))

    @property
    def get_size(self):
        try:
            size = self._soup.find_all('dd', class_='information-list__item__definition')[1].contents[0]
            return size
        except Exception as e:
            logging.warning('Appstore get_size: {}'.format(e))
            return 'NA'


    @property
    def get_name(self):
        try:
            result = self._soup.find_all('script', class_="ember-view")[0].contents[0]
            result = json.loads(result)
            return result.get('name')
        except IndexError:
            return None
        except Exception as e:
            logging.warning('Appstore get_name: {}'.format(e))

    @property
    def get_family(self):
        support_list = []
        try:
            source = self._soup.find_all('div', class_='supports-list__item__copy')
            for s in source:
                support_list.append(s.find('h3').text.strip().lower())
            if 'family sharing' in support_list:
                 return True
            else:
                return False
        except IndexError:
            return False
        except Exception as e:
            logging.warning('Appstore get_family: {}'.format(e))
        
    @property
    def get_gamecenter(self):
        support_list = []
        try:
            source = self._soup.find_all('div', class_='supports-list__item__copy')
            for s in source:
                support_list.append(s.find('h3').text.strip().lower())
            if 'game center' in support_list:
                 return True
            else:
                return False
        except IndexError:
            return False
        except Exception as e:
            logging.warning('Appstore get_gamecenter: {}'.format(e))

    @property
    def get_controller(self):
        support_list = []
        try:
            source = self._soup.find_all('div', class_='supports-list__item__copy')
            for s in source:
                support_list.append(s.find('h3').text.strip().lower())
            if 'game controllers' in support_list:
                 return True
            else:
                return False
        except IndexError:
            return False
        except Exception as e:
            logging.warning('Appstore get_controller: {}'.format(e))