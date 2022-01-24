from peewee import *
from datetime import datetime

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
    distens = TextField()  # расстояние до центра
    photo_url = TextField()


HotelInfo.create_table()





