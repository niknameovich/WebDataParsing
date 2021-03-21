import requests
from fake_useragent import UserAgent
from lxml import html
from pymongo import MongoClient
import re


class Parser:
    rand_agent = {'User-Agent': UserAgent().random}

    def __init__(self):
        self.mclient = MongoClient('localhost', 27017)
        self.testdb = self.mclient['news_db']
        self.collection = self.testdb.news_collection

    def parse_data(self, url):
        response = requests.get(url['baseurl'], headers=Parser.rand_agent)
        # условие корректности ответа для HH
        if response.status_code < 400:
            root = html.fromstring(response.text)
            result = root.xpath(self.aggregate_xpath(url['xpath']))
            self.get_result_item(result, url['parsing'], url['baseurl'])
        else:
            pass

    def get_result_item(self, elements, path_dict, baseurl):
        for item in elements:
            result_v = {}
            for key, value in path_dict.items():
                result_v[key] = self.get_item_key(item.xpath(self.aggregate_xpath(value)))
            result_v['site'] = baseurl
            self.write_result_to(result_v, self.collection)

    def get_item_key(self, result_xpath):
        if type(result_xpath) is list and len(result_xpath)>0:
            notemp = list(filter(lambda x: len(x) > 0, set(result_xpath)))
            if len(notemp) > 1:
                return None
            else:
                return notemp[0]

    def aggregate_xpath(self, mxpath):
        if type(mxpath) is list:
            result = " | ".join(mxpath)
        else:
            result = mxpath
        return result

    def write_result_to(self, tag, collection):
        collection.update_one({'news_ref': tag['news_ref']}, {'$set': tag}, upsert=True)


url_list = [{'baseurl': 'https://yandex.ru/news/',
             # элемент для поиска всех Tag  содержащих вакансии
             'xpath': "//article[contains(@class,'mg-card')]",
             # элементы поиска в ответе
             'parsing': {
                 'news_ref': ".//a[contains(@class,'mg-card__link')]/@href",
                 'source': ".//div[contains(@class,'mg-card-source')]"
                           "/span[contains(@class,'mg-card-source__source')]/a/text()",
                 'publish_date': ".//div[contains(@class,'mg-card-source')]"
                                 "/span[contains(@class,'mg-card-source__time')]/text()",
                 'header': ".//a[contains(@class,'mg-card__link')]/h2/text()"
             }
             },
            {'baseurl': 'https://lenta.ru/',
             'xpath': ['//div[contains(@class,"b-tabloid__topic_news")]', '//div[contains(@class,"article")]',
                       '//div[contains(@class,"b-tabloid__topic article")]',
                       '//div[contains(@class,"b-yellow-box__wrap")]/div[contains(@class,"item")]'],
             'parsing': {
                 'news_ref': ['./div[contains(@class,"titles")]/h3/a/@href',
                              './/a[@data-partslug="text"]/@href', './a/@href'],
                 'publish_date': ['.//div[contains(@class,"g-date")]/span[contains(@class,"g-date")]/text()'],
                 'header': ['./div[contains(@class,"titles")]/h3/a/span/text()',
                            './/span[contains(@class,"b-tabloid__headline")]/text()',
                            './a/text()']
             }
             },
            {'baseurl': 'https://news.mail.ru/',
             'xpath': ['//div[contains(@class,"newsitem")]', '//li[contains(@class,"list__item")]',
                       '//div[contains(@class,"daynews__item")]',
                       '//div[contains(@class,"collections__item")]'],
             'parsing': {
                 'news_ref': ['./a[contains(@class,"newsitem__title")]/@href',
                              './/a[contains(@class,"link")]/@href', './a/@href',
                              './/a[contains(@class,"collections__wrapper")]/@href'],
                 'publish_date': ['.//div[contains(@class,"newsitem__params")]/span[@datatime]/@datatime'],
                 'header': ['.//span[contains(@class,"newsitem__title-inner")]/text()',
                            './/span[contains(@class,"link__text")]/text()',
                            './/span[contains(@class,"photo__title")]/text()',
                            './/span[contains(@class,"collections__title")]/text()']
             }
             }
            ]

my_parser = Parser()
for url in url_list:
    my_parser.parse_data(url)
