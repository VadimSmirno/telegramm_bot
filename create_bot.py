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
                 'count': 0}

class search_low_states(StatesGroup):
    city = State()
    number_city = State()




