import requests
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
           'pagesize': '10',
           'fulltext': 'false',
           'apiKey': 'UxdTZGI1OJVMrSeDECX3N05imvLAB6FR', }
base_uri = 'https://core.ac.uk:443/api-v2/articles/search/title%3A%20'
title = input('put your desired title here:')
authresp = requests.get(f'{base_uri}{title}', headers=headers)
if authresp.status_code == 200:
    simplifydict = {}
    myresp = json.loads(authresp.text)
    # упрощенный json с небольшим количеством атрибутов
    datadict = myresp['data']
    for articledict in datadict:
        simplifydict[articledict['id']] = {key: value for key, value in articledict.items() if
                                           key in ['title', 'authors', 'description']}
    with open(f'your_{title}.json', 'w') as respf:
        json.dump(simplifydict, respf, indent=2)
else:
    print(f'OOPS! You have got an error {authresp.status_code}')
