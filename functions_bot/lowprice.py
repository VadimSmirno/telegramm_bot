from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import search_params,SearchLowStates
from request.request import hotel_search, locations_city
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from data_base import peewee_bd
import logging
import datetime



# @dp.message_handler(commands=['lowprice'])
async def low_price_0(message: types.Message):

    """" После команды lowprice спрашиваем у пользователя 
     в каком городе ищем отель, запоминаем что он ввел
     через машино состояние"""""

    await message.reply('В каком городе ищем?')
    await SearchLowStates.city.set()  # переход в машино-состояние город


# @dp.message_handler(state=search_low_states.city)
async def low_price_1(message: types.Message, state: FSMContext):

    """" делаем request запрос и вытаскиваем чарез API название 
     локации и id локации в виде словаря
     {локация : id локации  и создаем inlane клавиатуру }"""""

    try:
        town = message.text  # город
        search_params['town'] = town
        locations_city_dct = locations_city(town=town)
        if len(locations_city_dct)!=0:
            keyboard = InlineKeyboardMarkup(row_width=1)
            button_list = [InlineKeyboardButton(text=key, callback_data=f'id{values}')
                           for key, values in locations_city_dct.items()]
            keyboard.add(*button_list)
            await message.answer('Подтвердите', reply_markup=keyboard)
            await state.reset_state()
        else:
            await message.answer(f'Ничего не нашел в городе {town}')
            await message.answer('Может в другом городе посмотрим отели?')
            await SearchLowStates.city.set()
    except AttributeError:
        logging.error('Ошибка в функции locations_city')

# @dp.callback_query_handler(Text(startswith='num'))
async def location_confirmation(coll : types.CallbackQuery):

    """"" отлавливаем нажатие inlane кнопки """""""""

    await coll.answer('Подтверждено')
    destinationId = coll['data'][2:]
    search_params['destinationId'] = destinationId
    await coll.message.answer('Сколько отелей нужно вывести? от 1 до 5')
    await SearchLowStates.number_city.set() # машино-состояние количество городов



# @dp.message_handler(state=search_low_states.number_city)
async def low_price_2(message: types.Message, state: FSMContext):

    """ из машино-состояния забираем количество отелей
     проверяем корректность введеных данных
     Создаем календарь для выбора даты заселения"""""

    count = message.text
    try:
        search_params['count'] = int(count)
        if  int(search_params['count']) > 5 or int(search_params['count'])<0:
            raise Exception
        await state.reset_state()
        await message.answer("Пожалуйста выберите дату заселения: ", reply_markup=await SimpleCalendar().start_calendar())
        await SearchLowStates.date_start.set()

    except Exception:
        logging.error('Пользователь неправильно ввел данные')
        await message.answer('Некорректный ввод.')
        await message.answer('Введите число не более 5')




# @dp.callback_query_handler(simple_cal_callback.filter(),state=search_low_states.date_start)
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
            await SearchLowStates.date_finish.set()
            await callback_query.message.edit_text(f'Начало бронирования: {date_start}')
            await callback_query.message.answer('Выберите дату выселения:\n',
                reply_markup=await SimpleCalendar().start_calendar())



# @dp.callback_query_handler(simple_cal_callback.filter(), state=search_low_states.date_finish)
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
                button_list = [InlineKeyboardButton(text=number, callback_data=f'да{number}') for number in
                               ['Да', 'Нет']]
                keyboard.add(*button_list)
                await callback_query.message.answer('Хотите посмотреть фото отелей?', reply_markup=keyboard)


# @dp.register_callback_query_handler(Text(startswith='да'))
async def photo(massege: types.CallbackQuery):

    """Вызываем функцию hotel_search в которой собирается информация по отелям через API.
    из базы данных отправляем нужную информацию сообщением пользователю. 
    Если пользователь нажал да, то из базы данных достаем ссылку  на фото и отпарвляем
    через MediaGroup. Если нет, то фото не отправляются. 
    """""

    await massege.answer('Подтверждено')
    checkIn = search_params['check_in']
    checkOut = search_params['check_out']
    if massege['data'][2:]== 'Да':
        sort_by = 'PRICE'


        await massege.message.answer('Уже ищу!')
        hotel_search(search_params['destinationId'], sort_by, str(search_params['count']),checkIn,checkOut)
        with peewee_bd.db:
            msg = peewee_bd.HotelInfo.select().\
                order_by(peewee_bd.HotelInfo.id.desc()).\
                limit(int(search_params['count'])) #  сортируем таблицу бд в обратном порядке и забираем первые данные

        for info_on_hotels in msg:

            res_msg =f'Название: {info_on_hotels.name}\n' \
                     f'Рейтинг: {info_on_hotels.rate}\n' \
                     f'Адрес:{info_on_hotels.addrres}\n' \
                     f'Стоимость проживания:{info_on_hotels.price}\n' \

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
        hotel_search(search_params['destinationId'], sort_by, str(search_params['count']),checkIn,checkOut)
        msg = peewee_bd.HotelInfo.select().\
            order_by(peewee_bd.HotelInfo.id.desc()).\
            limit(int(search_params['count']))
        for info_on_hotils in msg:
            res_msg = f'Название: {info_on_hotils.name}\n' \
                      f'Рейтинг: {info_on_hotils.rate}\n' \
                      f'Адрес:{info_on_hotils.addrres}\n' \
                      f'Стоимость проживания:{info_on_hotils.price}\n' \

            url_hotels = InlineKeyboardMarkup(row_width=1)
            url_botton = InlineKeyboardButton(text='Ссылка на отель',
                                              url=f'https://ru.hotels.com/ho{info_on_hotils.id_hotels}')
            url_hotels.add(url_botton)
            await massege.message.answer(res_msg,reply_markup=url_hotels)




def register_handlers_lowprice(dp : Dispatcher):

    """ Регистрируем message_handler"""""

    dp.register_message_handler(low_price_0,commands=['lowprice'])
    dp.register_message_handler(low_price_1,state=SearchLowStates.city)
    dp.register_message_handler(low_price_2,state=SearchLowStates.number_city)



def register_handlers_examination(dp:Dispatcher):

    """регистрируем  callback_query_handler"""""

    dp.register_callback_query_handler(location_confirmation,Text(startswith='id'))
    dp.register_callback_query_handler(photo,Text(startswith='да'))
    dp.register_callback_query_handler(process_simple_calendar,simple_cal_callback.filter())
    dp.register_callback_query_handler(process_simple_calendar,simple_cal_callback.filter(),
                                       state=SearchLowStates.date_start)
    dp.register_callback_query_handler(process_simple_calendar2, simple_cal_callback.filter(),
                                       state=SearchLowStates.date_finish)


