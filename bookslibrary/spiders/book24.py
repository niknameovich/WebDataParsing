import scrapy
from scrapy.http import HtmlResponse

from bookslibrary.items import BookslibraryItem
from scrapy.loader import ItemLoader

class Book24Spider(scrapy.Spider):
    name = 'book24'
    absolute_url = 'https://book24.ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://www.book24.ru/catalog/nauchnaya-fantastika-2051/',
                  'https://www.book24.ru/catalog/fiction-1592/?saleleader=1']

    def parse(self, response: HtmlResponse):

        next_page = response.xpath('//a[contains(@class,"catalog-pagination__item _text")]/@href').extract_first()
        if next_page:
            yield response.follow(f'{Book24Spider.absolute_url}{next_page}', callback=self.parse)

        book_pages = response.xpath('//a[contains(@class,"book-preview__title-link")]//@href').extract()
        for book in book_pages:
            yield response.follow(f'{Book24Spider.absolute_url}{book}', callback=self.parse_book)

    def parse_book(self, response: HtmlResponse):
        loader = ItemLoader(item=BookslibraryItem(), response=response)
        loader.add_xpath('name','.//h1/text()')
        loader.add_xpath('authors','.//a[contains(@itemprop,"author")]/text()')
        loader.add_xpath('price_old', './/div[@class="item-actions__price-old"]/text()')
        loader.add_xpath('price_new', './/b[contains(@itemprop,"price")]/text()')
        loader.add_xpath('rate', './/div[contains(@class,"rate-value")]/text()')
        loader.add_value('link', response.url)
        yield loader.load_item()
        # name = response.xpath('//h1/text()').extract_first()
        # authors = response.xpath('//a[contains(@itemprop,"author")]/text()').extract()
        # price_old = response.xpath('//div[contains(@class,"price-old")]/text()').extract_first()
        # price_new = response.xpath('//b[contains(@itemprop,"price")]/text()').extract_first()
        # rate = response.xpath('//div[contains(@class,"rate-value")]/text()').extract_first()
        # yield BookslibraryItem(name=name, authors=authors, price_old=price_old, price_new=price_new, rate=rate, link = response.url)
