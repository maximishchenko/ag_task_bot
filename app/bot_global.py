"""
Глобальная конфигурация приложения.

Установка глобальных переменных, которые впоследстии импортируются
скриптами приложения
"""

# Standard Library
import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage

from app.service.config import CobraConfig, TelegramConfig

config_file = "config/config.ini"
fsm_state_file = "job/states.json"
log_config_file = "config/log.ini"
db_file = "db.sqlite3"


tg_config = TelegramConfig(config_file)
cobra_config = CobraConfig(config_file)

logging.config.fileConfig(log_config_file, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = Bot(token=tg_config.get_token(), loop=loop)
dp = Dispatcher(bot, storage=JSONStorage(fsm_state_file))
