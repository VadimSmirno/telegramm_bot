from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from create_bot import search_params
from request.request import hotel_search, locations_city
from create_bot import search_high_states
from data_base import peewee_bd
import logging




async def high_price_0(message: types.Message):

    """" После команды highprice спрашиваем у пользователя 
         в каком городе ищем отель, запоминаем что он ввел
         через машино состояние"""""

    await message.reply('В каком городе ищем?')
    await search_high_states.city.set() # переход в машиносостояние город


# @dp.message_handler(state=search_high_states.city)
async def high_price_1(message: types.Message, state: FSMContext):

    """" делаем request запрос и вытаскиваем чарез API название 
         локации и id локации в виде словаря
         {локация : id локации  и создаем inlane клавиатуру }"""""

    town = message.text
    search_params['town'] = town
    try:
        locations_city_dct = locations_city(town=town)

        keyboard = InlineKeyboardMarkup(row_width=1)
        button_list = [InlineKeyboardButton(text=key, callback_data=f'values{values}')
                       for key, values in locations_city_dct.items()]
        keyboard.add(*button_list)
        await message.answer('Подтвердите', reply_markup=keyboard)
        await state.reset_state()
    except AttributeError:
        logging.error('Ошибка в функции locations_city')

# @dp.callback_query_handler(Text(startswith='num'))
async def location_confirmation(coll : types.CallbackQuery):

    """"" отлавливаем нажатие inlane кнопки """""""""

    await coll.answer('Подтверждено')
    destinationId = coll['data'][6:]
    search_params['destinationId'] = destinationId
    await coll.message.answer('Сколько отелей нужно вывести? от 1 до 5')
    await search_high_states.number_city.set() # машино-состояние количество городов


# @dp.message_handler(state=search_high_states.number_city)
async def high_price_2(message: types.Message, state: FSMContext):

    """Отлавливаем сколько нужно вывести отелей, если данные некоррекиные - 
    переспрашиваем 
    Сождаем кнопки (Да, Нет) спрашиваем нужны ли фото"""""

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

    """ Вызываем функцию hotel_search() и отправляем сообщение пользователю
     из базы данных с нужной информацией
     Если пользователь в функции high_price_2 нажал Да, то 
      отправляем фотографии"""""

    await massege.answer('Подтверждено')
    if massege['data'][2:]=='Да':
        sort_by = 'PRICE_HIGHEST_FIRST'
        await massege.message.answer('Уже ищу!')
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
            url_hotels = InlineKeyboardMarkup(row_width=1)
            url_botton = InlineKeyboardButton(text='Ссылка на отель',
                                              url=f'https://ru.hotels.com/ho{info_on_hotels.id_hotels}')
            url_hotels.add(url_botton)
            await massege.message.answer(res_msg,reply_markup=url_hotels)

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
        for info_on_hotels in msg:
            res_msg = f'Название: {info_on_hotels.name}\n' \
                      f'Рейтинг: {info_on_hotels.rate}\n' \
                      f'Адрес:{info_on_hotels.addrres}\n' \
                      f'Цена:{info_on_hotels.price}\n'
            url_hotels = InlineKeyboardMarkup(row_width=1)
            url_botton = InlineKeyboardButton(text='Ссылка на отель',
                                              url=f'https://ru.hotels.com/ho{info_on_hotels.id_hotels}')
            url_hotels.add(url_botton)
            await massege.message.answer(res_msg,reply_markup=url_hotels)

def register_handlers_highprice(dp : Dispatcher):

    """ Регистрируем message_handler """""

    dp.register_message_handler(high_price_0,commands=['highprice'])
    dp.register_message_handler(high_price_1,state=search_high_states.city)
    dp.register_message_handler(high_price_2,state=search_high_states.number_city)

def register_handlers_callback_query_handler(dp : Dispatcher):

    """ Регистрируем callback_query_handler"""""

    dp.register_callback_query_handler(location_confirmation, Text(startswith='values'))
    dp.register_callback_query_handler(photo_high, Text(startswith='qw'))