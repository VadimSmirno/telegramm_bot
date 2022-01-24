from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import search_best_states,search_params
from request.request import locations_city
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from create_bot import dp
from request.request import bestdeal




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


@dp.callback_query_handler(Text(startswith='num'))
async def location_confirmation(coll: types.CallbackQuery):
    await coll.answer('Подтверждено')
    destinationId = coll['data'][3:]
    search_params['destinationId'] = destinationId
    keyboard = InlineKeyboardMarkup(row_width=5)
    button_list = [InlineKeyboardButton(text= number,callback_data=f'_{number}') for number in ['1','2','3','4','5']]
    keyboard.add(*button_list)
    await coll.message.answer('Сколько отелей нужно вывести?',reply_markup=keyboard)




@dp.callback_query_handler(Text(startswith='_'))
async def ansve_count_hotel(massege: types.CallbackQuery):
    count = massege['data'][-1]
    search_params['count'] = count
    await massege.message.answer('Введите диапазон цен через "-", например 1000-5000')
    await massege.answer()
    await search_best_states.price.set()

@dp.message_handler(state=search_best_states.price)
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
        await massege.answer('Некорректные данные')
        await massege.answer('Введите диапазон цен через "-", например 1000-5000')
        await search_best_states.price.set()

# @dp.message_handler(state=search_best_states.price)
# async def distens_range(massage: types.Message):
#     price = massage.text.split('-')
#     search_params['price'] = price
#     await massage.answer('На каком расстоянии от центра посмотреть отели? '
#                          'введите через "-" 4-10')
#     await search_best_states.next()



@dp.message_handler(state=search_best_states.distens)
async def low_price_2(message: types.Message, state: FSMContext):
    distens = message.text.split('-')
    search_params['distens'] = distens
    priceMin = search_params['price'][0]
    priceMax = search_params['price'][1]
    distensMin = float(distens[0])
    distensMax = float(distens[1])
    res = bestdeal(search_params['destinationId'],priceMin,priceMax,distensMin,distensMax,int(search_params['count']))
    await message.answer(res)
    await state.reset_state()

def register_handlers_bestdeal(dp : Dispatcher):
    dp.register_message_handler(low_price_0,commands=['bestdeal'])
    dp.register_message_handler(low_price_1,state=search_best_states.city)


def register_callback_query_handler(dp: Dispatcher):
    dp.register_callback_query_handler(location_confirmation,Text(startswith='num'))
    dp.callback_query_handler(ansve_count_hotel,Text(startswith='_'))
