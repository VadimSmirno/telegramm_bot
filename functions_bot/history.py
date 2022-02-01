
from aiogram import types,Dispatcher
from data_base import peewee_bd



async def requsts_history(message:types.Message):
    with peewee_bd.db:
        msg = peewee_bd.HotelInfo.select(). \
            order_by(peewee_bd.HotelInfo.id.desc()). \
            limit(5)
        for info_history in msg:
            res_message = f'Название: {info_history.name}\n' \
                          f'Рейтинг: {info_history.rate}\n' \
                          f'Адрес:{info_history.addrres}\n' \
                          f'Цена:{info_history.price}\n' \
                          f'Дата запроса: {info_history.data}'
            await message.answer(res_message)
            medias = types.MediaGroup()
            [medias.attach_photo(j) for j in [info_history.photo_url1, info_history.photo_url2]]
            await message.answer_media_group(media=medias)

def register_history(dp : Dispatcher):
    dp.register_message_handler(requsts_history,commands=['history'])