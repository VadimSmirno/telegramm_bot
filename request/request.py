import requests
from create_bot import RapidAPI
from bs4 import BeautifulSoup
import re
import logging


def hotel_search(destinationId, sort_by, count='5' ):
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
        return dct
    else:
        return 'Сервер не доступен'

def bestdeal(destinationId,priceMin,priceMax,distensMin, distensMax,count):
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": destinationId, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                   "checkOut": "2020-01-15", "adults1": "1","priceMin":priceMin,"priceMax":priceMax, "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "1c53557662msh988d1a96d4da0d7p152179jsnce4697853b15"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        resp = response.json()
        res = resp['data']['body']['searchResults']['results']
        lst_bestdeal = []
        res_masg=''
        for i in res:
            name = i['name']
            address = i['address']['streetAddress']
            distance = i['landmarks'][0]['distance']
            distance = distance.replace(',','.')
            distance = float(re.sub('[А-яA-z ]','',distance))
            try:
                price = i['ratePlan']['price']['current']
            except:
                price = 'Неизвестно'
            result_str = name , address, price
            if distensMin<distance<distensMax:
                lst_bestdeal.append([result_str,distance])
        lst_bestdeal = sorted(lst_bestdeal,key=lambda x:x[1])

        result = lst_bestdeal[:-(len(lst_bestdeal)-count)]
        try:
            for i in result:
                name_hostel = i[0][0]
                address_hostel = i[0][1]
                distance_cintr = i[1]
                price_hotels = i[0][2]
                res_masg += f'''
                Название: {name_hostel},
                Адрес: {address_hostel},
                Расстояние до центра: {distance_cintr}
                Цена: {price_hotels}
    
                '''
        except:
            return 'По Вашим запросам ничего не найдено'
        return res_masg

