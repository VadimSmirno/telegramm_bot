from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from create_bot import search_params,search_low_states
from request.request import hotel_search, locations_city



# @dp.message_handler(commands=['lowprice'])
async def low_price_0(message: types.Message):

    """" После команды lowprice спрашиваем у пользователя 
     в каком городе ищем отель, запоминаем что он ввел
     через машино состояние"""""

    await message.reply('В каком городе ищем?')
    await search_low_states.city.set()  # переход в машино-состояние город


# @dp.message_handler(state=search_low_states.city)
async def low_price_1(message: types.Message, state: FSMContext):

    """" делаем request запрос и вытаскиваем чарез API название 
     локации и id локации в виде словаря
     {локация : id локации  и создаем inlane клавиатуру }"""""

    town = message.text  # город
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
    await search_low_states.number_city.set() # машино-состояние количество городов


# @dp.message_handler(state=search_low_states.number_city)
async def low_price_2(message: types.Message, state: FSMContext):

    """ из машино-состояния забираем количество отелей
     делаем request запрос и отправляем в чат нужную информацию"""""

    count = message.text
    search_params['count'] = count
    sort_by = 'PRICE'
    await message.answer('Уже ищу!')
    msg = hotel_search(search_params['destinationId'], sort_by, search_params['count'])
    await message.answer(msg)
    await state.reset_state()  # сброс состояний


def register_handlers_lowprice(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['lowprice'])
    dp.register_message_handler(low_price_1,state=search_low_states.city)
    dp.register_message_handler(low_price_2,state=search_low_states.number_city)

def register_handlers_examination(dp:Dispatcher):
    dp.register_callback_query_handler(location_confirmation,Text(startswith='num'))



