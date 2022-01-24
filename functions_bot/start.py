from aiogram import types, Dispatcher



start_message = 'Привет! Я помогу тебе  выбрать самые классные отели по твоим запросам.\n\
						 Получить самые дешевые отели: команда /lowprice,\n\
						 Получить самые дорогие отели: команда /highprice, \n\
						 '

# @dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(start_message)

def register_handlers_start(dp : Dispatcher):
    dp.register_message_handler(cmd_start,commands=['start', 'help'])