from aiogram import Bot, Dispatcher, executor
from aiogram.types import BotCommand
from app.handlers.common import register_handlers_common
from app.handlers.signup import register_handlers_signup
from app.handlers.event import register_handlers_event
from app.bot_global import bot, dp

PYTHONDONTWRITEBYTECODE = 1


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/signup", description="Регистрация"),
        BotCommand(command="/tasks", description="Генерация списка заявок"),
        BotCommand(command="/my_tasks", description="Мои заявки"),
        BotCommand(command="/cancel", description="Сброс состояния диалога"),
    ]
    await bot.set_my_commands(commands)


async def shutdown(dispatcher: Dispatcher):
    """Действие при завершении"""
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def startup(dispatcher: Dispatcher):
    """Действие перед запуском"""
    register_handlers_common(dispatcher)
    register_handlers_signup(dispatcher)
    register_handlers_event(dispatcher)
    await set_commands(bot)


if __name__ == "__main__":
    executor.start_polling(dp, on_shutdown=shutdown, on_startup=startup)
