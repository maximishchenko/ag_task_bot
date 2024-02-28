from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
import asyncio
import logging
import logging.config
from app.service.config import TelegramConfig
from app.service.config import CobraConfig

tg_config = TelegramConfig()
cobra_config = CobraConfig()
fsm_state_file = "job/states.json"
log_config_file = "config/log.ini"


logging.config.fileConfig(log_config_file, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = Bot(token=tg_config.get_token(), loop=loop)
dp = Dispatcher(bot, storage=JSONStorage(fsm_state_file))

db_file = "db.sqlite3"
