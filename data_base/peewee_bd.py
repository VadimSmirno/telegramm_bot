from peewee import *
import datetime

db = SqliteDatabase('Hotels.db')

class BaseModel(Model):
    class Meta:
        database = db
        db_table = 'hotels informations'

class HotelInfo(BaseModel):
    name = CharField()
    id_hotels = IntegerField()
    rate = FloatField()  # рейтинг
    addrres = TextField()
    price = TextField()
    data = DateField()  # время создания
    photo_url1 = TextField()
    photo_url2 = TextField()
    distens = FloatField()  # расстояние до центра


def start_db():
    HotelInfo.create_table()





