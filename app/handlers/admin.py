from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types

async def cmd_admin_list(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Добро пожаловать в меню администратора. Выберите команду из предложенных ниже:\r\n\r\n \
/admin_users_list - список пользователей \r\n \
/admin_notify_tasks - принудительный запуск уведомлений о заявках"
    )

async def cmd_admin_users_list(message: types.Message, state: FSMContext):
    # TODO Реализовать вывод кнопок с именами пользователей и возможность управления пользователями
    await message.answer("Реализовать вывод кнопок с именами пользователей")

async def cmd_admin_notify_tasks(message: types.Message, state: FSMContext):
    # TODO реализовать принудительный запуск уведомлений пользователей о задачах на случай, если будет пропущен плановый запуск
    await message.answer("Реализовать принудительный запуск уведомлений о задачах")


def register_handlers_admin(dp: Dispatcher):
    # TODO действие доступно только администратору
    dp.register_message_handler(cmd_admin_list, commands="admin", state="*")
    dp.register_message_handler(cmd_admin_users_list, commands="admin_users_list", state="*")
    dp.register_message_handler(cmd_admin_notify_tasks, commands="admin_notify_tasks", state="*")
