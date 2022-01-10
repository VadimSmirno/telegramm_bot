from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import search_params,dp
from request.request import hotel_search

class search_high_states(StatesGroup):
    city = State()
    number_city = State()

# @dp.message_handler(commands=['git '])
async def low_price_0(message: types.Message):
    await message.reply('В каком городе ищем?')
    await search_high_states.city.set()


# @dp.message_handler(state=search_high_states.city)
async def low_price_1(message: types.Message, state: FSMContext):
    town = message.text
    search_params['town'] = town
    await message.answer('Сколько отелей нужно вывести?')
    await search_high_states.next()


# @dp.message_handler(state=search_high_states.number_city)
async def low_price_2(message: types.Message, state: FSMContext):
    count = message.text
    search_params['count'] = count
    sort_by = 'PRICE_HIGHEST_FIRST'
    await message.answer('Уже ищу!')
    msg = hotel_search(search_params['town'], search_params['count'], sort_by)
    await message.answer(msg)
    await state.reset_state()

def register_handlers_highprice(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['highprice'])
    dp.register_message_handler(low_price_1,state=search_high_states.city)
    dp.register_message_handler(low_price_2,state=search_high_states.number_city)