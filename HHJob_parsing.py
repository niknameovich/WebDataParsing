from bs4 import BeautifulSoup as bs
import requests
from fake_useragent import UserAgent
import pandas


# функция для определения предлагаемой ЗП с сайта HH
def calc_comp_hh(compensation, result_v):
    if compensation is not None:
        if compensation.text.startswith('от '):
            result_v['start_comp'] = compensation.text[3:-1]
            result_v['max_comp'] = 'not set'
        elif compensation.text.startswith('до '):
            result_v['start_comp'] = 'not set'
            result_v['max_comp'] = compensation.text[3:-1]
        else:
            comp = compensation.text.split('-')
            result_v['start_comp'] = comp[0]
            result_v['max_comp'] = comp[-1]


# функция для определения предлагаемой ЗП с сайта SuperJob
def calc_comp_sj(compensation, result_v):
    if compensation is not None:
        if compensation.text.__contains__('от'):
            result_v['start_comp'] = compensation.text[3:-1]
            result_v['max_comp'] = 'not set'
        elif compensation.text.__contains__('до'):
            result_v['start_comp'] = 'not set'
            result_v['max_comp'] = compensation.text[3:-1]
        elif compensation.text.startswith('По '):
            result_v['start_comp'] = 'not set'
            result_v['max_comp'] = 'not set'
        else:
            comp = compensation.text.split('-')
            result_v['start_comp'] = comp[0]
            result_v['max_comp'] = comp[-1]


# функция для поэлементной работы с каждым из действительных результатов поиска вакансий
def jobsparsing(elements, listvalue, result):
    for vacancy in elements:
        result_v = {}
        title = vacancy.find(listvalue[0][0], attrs=listvalue[0][1])
        if title is None:
            continue
        result_v['site'] = url['baseurl']
        result_v['name'] = title.text
        result_v['href'] = title['href']
        compensation = vacancy.find(listvalue[1][0], attrs=listvalue[1][1])
        # вызов функции обработчика определения предлагаемой ЗП из словаря исходных данных
        listvalue[2](compensation, result_v)
        result.append(result_v)
    return result

# исходные данные
useragent = {'User-Agent': UserAgent().random}
vacancyname = input('Put your desire vacancy name: ')

# структура для единообразного хранения html структуры запроса/ответа по каждому из сайтов поиска
urllist = [{'baseurl': 'https://www.hh.ru/search/vacancy',
            # переменная для выхода из цикла постраничного поиска
            'breakflag': False,
            'params': {},
            # элемент для поиска всех Tag  содержащих вакансии
            'div': {'class': 'vacancy-serp-item'},
            # элементы поиска в ответе
            'parsing': [
                ('a', {'data-qa': 'vacancy-serp__vacancy-title'}),
                ('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}),
                # передача ссылки на функцию обработчик предлагаемой ЗП
                calc_comp_hh
            ]},
           {'baseurl': 'https://www.superjob.ru/vacancy/search/',
            'breakflag': False,
            'params': {},
            'div': {'class': 'f-test-search-result-item'},
            'parsing': [
                ('a', {'class': 'icMQ_'}),
                ('span', {'class': 'f-test-text-company-item-salary'}),
                calc_comp_sj]
            }]

# параметры УРЛ запроса для каждого сайта
urllist[0]['params'] = {'st': 'searchVacancy', 'text': vacancyname.replace(' ', '+'),
                        'area': '113', 'items_on_page': '100', 'page': '0'}
urllist[1]['params'] = {'keywords': vacancyname.replace(' ', '-'), 'page': '1', 'noGeo': '1'}

totalvacancies = []

# общий цикл запросов к сайтам
# выход в том случаи, если ответы с обоих сайтов не прошли проверку наличия данных
while not urllist[0]['breakflag'] & urllist[1]['breakflag']:
    for url in urllist:
        if not url['breakflag']:
            response = requests.get(url['baseurl'], headers=useragent, params=url['params'])
            # условие корректности ответа для HH
            if response.ok:
                soup = bs(response.text, 'lxml')
                vacancies = soup.find_all(name='div', attrs=url['div'])
                # условие корректности ответа для SUPERJOB
                if len(vacancies) == 0:
                    url['breakflag'] = True
                    continue
                else:
                    jobsparsing(vacancies, url['parsing'], totalvacancies)
                    # изменения параметров исходного GET запроса
                    url['params']['page'] = str(int(url['params']['page']) + 1)
            else:
                url['breakflag'] = True
                continue

# вывод списка словарей в табличную структуру
totalvacDF = pandas.DataFrame.from_records(totalvacancies)
totalvacDF.to_csv(f'totalvacancies_{vacancyname}.csv')
