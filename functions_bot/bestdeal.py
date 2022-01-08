from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import dp
from request.request import hotel_search


class search_best_states(StatesGroup):
    q1 = State()
    q2 = State()

# @dp.message_handler(commands=['bestdeal'])
async def low_price_0(message: types.Message):
    await message.reply('В каком городе ищем?')
    await search_best_states.q1.set()


# @dp.message_handler(state=search_best_states.q1)
async def low_price_1(message: types.Message, state: FSMContext):
    city = message.text
    await message.answer('Сколько отелей нужно вывести?')
    await search_best_states.next()


# @dp.message_handler(state=search_best_states.q2)
async def low_price_2(message: types.Message, state: FSMContext):
    count = message.text
    # запрос api
    await state.reset_state()

def register_handlers_bestdeal(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['bestdeal'])
    dp.register_message_handler(low_price_1,state=search_best_states.q1)
    dp.register_message_handler(low_price_2,state=search_best_states.q2)