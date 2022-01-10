from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types,Dispatcher
from create_bot import dp
from create_bot import search_low_states
from aiogram.dispatcher import FSMContext


inkb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='парсер из api',callback_data='api'))

@dp.message_handler(state=search_low_states.city)
async def examination (massage : types.Message,state : FSMContext):
    await massage.answer('Подтвердите',reply_markup=inkb)
    await state.reset_state() # сброс состояния

@dp.callback_query_handler(text='api')
async def location_confirmation(callbac : types.CallbackQuery):
    await callbac.answer('Подтверждено')
    await callbac.answer()

def register_handlers_examination(dp : Dispatcher):
    dp.register_message_handler(examination,state=search_low_states)

def register_callback_query_handler(dp : Dispatcher):
    dp.register_callback_query_handler(location_confirmation,text='api')

