from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from create_bot import search_params,dp
from request.request import hotel_search, locations_city
from create_bot import search_high_states



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
    button_list = [InlineKeyboardButton(text=key, callback_data=f'num{values}')
                   for key, values in locations_city_dct.items()]
    keyboard.add(*button_list)

    await message.answer('Подтвердите', reply_markup=keyboard)
    await state.reset_state()

# @dp.callback_query_handler(Text(startswith='num'))
async def location_confirmation(coll : types.CallbackQuery):

    """"" отлавливаем нажатие inlane кнопки """""""""

    await coll.answer('Подтверждено')
    destinationId = coll['data'][3:]
    search_params['destinationId'] = destinationId
    await coll.message.answer('Сколько отелей нужно вывести?')
    await search_high_states.number_city.set() # машино-состояние количество городов


# @dp.message_handler(state=search_high_states.number_city)
async def low_price_2(message: types.Message, state: FSMContext):
    count = message.text
    search_params['count'] = count
    sort_by = 'PRICE_HIGHEST_FIRST'
    await message.answer('Уже ищу!')
    msg = hotel_search(search_params['town'], sort_by, search_params['count'])
    await message.answer(msg)
    await state.reset_state()

def register_handlers_highprice(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['highprice'])
    dp.register_message_handler(low_price_1,state=search_high_states.city)
    dp.register_message_handler(low_price_2,state=search_high_states.number_city)

def register_handlers_callback_query_handler(dp : Dispatcher):
    dp.register_callback_query_handler(location_confirmation, Text(startswith='num'))