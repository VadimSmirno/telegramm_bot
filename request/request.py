import requests,re,logging
from requests.exceptions import Timeout
from create_bot import RapidAPI
from bs4 import BeautifulSoup
from data_base import peewee_bd
import datetime
import time



def hotel_search(destinationId, sort_by, count):

    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": destinationId, "pageNumber": "1", "pageSize": count, "checkIn": "2020-01-08",
                    "checkOut": "2020-01-15", "adults1": "1", "sortOrder": sort_by, "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-key': RapidAPI,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }



    try:
        response = requests.request("GET", url, headers=headers, params=querystring,timeout=10)
        logging.info(response.status_code)
        if response.status_code == 200:
            resp = response.json()
            res = resp['data']['body']['searchResults']['results']
        else:
            return  'Сервер не доступен'

        lst_db_data=[]

        for r in res:
            id_hotels = r['id']
            time.sleep(1)
            url_photo = photo_hotels(id_hotels)
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

            lst_db_data.append([name,id_hotels,rate,adr,price,datetime.datetime.now(),url_photo[0],url_photo[1],0.0])
        with peewee_bd.db:
            peewee_bd.HotelInfo.insert_many(lst_db_data).execute()
    except (ConnectionError,TimeoutError):
        return 'Ошибка!'


def locations_city(town) -> dict:
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": town, "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RapidAPI
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
        logging.info(response.status_code)
        if response.status_code == 200:
            resp1 = response.json()
            entities = resp1['suggestions'][0]['entities']
            dct = dict()
            for i in entities:
                dct.update({BeautifulSoup(i['caption'], features='html.parser').get_text(): i['destinationId']})
            return dct
        else:
            logging.error('Сервер не доступен!')
    except (TimeoutError,AttributeError,KeyError) as e:
        logging.error(e)
        logging.error('Ошибка запроса')

def bestdeal(destinationId,priceMin,priceMax,distensMin, distensMax,count):
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": destinationId, "pageNumber": "1", "pageSize": "10", "checkIn": "2020-01-08",
                   "checkOut": "2020-01-15", "adults1": "1","priceMin":priceMin,"priceMax":priceMax, "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RapidAPI
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            resp = response.json()
            res = resp['data']['body']['searchResults']['results']
            lst_bestdeal = []

            for i in res:
                id_hotels = i['id']
                time.sleep(1)
                url_photo = photo_hotels(int(id_hotels))
                name = i['name']
                rate = i['starRating']
                try:
                    address = i['address']['streetAddress']
                except KeyError:
                    logging.error('Нет ключа адрес')
                    address = 'Неизвестно'
                try:
                    distance = i['landmarks'][0]['distance']
                    distance = distance.replace(',','.')
                    distance = float(re.sub('[А-яA-z ]','',distance))
                except KeyError:
                    logging.error('Нет ключа дистанция')
                    distance = 0.0
                try:
                    price = i['ratePlan']['price']['current']
                except KeyError:
                    price = 'Неизвестно'
                result_str = name , address, price,id_hotels,url_photo,rate
                if int(distensMin)<distance<int(distensMax):
                    lst_bestdeal.append([result_str,distance])


            lst_bestdeal = sorted(lst_bestdeal,key=lambda x:x[1])
            result = lst_bestdeal[:-(len(lst_bestdeal)-int(count))]
            if len(result)==0:
                return 'По Вашим запросам ничего не найдено'

            try:
                lst_data_base =[]
                for info_on_hotels in result:
                    name_hostel = info_on_hotels[0][0]
                    address_hostel = info_on_hotels[0][1]
                    distance_cintr = info_on_hotels[1]
                    price_hotels = info_on_hotels[0][2]
                    id_hotels = info_on_hotels[0][3]
                    url_photo = info_on_hotels[0][4]
                    rate = info_on_hotels[0][5]

                    lst_data_base.append(
                        [name_hostel, id_hotels, rate, address_hostel, price_hotels, datetime.datetime.now(),
                         url_photo[0], url_photo[1], distance_cintr])

                with peewee_bd.db:
                    peewee_bd.HotelInfo.insert_many(lst_data_base).execute()
            except Exception:
                return 'По Вашим запросам ничего не найдено'
    except (TimeoutError,AttributeError,KeyError) as err:
        logging.error(err)
        return 'Ошибка запроса'

def photo_hotels(id_hotels):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": id_hotels}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RapidAPI
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring,timeout=5)
        if response.status_code == 200:
            url=response.json()
            url_photo1 = url['hotelImages'][0]['baseUrl']
            url_photo2 = url['hotelImages'][1]['baseUrl']
            url_photo1 = str(url_photo1).replace('{size}','z')
            url_photo2 = str(url_photo2).replace('{size}', 'z')
            return [url_photo1,url_photo2]
        else:
            logging.error('сервер недоступен ошибка в photo_hotels')
    except Timeout  as err:
        logging.error(err)
        return ['https://nastolkiperm.ru/image/cache/data/Games/A-A-A/Bezymyannnnnnyy-500x500.png',
                'https://nastolkiperm.ru/image/cache/data/Games/A-A-A/Bezymyannnnnnyy-500x500.png']


