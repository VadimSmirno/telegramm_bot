from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import search_best_states,search_params
from request.request import locations_city
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from create_bot import dp
from request.request import bestdeal
import logging
from data_base import peewee_bd




# @dp.message_handler(commands=['bestdeal'])
async def low_price_0(message: types.Message):
    await message.reply('В каком городе ищем?')
    await search_best_states.city.set()


# @dp.message_handler(state=search_best_states.city)
async def low_price_1(message: types.Message, state: FSMContext):

    town = message.text
    search_params['town'] = town
    locations_city_dct = locations_city(town=town)
    keyboard = InlineKeyboardMarkup(row_width=1)
    button_list = [InlineKeyboardButton(text=key, callback_data=f'num{values}')
                   for key, values in locations_city_dct.items()]
    keyboard.add(*button_list)
    await message.answer('Подтвердите', reply_markup=keyboard)
    await state.reset_state()


# @dp.callback_query_handler(Text(startswith='num'))
async def location_confirmation(coll: types.CallbackQuery):
    await coll.answer('Подтверждено')
    destinationId = coll['data'][3:]
    search_params['destinationId'] = destinationId
    keyboard = InlineKeyboardMarkup(row_width=5)
    button_list = [InlineKeyboardButton(text= number,callback_data=f'_{number}') for number in ['1','2','3','4','5']]
    keyboard.add(*button_list)
    await coll.message.answer('Сколько отелей нужно вывести?',reply_markup=keyboard)




# @dp.callback_query_handler(Text(startswith='_'))
async def ansve_count_hotel(massege: types.CallbackQuery):
    count = massege['data'][-1]
    search_params['count'] = count
    await massege.message.answer('Введите диапазон цен через "-", например 1000-5000')
    await massege.answer()
    await search_best_states.price.set()

# @dp.message_handler(state=search_best_states.price)
async def message_check(massege: types.Message):
    price = massege.text.split('-')
    try:
        if int(price[0])<int(price[1]):
            search_params['price'] = price
            await massege.answer('На каком расстоянии от центра посмотреть отели? '
                                 'введите через "-" 4-10')
            await search_best_states.distens.set()
        else:
            await massege.answer('Некорректные данные')
            await massege.answer('Введите диапазон цен через "-", например 1000-5000')
            await search_best_states.price.set()
    except:
        logging.error('Пользователь ввел некорректные данные')
        await massege.answer('Некорректные данные')
        await massege.answer('Введите диапазон цен через "-", например 1000-5000')
        await search_best_states.price.set()


# @dp.message_handler(state=search_best_states.distens)
async def low_price_2(message: types.Message, state: FSMContext):
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
            # try:
            #     res = bestdeal(search_params['destinationId'], priceMin, priceMax, distensMin, distensMax,
            #                    int(search_params['count']))
            #     await message.answer(res)
            # except:
            #     logging.error('Ошибка в функции')

            await state.reset_state()
        else:
            logging.error('Пользователь ввел некорректные данные')
            raise Exception

    except:
        logging.error('Пользователь ввел некорректные данные')
        await message.answer('Некорректные данные')
        await message.answer('Введите диапазон расстояний через "-", например 1-5')
        await search_best_states.distens.set()

# @dp.callback_query_handler(Text(startswith='wq'))
async def photo_bestdeal(massege: types.CallbackQuery):
    await massege.answer('Подтверждено')
    distens = search_params['distens']
    priceMin = search_params['price'][0]
    priceMax = search_params['price'][1]
    distensMin = float(distens[0])
    distensMax = float(distens[1])
    if massege['data'][2:] == 'Да':
        await massege.message.answer('Уже ищу!')
        bestdeal(search_params['destinationId'], priceMin, priceMax, distensMin, distensMax,
                           int(search_params['count']))
        with peewee_bd.db:
            msg = peewee_bd.HotelInfo.select().\
                order_by(peewee_bd.HotelInfo.id.desc()).\
                limit(int(search_params['count']))
            for info_on_hotels in msg:
                res_msg = f'Название: {info_on_hotels.name}\n' \
                          f'Рейтинг: {info_on_hotels.rate}\n' \
                          f'Адрес:{info_on_hotels.addrres}\n' \
                          f'Цена:{info_on_hotels.price}\n'
                await massege.message.answer(res_msg)
                medias = types.MediaGroup()
                [medias.attach_photo(j) for j in [info_on_hotels.photo_url1, info_on_hotels.photo_url2]]
                await massege.message.answer_media_group(media=medias)

    else:

        try:
            bestdeal(search_params['destinationId'], priceMin, priceMax, distensMin, distensMax,
                           int(search_params['count']))
            with peewee_bd.db:
                msg = peewee_bd.HotelInfo.select(). \
                    order_by(peewee_bd.HotelInfo.id.desc()). \
                    Limit(int(search_params['count']))
                for info_on_hotels in msg:
                    res_msg = f'Название: {info_on_hotels.name}\n' \
                              f'Рейтинг: {info_on_hotels.rate}\n' \
                              f'Адрес:{info_on_hotels.addrres}\n' \
                              f'Цена:{info_on_hotels.price}\n' \
                              f'Расстояние до центра: {info_on_hotels.distens} км'
                    await massege.message.answer(res_msg)

        except:
            logging.error('Ошибка в функции')
            await massege.message.answer('По Вашим запросам ничего не найдено')


def register_handlers_bestdeal(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['bestdeal'])
    dp.register_message_handler(low_price_1,state=search_best_states.city)
    dp.register_message_handler(low_price_2,state=search_best_states.distens)
    dp.register_message_handler(message_check,state=search_best_states.price)


def register_callback_query_handler(dp: Dispatcher):
    dp.register_callback_query_handler(location_confirmation,Text(startswith='num'))
    dp.register_callback_query_handler(ansve_count_hotel,Text(startswith='_'))
    dp.register_callback_query_handler(photo_bestdeal,Text(startswith='wq'))
