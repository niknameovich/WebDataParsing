# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline



class GardentechPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['books']

    def process_item(self, item, spider):
        current_collection = self.db[spider.name]
        if item['characteristics']:
            item['characteristics'] = self.process_characteristics(item['characteristics'])
        for key in item.keys():
            if type(item[key]) is None:
                dict(item).pop(key)
        current_collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
        return item

    def process_characteristics(self,chars: list):
        terms = [val for index, val in enumerate(chars) if index % 2 == 0]
        defs = [val for index, val in enumerate(chars) if index % 2 != 0]
        return dict(zip(terms, defs))


class PhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None, *, item=None):
        return f'{item["name"].replace("/","")}/{request.url.split("/")[-1]}'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
