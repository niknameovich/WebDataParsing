import scrapy
from scrapy.http import HtmlResponse

from bookslibrary.items import BookslibraryItem
from scrapy.loader import ItemLoader


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    absolute_url = 'https://www.labirint.ru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/genres/2304/', 'https://www.labirint.ru/genres/2828/']

    def parse(self, response: HtmlResponse):

        next_page = response.xpath('//a[contains(@class,"pagination-next")]/@href').extract_first()
        if next_page:
            yield response.follow(f'{response.url.split("?")[0]}{next_page}', callback=self.parse)

        book_pages = response.xpath('//a[contains(@class,"link")]//@href').extract()
        for book in book_pages:
            yield response.follow(f'{LabirintSpider.absolute_url}{book}', callback=self.parse_book)

    def parse_book(self, response: HtmlResponse):
        loader = ItemLoader(item=BookslibraryItem(), response=response)
        loader.add_xpath('name', './/h1/text()')
        loader.add_xpath('authors', '//div[contains(@class,"authors")]/a/text()')
        loader.add_xpath('price_old', '//span[contains(@class,"priceold")]/text()')
        loader.add_xpath('price_new', '//span[contains(@class,"pricenew")]/text()')
        loader.add_xpath('rate', '//div[@id="rate"]/text()')
        loader.add_value('link', response.url)
        yield loader.load_item()
        # name = response.xpath('//h1/text()').extract_first()
        # authors = response.xpath('//div[contains(@class,"authors")]/a/text()').extract()
        # price_old = response.xpath('//span[contains(@class,"priceold")]/text()').extract_first()
        # price_new = response.xpath('//span[contains(@class,"pricenew")]/text()').extract_first()
        # rate = response.xpath('//div[@id="rate"]/text()').extract_first()
        # yield BookslibraryItem(name=name, authors=authors, price_old=price_old, price_new=price_new, rate=rate, link = response.url)
