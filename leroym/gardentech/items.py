# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


def convert_price_to_float(price):
    return float(price.replace(' ', ''))


def clean_data(args):
    args = args.replace('\n', '').strip()
    pattern_int = re.compile('^\d+$')
    pattern_float = re.compile('^\d*[.]\d*$')
    if pattern_int.match(args):
        return int(args)
    elif pattern_float.match(args):
        return float(args)
    else:
        return args


class GardentechItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(output_processor=MapCompose())
    characteristics = scrapy.Field(input_processor=MapCompose(clean_data))
    price = scrapy.Field(input_processor=MapCompose(convert_price_to_float), output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    UOM = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()
    pass
