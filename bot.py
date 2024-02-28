"""
Скрипт запуска бота.

Реализует интерфейс взаимодействия с функциями бота
"""

from aiogram import Bot  # noqa
from aiogram import Dispatcher  # noqa
from aiogram import executor  # noqa
from aiogram.types import BotCommand  # noqa

from app.bot_global import bot as bot_app  # noqa
from app.bot_global import dp  # noqa
from app.handlers.common import register_handlers_common  # noqa
from app.handlers.event import register_handlers_event  # noqa
from app.handlers.signup import register_handlers_signup  # noqa


async def set_commands(bot: Bot):
    """
    Установка команд бота.

    Args:
        bot (Bot): экземпляр бота
    """
    commands = [
        BotCommand(command="/signup", description="Регистрация"),
        BotCommand(command="/tasks", description="Генерация списка заявок"),
        BotCommand(command="/my_tasks", description="Мои заявки"),
        BotCommand(command="/cancel", description="Сброс состояния диалога"),
    ]
    await bot.set_my_commands(commands)


async def shutdown(dispatcher: Dispatcher):
    """
    Действие при завершении.

    Сохраняет состояние диалога при завершении работы приложения

    Args:
        dispatcher (Dispatcher): диспетчер обновлений
    """
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def startup(dispatcher: Dispatcher):
    """

    Действие перед запуском.

    Регистрация обработчиков событий.
    Установка команд бота

    Args:
        dispatcher (Dispatcher): диспетчер обновлений
    """
    register_handlers_common(dispatcher)
    register_handlers_signup(dispatcher)
    register_handlers_event(dispatcher)
    await set_commands(bot_app)


if __name__ == "__main__":
    executor.start_polling(dp, on_shutdown=shutdown, on_startup=startup)
