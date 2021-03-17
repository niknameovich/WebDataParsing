from bs4 import BeautifulSoup as bs
import requests
from fake_useragent import UserAgent
import pandas
from pymongo import MongoClient
from urllib.parse import urlparse
import re


class VacanciesParser:
    rand_agent = {'User-Agent': UserAgent().random}
    headers = {'vacancy': ['site', 'name', 'href'], 'salary': ['min_salary', 'max_salary', 'currency']}

    def __init__(self, vacancy_text):
        self.vacancy = vacancy_text
        self.mclient = MongoClient('localhost', 27017)
        self.testdb = self.mclient['test_db']
        self.collection = self.testdb.doc_collection
        self.total_vacancies = []

    # функция для определения предлагаемой ЗП с сайта HH
    def calc_comp(self, compensation, result_v, list_headers=headers['salary']):
        salary_regex = re.compile(r'(\D*)(\d+)(\s?)(\d+)(-?)(\d*)(\s?)(\d*)(\s*)(\S+)')
        if compensation is not None:
            salary_data = salary_regex.findall(compensation.text)
            if len(salary_data) > 0:
                if 'от' in salary_data[0][0]:
                    result_v[list_headers[0]] = int(salary_data[0][1] + salary_data[0][3])
                    result_v[list_headers[2]] = salary_data[0][-1]
                elif 'до' in salary_data[0][0]:
                    result_v[list_headers[1]] = int(salary_data[0][1] + salary_data[0][3])
                    result_v[list_headers[2]] = salary_data[0][-1]
                elif 'ПО' in salary_data[0][0].upper():
                    pass
                else:
                    if len(salary_data) > 1:
                        result_v[list_headers[0]] = int(salary_data[0][1] + salary_data[0][3])
                        result_v[list_headers[1]] = int(salary_data[-1][1] + salary_data[-1][3])
                        result_v[list_headers[2]] = salary_data[-1][-1]
                    else:
                        result_v[list_headers[0]] = int(salary_data[0][1] + salary_data[0][3])
                        result_v[list_headers[1]] = int(salary_data[0][5] + salary_data[0][7])
                        result_v[list_headers[2]] = salary_data[0][-1]
        return result_v

    # задание 3. Определение ID для найденных ваканский
    # mode задается в словаре исходных данных для каждого сайта
    # функция получения ID найденной вакансии
    def getId(self, tag, mode):
        if mode == 0:
            return urlparse(tag['href']).path.split('/')[-1]
        elif mode == 1:
            return tag['href'].split('-')[-1].split('.')[0]

    # функция для поэлементной работы с каждым из действительных результатов поиска вакансий
    def job_parsing(self, elements, parsing_dict, base_url, mode, list_headers=headers['vacancy']):
        for vacancy in elements:
            result_v = {}
            title = vacancy.find(parsing_dict['title'][0], attrs=parsing_dict['title'][-1])
            if title is None:
                continue
            result_v[list_headers[0]] = base_url
            result_v[list_headers[1]] = title.text
            result_v[list_headers[2]] = title['href']
            result_v['_id'] = self.getId(title, mode)
            compensation = vacancy.find(parsing_dict['salary'][0], attrs=parsing_dict['salary'][-1])
            # вызов функции обработчика определения предлагаемой ЗП из словаря исходных данных
            self.calc_comp(compensation, result_v, VacanciesParser.headers['salary'])
            self.write_result_to(result_v, self.collection)

    def check_continuation_criteria(self, url_list):
        result = True
        for url_dict in url_list:
            result = url_dict['breakflag'] & result
        return result

    def parse_data(self, url, mode):
        if not url['breakflag']:
            response = requests.get(url['baseurl'], headers=VacanciesParser.rand_agent, params=url['params'])
            # условие корректности ответа для HH
            if response.status_code < 400:
                soup = bs(response.text, 'lxml')
                vacancies = soup.find_all(name='div', attrs=url['div'])
                # условие корректности ответа для SUPERJOB
                if len(vacancies) == 0:
                    url['breakflag'] = True
                else:
                    self.job_parsing(vacancies, url['parsing'], url['baseurl'], mode,
                                     VacanciesParser.headers['vacancy'])
                    # изменения параметров исходного GET запроса
                    url['params']['page'] = str(int(url['params']['page']) + 1)
            else:
                url['breakflag'] = True

    # Задание 1. Запись результатов парсинга в коллекцию mongoDB
    # Задание 2. Вывод в csv результатов поиска в MongoDB по критерию
    def write_result_to(self, tag, collection):
        if type(tag) is list:
            # вывод списка словарей в табличную структуру
            totalvacDF = pandas.DataFrame.from_records(tag)
            totalvacDF.to_csv(f'totalvacancies_{self.vacancy}.csv')
        elif type(tag) is dict:
            collection.update_one({'_id': tag['_id']}, {'$set': tag}, upsert=True)
        else:
            pass

    # Задание 2. Поиск в MongoDB по критерию
    def find_parsed_data(self, parameter, criteria, value):
        if value is None:
            current_query = self.collection.find({'currency': value})
        else:
            to_translate = ['>', '<', '>=', '<=', '=']
            translated = ['$gt', '$lt', '$gte', '$lte', '$eq']
            current_query = self.collection.find({parameter: {translated[to_translate.index(criteria)]: value}})
        self.write_result_to(list(current_query), self.collection)


# исходные данные
my_best_parser = VacanciesParser(input('Put your desire vacancy name: '))
url_list = [{'baseurl': 'https://www.hh.ru/search/vacancy',
             # переменная для выхода из цикла постраничного поиска
             'breakflag': False,
             'params': {},
             'mode': 0,
             # элемент для поиска всех Tag  содержащих вакансии
             'div': {'class': 'vacancy-serp-item'},
             # элементы поиска в ответе
             'parsing': {
                 'title': ('a', {'data-qa': 'vacancy-serp__vacancy-title'}),
                 'salary': ('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
             }
             },
            {'baseurl': 'https://www.superjob.ru/vacancy/search/',
             'breakflag': False,
             'params': {},
             'mode': 1,
             'div': {'class': 'f-test-search-result-item'},
             'parsing': {
                 'title': ('a', {'class': 'icMQ_'}),
                 'salary': ('span', {'class': 'f-test-text-company-item-salary'})
             }
             }]

# параметры УРЛ запроса для каждого сайта
url_list[0]['params'] = {'st': 'searchVacancy', 'text': my_best_parser.vacancy,
                         'area': '113', 'items_on_page': '100', 'page': '0'}
url_list[1]['params'] = {'keywords': my_best_parser.vacancy, 'page': '1', 'noGeo': '1'}


# общий цикл запросов к сайтам
# выход в том случаи, если ответы с обоих сайтов не прошли проверку наличия данных
while not my_best_parser.check_continuation_criteria(url_list):
    for url in url_list:
        my_best_parser.parse_data(url, url['mode'])

# примеры поиска по различным критериям
my_best_parser.find_parsed_data('min_salary', '<=', 50000)
my_best_parser.find_parsed_data('max_salary', '=', 300000)
my_best_parser.find_parsed_data('', '', None)
