from aiogram import Bot, Dispatcher, executor
from aiogram.types import BotCommand
from app.handlers.common import register_handlers_common
from app.handlers.signup import register_handlers_signup
from app.handlers.admin import register_handlers_admin
from app.bot_global import bot, dp


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/singup", description="Регистрация"),
        BotCommand(command="/admin", description="Меню администратора"),
        BotCommand(command="/cancel", description="Сброс состояния диалога"),
    ]
    await bot.set_my_commands(commands)

async def shutdown(dispatcher: Dispatcher):
    """ Действие при завершении """
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

async def startup(dispatcher: Dispatcher):
    """ Действие перед запуском """
    register_handlers_common(dispatcher)
    register_handlers_signup(dispatcher)
    register_handlers_admin(dispatcher)
    await set_commands(bot)

if __name__ == "__main__":
    executor.start_polling(dp, on_shutdown=shutdown, on_startup=startup)