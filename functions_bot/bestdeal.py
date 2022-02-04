from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import search_best_states,search_params
from request.request import locations_city
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from request.request import bestdeal
import logging
from data_base import peewee_bd





async def bestdeal_city(message: types.Message):

    """"Запрашиваем город и переходим в машино-состояние city"""""

    await message.reply('В каком городе ищем?')
    await search_best_states.city.set()



async def bestdeal_locations_city(message: types.Message, state: FSMContext):

    """"Вункция locations_city() возвращает словарь
    в котором название города-локации это ключ, а id города это значение
    Передаем словарь в инлайн кнопки"""""

    try:
        town = message.text
        search_params['town'] = town
        locations_city_dct = locations_city(town=town)
        keyboard = InlineKeyboardMarkup(row_width=1)
        button_list = [InlineKeyboardButton(text=key, callback_data=f'num{values}')
                       for key, values in locations_city_dct.items()]
        keyboard.add(*button_list)
        await message.answer('Подтвердите', reply_markup=keyboard)
        await state.reset_state()
    except AttributeError:
        logging.error('Ошибка в функции locations_city')



async def location_confirmation(coll: types.CallbackQuery):

    """"отлавливаем нажатие инлайн кнопки - выбираем город и его id"
    И сознаем новые инлайн кнопки (сколько вывести отелей)"""""

    await coll.answer('Подтверждено')
    destinationId = coll['data'][3:]
    search_params['destinationId'] = destinationId
    keyboard = InlineKeyboardMarkup(row_width=5)
    button_list = [InlineKeyboardButton(text= number,callback_data=f'_{number}') for number in ['1','2','3','4','5']]
    keyboard.add(*button_list)
    await coll.message.answer('Сколько отелей нужно вывести?',reply_markup=keyboard)





async def ansve_count_hotel(massege: types.CallbackQuery):

    """"Отлавливаем нажатие кнопки и переходим в машино-состояние price"""""

    count = massege['data'][-1]
    search_params['count'] = count
    await massege.message.answer('Введите диапазон цен через "-", например 1000-5000')
    await massege.answer()
    await search_best_states.price.set()

# @dp.message_handler(state=search_best_states.price)
async def message_check(massege: types.Message):

    """ обрабатываем введеные данные(цена), если данные некорректные переспрашиваем 
    и снова переходим в машино состояние price, если все верно переходим в машино-
    состояние distens"""""

    price = massege.text.split('-')
    try:
        if int(price[0])<int(price[1]):
            search_params['price'] = price
            await massege.answer('На каком расстоянии в км от центра посмотреть отели? '
                                 'введите через "-" Например: 0-10')
            await search_best_states.distens.set()
        else:
            await massege.answer('Некорректные данные')
            await massege.answer('Введите диапазон цен через "-", Например: 1000-5000')
            await search_best_states.price.set()
    except (ValueError, TypeError):
        logging.error('Пользователь ввел некорректные данные')
        await massege.answer('Некорректные данные')
        await massege.answer('Введите диапазон цен через "-", например 1000-5000')
        await search_best_states.price.set()


# @dp.message_handler(state=search_best_states.distens)
async def bestdeal_distens(message: types.Message, state: FSMContext):

    """ обрабатываем данные (дистанция), если некорректные, переспрашиваем и переходим 
    в машино-состояние distens,
    если все верно, созаем инлайн кнопки и предлагаем посмотреть фото (Да, Нет)"""""

    try:
        distens = message.text.split('-')
        if int(distens[0]) < int(distens[1]):
            search_params['distens'] = distens

            keyboard = InlineKeyboardMarkup(row_width=2)
            button_list = [InlineKeyboardButton(text=number, callback_data=f'wq{number}') for number in
                           ['Да', 'Нет']]
            keyboard.add(*button_list)
            await message.answer('Хотите посмотреть фото отелей?', reply_markup=keyboard)
            await state.reset_state()  # сброс состояний
        else:
            logging.error('Пользователь ввел некорректные данные')
            raise ValueError

    except (ValueError,TypeError):
        logging.error('Пользователь ввел некорректные данные')
        await message.answer('Некорректные данные')
        await message.answer('Введите диапазон расстояний через "-", например 1-5')
        await search_best_states.distens.set()

