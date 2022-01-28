from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from create_bot import search_params
from request.request import hotel_search, locations_city
from create_bot import search_high_states
from data_base import peewee_bd
import logging



# @dp.message_handler(commands=['git '])
async def low_price_0(message: types.Message):
    await message.reply('В каком городе ищем?')
    await search_high_states.city.set() # переход в машиносостояние город


# @dp.message_handler(state=search_high_states.city)
async def low_price_1(message: types.Message, state: FSMContext):
    town = message.text
    search_params['town'] = town
    locations_city_dct = locations_city(town=town)

    keyboard = InlineKeyboardMarkup(row_width=1)
    button_list = [InlineKeyboardButton(text=key, callback_data=f'values{values}')
                   for key, values in locations_city_dct.items()]
    keyboard.add(*button_list)

    await message.answer('Подтвердите', reply_markup=keyboard)
    await state.reset_state()

# @dp.callback_query_handler(Text(startswith='num'))
async def location_confirmation(coll : types.CallbackQuery):

    """"" отлавливаем нажатие inlane кнопки """""""""

    await coll.answer('Подтверждено')
    destinationId = coll['data'][6:]
    search_params['destinationId'] = destinationId
    await coll.message.answer('Сколько отелей нужно вывести? от 1 до 5')
    await search_high_states.number_city.set() # машино-состояние количество городов


# @dp.message_handler(state=search_high_states.number_city)
async def low_price_2(message: types.Message, state: FSMContext):
    count = message.text
    try:
        search_params['count'] = int(count)
        if int(search_params['count']) > 5 or int(search_params['count']) < 0:
            raise Exception
        keyboard = InlineKeyboardMarkup(row_width=2)
        button_list = [InlineKeyboardButton(text=number, callback_data=f'qw{number}') for number in
                       ['Да', 'Нет']]
        keyboard.add(*button_list)
        await message.answer('Хотите посмотреть фото отелей?', reply_markup=keyboard)
        await state.reset_state()
    except:
        logging.error('Пользователь неправильно ввел данные')
        await message.answer('Некорректный ввод.')
        await message.answer('Введите число не более 5')

# @dp.register_callback_query_handler(Text(startswith='qw'))
async def photo_high(massege:types.CallbackQuery):
    await massege.answer('Подтверждено')
    if massege['data'][2:]=='Да':
        sort_by = 'PRICE_HIGHEST_FIRST'
        await massege.message.answer('Уже ищу')
        hotel_search(search_params['destinationId'], sort_by, str(search_params['count']))
        with peewee_bd.db:
            msg = peewee_bd.HotelInfo.select(). \
                order_by(peewee_bd.HotelInfo.id.desc()). \
                limit(int(search_params['count']))  # сортируем таблицу бд в обратном порядке и забираем первые данные
        for info_on_hotels in msg:
            res_msg = f'Название: {info_on_hotels.name}\n' \
                      f'Рейтинг: {info_on_hotels.rate}\n' \
                      f'Адрес:{info_on_hotels.addrres}\n' \
                      f'Цена:{info_on_hotels.price}\n'
            await massege.message.answer(res_msg)
            medias = types.MediaGroup() # отправляем группу фотографий
            [medias.attach_photo(j) for j in [info_on_hotels.photo_url1, info_on_hotels.photo_url2]]
            await massege.message.answer_media_group(media=medias)
    else:
        sort_by = 'PRICE_HIGHEST_FIRST'
        await massege.message.answer('Уже ищу!')
        hotel_search(search_params['destinationId'], sort_by, str(search_params['count']))
        msg = peewee_bd.HotelInfo.select(). \
            order_by(peewee_bd.HotelInfo.id.desc()). \
            limit(int(search_params['count']))
        for info_on_hotils in msg:
            res_msg = f'Название: {info_on_hotils.name}\n' \
                      f'Рейтинг: {info_on_hotils.rate}\n' \
                      f'Адрес:{info_on_hotils.addrres}\n' \
                      f'Цена:{info_on_hotils.price}\n'
            await massege.message.answer(res_msg)

def register_handlers_highprice(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['highprice'])
    dp.register_message_handler(low_price_1,state=search_high_states.city)
    dp.register_message_handler(low_price_2,state=search_high_states.number_city)

def register_handlers_callback_query_handler(dp : Dispatcher):
    dp.register_callback_query_handler(location_confirmation, Text(startswith='values'))
    dp.register_callback_query_handler(photo_high, Text(startswith='qw'))