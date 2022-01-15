import requests
from create_bot import RapidAPI
from bs4 import BeautifulSoup


def hotel_search(destinationId, count, sort_by):
    # url = "https://hotels4.p.rapidapi.com/locations/search"
    #
    # querystring = {"query": town, "locale": "ru_RU","currency":"RUB"}
    #
    # headers = {
    #     'x-rapidapi-key': RapidAPI,
    #     'x-rapidapi-host': "hotels4.p.rapidapi.com"
    # }
    #
    # response = requests.request("GET", url, headers=headers, params=querystring,timeout=10)
    # if response.status_code == 200:
    #     resp1 = response.json()
    #     town_id = resp1['suggestions'][0]['entities'][0]['destinationId']
    #
    # else:
    #     return 'Сервер не доступен'

    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": destinationId, "pageNumber": "1", "pageSize": count, "checkIn": "2020-01-08",
                    "checkOut": "2020-01-15", "adults1": "1", "sortOrder": sort_by, "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-key': RapidAPI,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring,timeout=10)
    if response.status_code == 200:
        resp = response.json()
        res = resp['data']['body']['searchResults']['results']
    else:
        return  'Сервер не доступен'

    res_msg = ''
    for r in res:
        name = r['name']
        rate = r['starRating']
        try:
            adr = r['address']['streetAddress']
        except KeyError:
            adr = r['address']['locality']
        try:
            price = r['ratePlan']['price']['current']
        except KeyError: # некорректный индекс или ключ,несуществующий ключ IndexError, KeyError
            price = 'Неизвестно'
        res_msg += f'''Название: {name},
			Рейтинг: {rate},
			Адрес:{adr},
			Цена:{price}

			'''
    return res_msg


def locations_city(town):
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": town, "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-key': RapidAPI,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    if response.status_code == 200:
        resp1 = response.json()
        entities = resp1['suggestions'][0]['entities']
        dct = dict()
        for i in entities:
            dct.update({BeautifulSoup(i['caption'], features='html.parser').get_text(): i['destinationId']})
        print(dct)
        return dct
    else:
        return 'Сервер не доступен'