# @dp.callback_query_handler(Text(startswith='wq'))
async def photo_bestdeal(massege: types.CallbackQuery):

    """От лавливаем нажатие кнопки (Да, Нет) 
    Если Да, то вызываем функцию bestdeal, 
    достаем результаты из базы данных отправляем пользователю и
    отпраляем группой фотографии,
    если Нет, от информация и базы данных отправляется без фотографий"""""

    await massege.answer('Подтверждено')
    distens = search_params['distens']
    priceMin = search_params['price'][0]
    priceMax = search_params['price'][1]
    distensMin = float(distens[0])
    distensMax = float(distens[1])
    if massege['data'][2:] == 'Да':
        await massege.message.answer('Уже ищу!')
        try:
            res = bestdeal(search_params['destinationId'], priceMin, priceMax, distensMin, distensMax, search_params['count'])
            if res == 'По Вашим запросам ничего не найдено':
                await massege.message.answer('По Вашим запросам ничего не найдено')
            else:
                with peewee_bd.db:
                    msg = peewee_bd.HotelInfo.select().\
                        order_by(peewee_bd.HotelInfo.id.desc()).\
                        limit(int(search_params['count']))
                    for info_on_hotels in msg:
                        res_msg = f'Название: {info_on_hotels.name}\n' \
                                  f'Рейтинг: {info_on_hotels.rate}\n' \
                                  f'Адрес:{info_on_hotels.addrres}\n' \
                                  f'Цена:{info_on_hotels.price}\n' \
                                  f'Расстояние до центра: {info_on_hotels.distens} км'
                        url_hotels = InlineKeyboardMarkup(row_width=1)
                        url_botton = InlineKeyboardButton(text='Ссылка на отель',
                                                          url=f'https://ru.hotels.com/ho{info_on_hotels.id_hotels}')
                        url_hotels.add(url_botton)
                        await massege.message.answer(res_msg,reply_markup=url_hotels)
                        medias = types.MediaGroup()
                        [medias.attach_photo(url) for url in [info_on_hotels.photo_url1, info_on_hotels.photo_url2]]
                        await massege.message.answer_media_group(media=medias)
        except (TypeError,AttributeError):
            logging.error('Ошибка в функции bestdeal')
            await massege.message.answer('По Вашим запросам ничего не найдено')

    else:
        await massege.message.answer('Уже ищу!')
        try:
            bestdeal(search_params['destinationId'], priceMin, priceMax, distensMin, distensMax,search_params['count'])
            with peewee_bd.db:
                msg = peewee_bd.HotelInfo.select(). \
                    order_by(peewee_bd.HotelInfo.id.desc()). \
                    limit(int(search_params['count']))
                for info_on_hotels in msg:
                    res_msg = f'Название: {info_on_hotels.name}\n' \
                              f'Рейтинг: {info_on_hotels.rate}\n' \
                              f'Адрес:{info_on_hotels.addrres}\n' \
                              f'Цена:{info_on_hotels.price}\n' \
                              f'Расстояние до центра: {info_on_hotels.distens} км'
                    url_hotels = InlineKeyboardMarkup(row_width=1)
                    url_botton = InlineKeyboardButton(text='Ссылка на отель',
                                                      url=f'https://ru.hotels.com/ho{info_on_hotels.id_hotels}')
                    url_hotels.add(url_botton)
                    await massege.message.answer(res_msg,reply_markup=url_hotels)

        except TypeError:
            logging.error('Ошибка в функции')
            await massege.message.answer('По Вашим запросам ничего не найдено')


def register_handlers_bestdeal(dp : Dispatcher):

    """ регистрируем message_handler"""""

    dp.register_message_handler(bestdeal_city,commands=['bestdeal'])
    dp.register_message_handler(bestdeal_locations_city,state=search_best_states.city)
    dp.register_message_handler(bestdeal_distens,state=search_best_states.distens)
    dp.register_message_handler(message_check,state=search_best_states.price)


def register_callback_query_handler(dp: Dispatcher):

    """ регистрируем callback_query_handler"""""

    dp.register_callback_query_handler(location_confirmation,Text(startswith='num'))
    dp.register_callback_query_handler(ansve_count_hotel,Text(startswith='_'))
    dp.register_callback_query_handler(photo_bestdeal,Text(startswith='wq'))
