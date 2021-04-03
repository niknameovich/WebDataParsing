from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from spiders.instagram import InstagramSpider
import settings

if __name__ == '__main__':
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
    if len(user_to_parse) > 0:
        process.crawl(InstagramSpider(user_to_parse))
        process.start()
    else:
        print('Необходимо указать хотя бы один логин')
