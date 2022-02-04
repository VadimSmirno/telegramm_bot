from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,InputMediaPhoto
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import search_params,search_low_states
from request.request import hotel_search, locations_city
from data_base import peewee_bd
import logging



# @dp.message_handler(commands=['lowprice'])
async def low_price_0(message: types.Message):

    """" После команды lowprice спрашиваем у пользователя 
     в каком городе ищем отель, запоминаем что он ввел
     через машино состояние"""""

    await message.reply('В каком городе ищем?')
    await search_low_states.city.set()  # переход в машино-состояние город


# @dp.message_handler(state=search_low_states.city)
async def low_price_1(message: types.Message, state: FSMContext):

    """" делаем request запрос и вытаскиваем чарез API название 
     локации и id локации в виде словаря
     {локация : id локации  и создаем inlane клавиатуру }"""""

    try:
        town = message.text  # город
        search_params['town'] = town
        locations_city_dct = locations_city(town=town)

        keyboard = InlineKeyboardMarkup(row_width=1)
        button_list = [InlineKeyboardButton(text=key, callback_data=f'id{values}')
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
    destinationId = coll['data'][2:]
    search_params['destinationId'] = destinationId
    await coll.message.answer('Сколько отелей нужно вывести? от 1 до 5')
    await search_low_states.number_city.set() # машино-состояние количество городов


# @dp.message_handler(state=search_low_states.number_city)
async def low_price_2(message: types.Message, state: FSMContext):

    """ из машино-состояния забираем количество отелей
     делаем request запрос и отправляем в чат нужную информацию
     создаем инлайн кнопки (Да,Нет) запрашиваем нужны ли фото"""""

    count = message.text
    try:
        search_params['count'] = int(count)
        if  int(search_params['count']) > 5 or int(search_params['count'])<0:
            raise Exception
        keyboard = InlineKeyboardMarkup(row_width=2)
        button_list = [InlineKeyboardButton(text=number, callback_data=f'да{number}') for number in
                       ['Да', 'Нет']]
        keyboard.add(*button_list)
        await message.answer('Хотите посмотреть фото отелей?', reply_markup=keyboard)
        await state.reset_state()  # сброс состояний

    except Exception:
        logging.error('Пользователь неправильно ввел данные')
        await message.answer('Некорректный ввод.')
        await message.answer('Введите число не более 5')

# @dp.register_callback_query_handler(Text(startswith='да'))
async def photo(massege: types.CallbackQuery):
    await massege.answer('Подтверждено')


    if massege['data'][2:]== 'Да':
        sort_by = 'PRICE'
        await massege.message.answer('Уже ищу!')
        hotel_search(search_params['destinationId'], sort_by, str(search_params['count']))
        with peewee_bd.db:
            msg = peewee_bd.HotelInfo.select().\
                order_by(peewee_bd.HotelInfo.id.desc()).\
                limit(int(search_params['count'])) #  сортируем таблицу бд в обратном порядке и забираем первые данные

        for info_on_hotels in msg:
            res_msg =f'Название: {info_on_hotels.name}\n' \
                     f'Рейтинг: {info_on_hotels.rate}\n' \
                     f'Адрес:{info_on_hotels.addrres}\n' \
                     f'Цена:{info_on_hotels.price}\n'
            url_hotels = InlineKeyboardMarkup(row_width=1)
            url_botton = InlineKeyboardButton(text='Ссылка на отель', url=f'https://ru.hotels.com/ho{info_on_hotels.id_hotels}')
            url_hotels.add(url_botton)
            await massege.message.answer(res_msg,reply_markup=url_hotels)
            medias = types.MediaGroup()
            [medias.attach_photo(j) for j in[ info_on_hotels.photo_url1,info_on_hotels.photo_url2]]
            await massege.message.answer_media_group(media=medias)


    else:

        sort_by = 'PRICE'
        await massege.message.answer('Уже ищу!')
        hotel_search(search_params['destinationId'], sort_by, str(search_params['count']))
        msg = peewee_bd.HotelInfo.select().\
            order_by(peewee_bd.HotelInfo.id.desc()).\
            limit(int(search_params['count']))
        for info_on_hotils in msg:
            res_msg = f'Название: {info_on_hotils.name}\n' \
                      f'Рейтинг: {info_on_hotils.rate}\n' \
                      f'Адрес:{info_on_hotils.addrres}\n' \
                      f'Цена:{info_on_hotils.price}\n'
            url_hotels = InlineKeyboardMarkup(row_width=1)
            url_botton = InlineKeyboardButton(text='Ссылка на отель',
                                              url=f'https://ru.hotels.com/ho{info_on_hotils.id_hotels}')
            url_hotels.add(url_botton)
            await massege.message.answer(res_msg,reply_markup=url_hotels)




def register_handlers_lowprice(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['lowprice'])
    dp.register_message_handler(low_price_1,state=search_low_states.city)
    dp.register_message_handler(low_price_2,state=search_low_states.number_city)

def register_handlers_examination(dp:Dispatcher):
    dp.register_callback_query_handler(location_confirmation,Text(startswith='id'))
    dp.register_callback_query_handler(photo,Text(startswith='да'))



