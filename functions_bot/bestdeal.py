from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import SearchBestStates,search_params
from request.request import locations_city
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from request.request import bestdeal
from aiogram_calendar import simple_cal_callback, SimpleCalendar
import datetime
import logging
from data_base import peewee_bd





async def bestdeal_city(message: types.Message):

    """"Запрашиваем город и переходим в машино-состояние city"""""

    await message.reply('В каком городе ищем?')
    await SearchBestStates.city.set()



async def bestdeal_locations_city(message: types.Message, state: FSMContext):

    """"Вункция locations_city() возвращает словарь
    в котором название города-локации это ключ, а id города это значение
    Передаем словарь в инлайн кнопки"""""

    try:
        town = message.text
        search_params['town'] = town
        locations_city_dct = locations_city(town=town)
        if len(locations_city_dct)!=0:
            keyboard = InlineKeyboardMarkup(row_width=1)
            button_list = [InlineKeyboardButton(text=key, callback_data=f'num{values}')
                           for key, values in locations_city_dct.items()]
            keyboard.add(*button_list)
            await message.answer('Подтвердите', reply_markup=keyboard)
            await state.reset_state()
        else:
            await message.answer(f'Ничего не нашел в городе {town}')
            await message.answer('Может в другом городе посмотрим отели?')
            await SearchBestStates.city.set()
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
    await SearchBestStates.price.set()

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
            await SearchBestStates.distens.set()
        else:
            await massege.answer('Некорректные данные')
            await massege.answer('Введите диапазон цен через "-", Например: 1000-5000')
            await SearchBestStates.price.set()
    except (ValueError, TypeError):
        logging.error('Пользователь ввел некорректные данные')
        await massege.answer('Некорректные данные')
        await massege.answer('Введите диапазон цен через "-", например 1000-5000')
        await SearchBestStates.price.set()


# @dp.message_handler(state=search_best_states.distens)
async def bestdeal_distens(message: types.Message, state: FSMContext):

    """ обрабатываем данные (дистанция), если некорректные, переспрашиваем и переходим 
    в машино-состояние distens,
    если все верно, создаем календарь для выбора даты заселения"""""

    try:
        distens = message.text.split('-')
        if int(distens[0]) < int(distens[1]):
            search_params['distens'] = distens
            await state.reset_state()  # сброс состояний
            await message.answer("Пожалуйста выберите дату заселения: ",
                                 reply_markup=await SimpleCalendar().start_calendar())
            await SearchBestStates.date_start.set()

        else:
            logging.error('Пользователь ввел некорректные данные')
            raise ValueError

    except (ValueError,TypeError):
        logging.error('Пользователь ввел некорректные данные')
        await message.answer('Некорректные данные')
        await message.answer('Введите диапазон расстояний через "-", например 1-5')
        await SearchBestStates.distens.set()

# @dp.callback_query_handler(simple_cal_callback.filter(),state=search_best_states.date_start)
async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data,state:FSMContext):

    """"Отлавливаем событие (дата заселения) сравниваем с текущей датой, если данные не корректны- переспрашиваем
         иначе выводим календарь чтобы спросить дату выселения"""""

    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy():
            date_start = datetime.datetime.strptime(date.strftime("%Y-%m-%d"), '%Y-%m-%d').date()

        now = datetime.datetime.now().strftime('%Y-%m-%d')
        if now > str(date_start):
            await callback_query.message.answer(f"Дата заселения дожна быть больше {now}: ",
                                 reply_markup=await SimpleCalendar().start_calendar())

        else:
            search_params['check_in'] = date_start
            await SearchBestStates.date_finish.set()
            await callback_query.message.edit_text(f'Начало бронирования: {date_start}')
            await callback_query.message.answer('Выберите дату выселения:\n',
                reply_markup=await SimpleCalendar().start_calendar())

# @dp.callback_query_handler(simple_cal_callback.filter(), state=search_best_states.date_finish)
async def process_simple_calendar2(callback_query: types.CallbackQuery, callback_data, state: FSMContext):

    """ Отлавливаем событие (Дату выселения) если данные некорректны - переспрашиваем, иначе 
        выводим инлайн клавиатуру с кнопками (Да,Нет)"""""

    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy():
            date_finish = datetime.datetime.strptime(date.strftime("%Y-%m-%d"), '%Y-%m-%d').date()
            if str(date_finish) < str(search_params['check_in']):
                await callback_query.message.answer("Дата выселения должна быть больше даты заселения: ",
                                                    reply_markup=await SimpleCalendar().start_calendar())

            else:
                search_params['check_out'] = date_finish
                await callback_query.message.edit_text(f'Конец бронирования: {date_finish}')
                await state.reset_state()
                keyboard = InlineKeyboardMarkup(row_width=2)
                button_list = [InlineKeyboardButton(text=number, callback_data=f'wq{number}') for number in
                               ['Да', 'Нет']]
                keyboard.add(*button_list)
                await callback_query.message.answer('Хотите посмотреть фото отелей?', reply_markup=keyboard)


# @dp.callback_query_handler(Text(startswith='wq'))
async def photo_bestdeal(massege: types.CallbackQuery):

    """Отлавливаем нажатие кнопки (Да, Нет) 
    Если Да, то вызываем функцию bestdeal, 
    достаем результаты из базы данных отправляем пользователю и
    отпраляем группой фотографии,
    если Нет, от информация и базы данных отправляется без фотографий"""""

    await massege.answer('Подтверждено')
    checkIn = search_params['check_in']
    checkOut = search_params['check_out']
    distens = search_params['distens']
    priceMin = search_params['price'][0]
    priceMax = search_params['price'][1]
    distensMin = float(distens[0])
    distensMax = float(distens[1])
    if massege['data'][2:] == 'Да':
        await massege.message.answer('Уже ищу!')
        try:
            res = bestdeal(search_params['destinationId'], priceMin,
                           priceMax, distensMin, distensMax,
                           search_params['count'],checkIn,checkOut)
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
            bestdeal(search_params['destinationId'], priceMin, priceMax, distensMin,
                     distensMax,search_params['count'],checkIn,checkOut)
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
    dp.register_message_handler(bestdeal_locations_city,state=SearchBestStates.city)
    dp.register_message_handler(bestdeal_distens,state=SearchBestStates.distens)
    dp.register_message_handler(message_check,state=SearchBestStates.price)


def register_callback_query_handler(dp: Dispatcher):

    """ регистрируем callback_query_handler"""""

    dp.register_callback_query_handler(location_confirmation,Text(startswith='num'))
    dp.register_callback_query_handler(ansve_count_hotel,Text(startswith='_'))
    dp.register_callback_query_handler(photo_bestdeal,Text(startswith='wq'))
    dp.register_callback_query_handler(process_simple_calendar,simple_cal_callback.filter(),
                                       state=SearchBestStates.date_start)
    dp.register_callback_query_handler(process_simple_calendar2,simple_cal_callback.filter(),
                                       state=SearchBestStates.date_finish)
