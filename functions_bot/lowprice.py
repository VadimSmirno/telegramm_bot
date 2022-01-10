
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import search_params,dp,search_low_states
from request.request import hotel_search



# @dp.message_handler(commands=['lowprice'])
async def low_price_0(message: types.Message):
    await message.reply('В каком городе ищем?')
    await search_low_states.city.set()  # переход в машино-состояние город


# @dp.message_handler(state=search_low_states.city)
async def low_price_1(message: types.Message, state: FSMContext):
    town = message.text  # город
    search_params['town'] = town
    await message.answer('Сколько отелей нужно вывести?')
    await search_low_states.next() # машино-состояние количество городов


# @dp.message_handler(state=search_low_states.number_city)
async def low_price_2(message: types.Message, state: FSMContext):
    count = message.text
    search_params['count'] = count
    sort_by = 'PRICE'
    await message.answer('Уже ищу!')
    msg = hotel_search(search_params['town'], search_params['count'], sort_by)
    await message.answer(msg)
    await state.reset_state()  # сброс состояний


def register_handlers_lowprice(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['lowprice'])
    dp.register_message_handler(low_price_1,state=search_low_states.city)
    dp.register_message_handler(low_price_2,state=search_low_states.number_city)



