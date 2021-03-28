import scrapy
from scrapy.http import HtmlResponse
from gardentech.items import GardentechItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    absolute_path = 'https://leroymerlin.ru/'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/sadovaya-tehnika']

    def __init__(self):
        self.current_page = 1
        self.total_pages = 0
        super().__init__()

    def parse(self, response: HtmlResponse):
        if self.total_pages == 0:
            self.total_pages = int(response.xpath('//uc-pagination[@slot="pagination"]/@total').extract_first())
        if self.current_page <= self.total_pages:
            self.current_page += 1
            yield response.follow(f'{response.url}/"?page={self.current_page}"', callback=self.parse)

        product_pages = response.xpath('//product-card/@data-product-url').extract()
        for product in product_pages:
            yield response.follow(f'{LeroymerlinSpider.absolute_path}{product}', callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=GardentechItem(), response=response)
        loader.add_xpath('name', './/h1/text()')
        loader.add_xpath('photos', './/picture[@slot="pictures"]/source[@itemprop="image"]/@data-origin')
        loader.add_xpath('characteristics', '//div[contains(@class,"def-list__group")]/dt/text() |'
                                            ' //div[contains(@class,"def-list__group")]/dd/text()')
        loader.add_xpath('price', './/span[@slot="price"]/text()')
        loader.add_xpath('currency', './/span[@slot="currency"]/text()')
        loader.add_xpath('UOM', './/span[@slot="unit"]/text()')
        loader.add_value('link', response.url)
        yield loader.load_item()
