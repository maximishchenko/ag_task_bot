from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
import asyncio
from app.service.config import TelegramConfig

tg_config = TelegramConfig()
fsm_state_file = "job/states.json"

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = Bot(token=tg_config.get_token(), loop=loop)
dp = Dispatcher(bot, storage=JSONStorage(fsm_state_file))

db_file = 'db.sqlite3'