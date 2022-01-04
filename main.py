from aiogram import Bot, Dispatcher, executor, types
# import asyncio
import logging
# from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from decouple import  config
import requests



TOKEN = config('TOKEN')
RapidAPI = config('RapidAPI')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class search_low_states(StatesGroup):
    q1 = State()
    q2 = State()


class search_high_states(StatesGroup):
    q1 = State()
    q2 = State()


class search_best_states(StatesGroup):
    q1 = State()
    q2 = State()


search_params = {'town': 0,
                 'count': 0}


def hotel_search(town, count, sort_by):
    url = "https://hotels4.p.rapidapi.com/locations/search"

    querystring = {"query": town, "locale": "ru_RU","currency":"RUB"}

    headers = {
        'x-rapidapi-key': RapidAPI,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    resp1 = response.json()
    town_id = resp1['suggestions'][0]['entities'][0]['destinationId']

    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": town_id, "pageNumber": "1", "pageSize": count, "checkIn": "2020-01-08",
                   "checkOut": "2020-01-15", "adults1": "1", "sortOrder": sort_by, "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-key': RapidAPI,
        'x-rapidapi-host': "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    resp = response.json()
    res = resp['data']['body']['searchResults']['results']

    res_msg = ''
    for r in res:
        name = r['name']
        rate = r['starRating']
        adr = r['address']['streetAddress']
        try:
            price = r['ratePlan']['price']['current']
        except:
            price = 'Неизвестно'
        res_msg += f'''Название: {name},
			Рейтинг: {rate},
			Адрес:{adr},
			Цена:{price}

			'''
    return res_msg


# low_price, high_price, best_deal(дешевые и близко к центру)

start_message = 'Привет! Я помогу тебе выбрать самые классные отели по твоим запросам.\n\
						 Получить самые дешевые отели: команда /lowprice,\n\
						 Получить самые дор огие отели: команда /highprice, \n\
						 '


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(start_message)


@dp.message_handler(commands=['lowprice'])
async def low_price_0(message: types.Message):
    await message.reply('В каком городе ищем?')
    await search_low_states.q1.set()  # переход в состояние q1


@dp.message_handler(state=search_low_states.q1)
async def low_price_1(message: types.Message, state: FSMContext):
    town = message.text  # город
    search_params['town'] = town
    await message.answer('Сколько отелей нужно вывести?')
    await search_low_states.next()


@dp.message_handler(state=search_low_states.q2)
async def low_price_1(message: types.Message, state: FSMContext):
    count = message.text
    search_params['count'] = count
    sort_by = 'PRICE'
    await message.answer('Уже ищу!')
    msg = hotel_search(search_params['town'], search_params['count'], sort_by)
    await message.answer(msg)
    await state.reset_state()  # сброс состояний


@dp.message_handler(commands=['highprice'])
async def low_price_0(message: types.Message):
    await message.reply('В каком городе ищем?')
    await search_high_states.q1.set()


@dp.message_handler(state=search_high_states.q1)
async def low_price_1(message: types.Message, state: FSMContext):
    town = message.text
    search_params['town'] = town
    await message.answer('Сколько отелей нужно вывести?')
    await search_high_states.next()


@dp.message_handler(state=search_high_states.q2)
async def low_price_1(message: types.Message, state: FSMContext):
    count = message.text
    search_params['count'] = count
    sort_by = 'PRICE_HIGHEST_FIRST'
    await message.answer('Уже ищу!')
    msg = hotel_search(search_params['town'], search_params['count'], sort_by)
    await message.answer(msg)
    await state.reset_state()


@dp.message_handler(commands=['bestdeal'])
async def low_price_0(message: types.Message):
    await message.reply('В каком городе ищем?')
    await search_best_states.q1.set()


@dp.message_handler(state=search_best_states.q1)
async def low_price_1(message: types.Message, state: FSMContext):
    city = message.text
    await message.answer('Сколько отелей нужно вывести?')
    await search_best_states.next()


@dp.message_handler(state=search_best_states.q2)
async def low_price_1(message: types.Message, state: FSMContext):
    count = message.text
    # запрос api
    await state.reset_state()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)