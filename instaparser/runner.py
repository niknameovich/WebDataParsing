from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from pymongo import MongoClient
from spiders.instagram import InstagramSpider
import settings

if __name__ == '__main__':

    client = MongoClient('localhost', 27017)
    db = client['insta']
    collection = db[InstagramSpider.name]
    user_to_parse = list()
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)

    while True:
        current = input('для запуска сборщика введите "q"\r\nвведите логин пользователя - ')
        if current == 'q':
            break
        elif current not in user_to_parse:
            user_to_parse.append(current)

    process.crawl(InstagramSpider, user=user_to_parse)
    process.start()

    followers = list(collection.find({'username': user_to_parse[0]}, {'followed': 1}))
    # вывод количества подписчиков
    followed = collection.find({'followed': followers[0]['_id']})
    print(len(list(followed)))
    # вывод количества подписок
    follower_docs = collection.find({'_id': {'$in': followers[0]['followed']}})
    print(len(list(follower_docs)))

