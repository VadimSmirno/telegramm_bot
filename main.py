from aiogram import  executor
#from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from create_bot import dp
from functions_bot import start,lowprice,highprice,bestdeal

start.register_handlers_start(dp)
lowprice.register_handlers_lowprice(dp)
highprice.register_handlers_highprice(dp)
bestdeal.register_handlers_bestdeal(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)