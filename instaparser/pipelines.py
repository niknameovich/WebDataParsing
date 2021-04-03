# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from pymongo import MongoClient


class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['insta']

    def process_item(self, item, spider):
        current_collection = self.db[spider.name]
        # если на нас подписан исследумый пользователь
        if 'follower' in item.keys():
            # добавить наш ИД в массив для подписок исследуемого пользователя
            current_collection.update_one({'_id': item['follower']}, {'$push': {'followed': item['_id']}})
            del item['follower']
        current_collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item
