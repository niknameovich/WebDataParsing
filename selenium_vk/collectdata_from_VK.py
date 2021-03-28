from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
from urllib import parse
import datetime
import time


def process_item(item, collection):
    current_collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)


def get_date(param):
    result = param.split()
    if 'сегодня' in result:
        current_date = datetime.date.today()
        param = f'{current_date.day}.{current_date.month}.{current_date.year}-{result[-1]}'
    elif 'вчера' in result:
        current_date = datetime.date.today()
        # слишком много вариантов обработки для дз ... проверки на первый день месяца/года
        # конвертация различных форматов дат в текущем месяце в предыдущих года
        param = f'{current_date.day - 1}.{current_date.month}.{current_date.year}-{result[-1]}'
    return param

# получение прямых ссылок на изображения в посте
def get_image_links(element):
    return ['https:'+img.split(':')[-1].replace('url("', '').replace('")', '')
            for img in element.get_attribute('style').split(';') if 'url(' in img][0]

# поэлементная обработка постов
def get_item_dictionary(elements):
    item = dict()
    for element in elements:
        item['text'] = element.find_element_by_class_name('wall_text').text
        item['date'] = get_date(element.find_element_by_xpath('.//span[@class="rel_date"]').text)
        item['img'] = list(map(lambda x: get_image_links(x),
                               element.find_elements_by_class_name("image_cover")))
        item['link'] = parse.urljoin(base_url, element.find_element_by_xpath('.//a[@class="post_link"]')
                                     .get_attribute('href'))
        item['likes'] = int(element.find_element_by_xpath('.//a[contains(@class,"_like")]')
                            .get_attribute('data-count')
                            .replace('K', '00').replace('.', ''))
        item['shares'] = int(element.find_element_by_xpath('.//a[contains(@class,"_share")]')
                             .get_attribute('data-count')
                             .replace('K', '00').replace('.', ''))
        item['views'] = int(element.find_element_by_xpath('.//div[contains(@class,"_views")]').text.split()[0]
                            .replace('K', '00').replace('.', ''))
        yield item


group_id = 'minifutbolnnino'
search_value = input('введите поисковый запрос: ')
base_url = "https://vk.com/"
timeout = 10
client = MongoClient('localhost', 27017)
db = client['vk_posts']
current_collection = db['posts']
url = parse.urljoin(base_url, group_id)
driver = webdriver.Edge()
driver.get(url)
# переход на страницу поиска, кнопка поиска закрыта баннером
search_button = driver.find_element_by_class_name('ui_tab_search').get_attribute('href')
driver.get(parse.urljoin(base_url, search_button))
search_input = driver.find_element_by_id('wall_search')
search_input.send_keys(search_value)
search_input.send_keys(Keys.ENTER)

while True:
    # если вдруг появится окно запроса регистрации
    try:
        notnow = driver.find_element_by_class_name('JoinForm__notNow')
        if notnow:
            notnow.click()
    except Exception as e:
        print(e)
    finally:
        driver.find_element_by_tag_name("html").send_keys(Keys.END)
        # ожидание обновления скрытого элемента загрузки доп элементов
        time.sleep(1)
        button = driver.find_element_by_id('fw_load_more')
        style = button.get_attribute('style')
        # display: none; - критерий конца прокрутки
        if 'none' in style:
            break

posts = driver.find_element_by_id("page_wall_posts").find_elements_by_xpath(
    '//div[contains(@class,"post--with-likes")]')
for item in get_item_dictionary(posts):
    process_item(item, current_collection)

driver.close()
