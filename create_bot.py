from aiogram.dispatcher.filters.state import State, StatesGroup
from decouple import config
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging

TOKEN = config('TOKEN')
RapidAPI = config('RapidAPI')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

search_params = {'town': 0,
                 'count': 0,
                 'destinationId':0,
                 'price':0,
                 'distens':0,
                 'check_in':0,
                 'check_out':0}


class SearchLowStates(StatesGroup):
    city = State()
    number_city = State()
    date_start = State()
    date_finish = State()

class SearchHighStates(StatesGroup):
    city = State()
    number_city = State()
    date_start = State()
    date_finish = State()

class SearchBestStates(StatesGroup):
    city = State()
    number_city = State()
    price = State()
    distens = State()
    date_start = State()
    date_finish = State()



