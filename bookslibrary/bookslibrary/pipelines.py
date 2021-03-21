# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient


class BookslibraryPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['books']

    def process_item(self, item, spider):
        current_collection = self.db[spider.name]
        for key in item.keys():
            if type(item[key]) is None:
                dict(item).pop(key)
        current_collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
        return item
