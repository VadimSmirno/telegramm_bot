from aiogram import  executor
from create_bot import dp
from functions_bot import start,lowprice,highprice,bestdeal
from data_base.peewee_bd import HotelInfo




start.register_handlers_start(dp)
lowprice.register_handlers_lowprice(dp)
highprice.register_handlers_highprice(dp)
bestdeal.register_handlers_bestdeal(dp)
lowprice.register_handlers_examination(dp)
highprice.register_handlers_callback_query_handler(dp)
bestdeal.register_handlers_bestdeal(dp)
bestdeal.register_callback_query_handler(dp)
HotelInfo.create_table()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)