from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types
from tasks_notify import send_tasks
import asyncio
from aiogram.dispatcher.filters import ChatTypeFilter

async def cmd_tasks_notifications(message: types.Message, state: FSMContext):
    await message.answer(
        "Запуск генерации списка заявок. Пожалуйста ожидайте"
    )
    await send_tasks()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(send_tasks())



def register_handlers_event(dp: Dispatcher):
    dp.register_message_handler(
        cmd_tasks_notifications,
        ChatTypeFilter(chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP]),
        commands="tasks",
        state="*"
        )
