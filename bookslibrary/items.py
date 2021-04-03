# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst,Join



def clean_name(name: str):
    return name.split(':')[-1].replace('\n', '').replace('\r', '').strip()


def get_int_price(price):
    if price:
        if ' ' in price:
            try:
                return int(price.split()[0])
            except Exception as e:
                print(e)
        else:
            try:
                return int(price)
            except Exception as e:
                print(e)



class BookslibraryItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(input_processor=MapCompose(clean_name), output_processor=Join())
    price_old = scrapy.Field(input_processor=MapCompose(get_int_price), output_processor=TakeFirst())
    price_new = scrapy.Field(input_processor=MapCompose(get_int_price), output_processor=TakeFirst())
    rate = scrapy.Field(output_processor=TakeFirst())
    authors = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    pass
