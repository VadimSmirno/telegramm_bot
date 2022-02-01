from aiogram import types, Dispatcher



start_message = f'Привет! Я помогу тебе  выбрать самые классные отели по твоим запросам.\n' \
                f'Получить самые дешевые отели: команда /lowprice,\n' \
                f'Получить самые дорогие отели: команда /highprice,\n ' \
                f'Вывод отелей, наиболее подходящих по цене и расположению от центра /bestdeal\n ' \
                f'История запросов /history'

# @dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(start_message)

def register_handlers_start(dp : Dispatcher):
    dp.register_message_handler(cmd_start,commands=['start', 'help'])