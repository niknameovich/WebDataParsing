import scrapy
from scrapy.http import HtmlResponse
import re
import json
# from urllib.parse import urlencode
from urllib.parse import quote
from copy import deepcopy
from items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    username = "forexample613"
    enc_password = "#PWD_INSTAGRAM_BROWSER:9:1617462283:AVdQAFZ/MmfIEgl0nhZtvrj7WU5TAx71Z+8UqwF0szpoWGlLRkYFFBInSg7r" \
                   "/RTRuJPZcFD28KWqtqXHM9ZXyvNai5euAc4o5NihWr1tz61cR8rfxI83Kaqgn7WoLDuSLO4RylzgoR83UybC "
    login_url = "https://www.instagram.com/accounts/login/ajax/"

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = '5aefa9893005572d237da5068082d8d5'
    followed_hash = '3dec7e2c57367ef3da3d987d89f9dbc'

    def __init__(self, logins: list):
        self.user_to_parse = logins
        super(InstagramSpider).__init__(self)

    def parse(self, response: HtmlResponse):
        yield scrapy.FormRequest(
            self.login_url,
            callback=self.user_login,
            method="POST",
            formdata={"username": self.username, "enc_password": self.enc_password},
            headers={"X-CSRFToken": self.fetch_csrf_token(response.text)}
        )

    def user_login(self, response: HtmlResponse):
        json_data = response.json()
        if json_data["user"] and json_data["authenticated"]:
            # self.user_id = json_data["userId"]
            for login in self.user_to_parse:
                yield response.follow(
                    f'/{login}',
                    callback=self.user_data_parse,
                    cb_kwargs={"username": login}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {"id": user_id, 'include_reel': True, 'fetch_mutual': False, "first": 24}
        # сравните с оригинальной строкой из запроса от сайта
        str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
        # вручную упаковываем variables в нужный формат строки
        # str_variables = self.make_variables_string(variables)
        url = self.graphql_url + f"query_hash={self.followers_hash}&variables={str_variables}"
        yield response.follow(
            url,
            callback=self.parse_posts,
            cb_kwargs={
                "username": username,
                "user_id": user_id,
                "variables": deepcopy(variables)
            },
        )

    def make_variables_string(self, variables):
        # хардкод для кодирования словаря как в запросе Instagram
        # %7B"id"%3A"7709057810"%2C"first"%3A12%2C"after"%3A"QVFCblJDbklkd1F3bm1hWExXRVR2RVRDYWRXek5ORWUxOWtjY01mLWtGYS05Y25ZTkJ2c20zNzRGdjEwNGZmNnhQY1F2eGZZMXgzQUd1X3d5eWVMejczRw%3D%3D"%7D
        open_parenthesis = "%7B"  # {
        close_parenthesis = "%7D"  # }
        space = "%3A"
        comma = "%2C"  # ,
        s = []
        for i, (k, v) in enumerate(variables.items()):
            s.append('"' + k + '"')
            s.append(space)
            if isinstance(v, str):
                s.append('"' + v + '"')
            else:
                s.append(str(v))

            if i != len(variables) - 1:
                s.append(comma)
        s = [open_parenthesis] + s + [close_parenthesis]
        return "".join(s)

    def parse_followers(self, response: HtmlResponse, username, user_id, variables):
        data = response.json()
        data = data["data"]["user"]["edge_owner_to_timeline_media"]
        page_info = data.get("page_info", None)
        if page_info["has_next_page"]:
            variables["after"] = page_info["end_cursor"]

            # сравните с оригинальной строкой из запроса от сайта
            str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
            # вручную упаковываем variables в нужный формат строки
            # str_variables = self.make_variables_string(variables)
            url = self.graphql_url + f"query_hash={self.followers_hash}&variables={str_variables}"
            yield response.follow(
                url,
                callback=self.parse_followers,
                cb_kwargs={
                    "username": username,
                    "user_id": user_id,
                    "variables": deepcopy(variables)
                }
            )

        posts = data["edges"]
        for post in posts:
            tmp = post["node"]
            item = InstaparserItem(
                user_id=user_id,
                photo=tmp["display_url"],
                likes=tmp["edge_media_preview_like"]["count"],
                post_data=tmp
            )
            yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
