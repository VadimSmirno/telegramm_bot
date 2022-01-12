from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types,Dispatcher
from create_bot import search_low_states,dp
from aiogram.dispatcher import FSMContext

dct={'Москва, Россия': '1153093',
     'Центр Москвы, Москва, Россия': '10565407',
     'Измайлово, Москва, Россия': '10779356',
     'Арбат, Москва, Россия': '1665959',
     'Сокольники, Москва, Россия': '1786031'}

keyboard = InlineKeyboardMarkup(row_width=1)

button_list = [InlineKeyboardButton(text=key, callback_data=values) for key,values in dct.items()]
keyboard.add(*button_list)

@dp.message_handler(state=search_low_states.city)
async def examination (massage : types.Message,state : FSMContext):
    await massage.answer('Подтвердите',reply_markup=keyboard)
    await state.reset_state() # сброс состояния

@dp.callback_query_handler(text='1153093')
async def location_confirmation(callbac : types.CallbackQuery):
    await callbac.answer('Подтверждено')
    await callbac.answer()

def register_handlers_examination(dp : Dispatcher):
    dp.register_message_handler(examination,state=search_low_states)

def register_callback_query_handler(dp : Dispatcher):
    dp.register_callback_query_handler(location_confirmation,text='api')

