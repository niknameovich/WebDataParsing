import requests
import json

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

username = input('put your git login here: ')
git_response = requests.get(f'https://api.github.com/users/{username}/repos',headers=headers)
if git_response.ok:
    with open('yourgitrepos.json','w') as respf:
        json.dump(git_response.json(),respf, indent=2)
else:
    print(f'OOPS! you have got an error {git_response.status_code}')