from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types
from tasks_notify import send_all_tasks, send_personal_tasks
from app.service.config import TelegramConfig
from aiogram.dispatcher.filters import ChatTypeFilter
from app.bot_global import db_file
from app.service.db import User
from app.bot_global import logger

tg_config = TelegramConfig()     

user = User(db_file)   


def is_full_report(message: types.Message) -> bool:
    return message.chat.type == types.ChatType.GROUP or \
        message.chat.type == types.ChatType.SUPERGROUP

def is_personal_report(message: types.Message) -> bool:
    return message.chat.type == types.ChatType.PRIVATE and user.get_user(message.from_user.id)


async def cmd_tasks_notifications(message: types.Message, state: FSMContext):
    await message.answer(
        "Запуск генерации списка заявок. Пожалуйста ожидайте"
    )
    if is_personal_report(message):
        await send_personal_tasks()
    elif is_full_report(message):
        await send_all_tasks()
    else:
        logger.warning("Генерация отчета запрошена пользователем, \
                       не состоящим в группе и не прошедшим регистрацию")

def register_handlers_event(dp: Dispatcher):
    dp.register_message_handler(
        cmd_tasks_notifications,
        commands="tasks",
        state="*"
        )
