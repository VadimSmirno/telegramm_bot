from peewee import *
import datetime

db = SqliteDatabase('Hotels.db')

class BaseModel(Model):
    class Meta:
        database = db
        db_table = 'hotels informations'

class HotelInfo(BaseModel):
    name = CharField()
    id_hotels = TextField()
    rate = TextField()  # рейтинг
    addrres = TextField()
    price = TextField()
    data = DateField()  # время создания
    photo_url1 = TextField()
    photo_url2 = TextField()
    distens = TextField()  # расстояние до центра


def start_db():
    HotelInfo.create_table()

# l=[['Хостел Travel Inn на Преображенской', '1576205920', '2.0', 'ул. Девятая Рота, 6, стр. 2', '1,161 RUB', datetime.datetime(2022, 1, 27, 11, 7, 49, 141512), '', ''],
#    ['Хостел Bed&Beer Таганка', '1219660160', '1.5', 'ул. Александра Солженицына, 31-2 ', '1,071 RUB', datetime.datetime(2022, 1, 27, 11, 7, 49, 141512), '', ''],
#    ['Хостел Travel Inn Красные Ворота', '1576222336', '2.0', 'ул. Новая Басманная, 1, стр. 10', '1,071 RUB', datetime.datetime(2022, 1, 27, 11, 7, 49, 141512), '', '']]
#
#
# with db:
#     info_hot =HotelInfo.insert_many(l).execute()



