from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types
from app.bot_global import tg_config, bot, dp, db_file
from app.service.db import User
from app.service.status import Status, StatusAction

user = User(db_file)

def get_user_states_keyboard(admin_chat_id: str, user_chat_id: str):
    """ Генерация кнопок для подтверждения регистрации пользователя 
    администратором """
    buttons = [
        [
            types.InlineKeyboardButton(text="Активировать", callback_data=f"{StatusAction.act_enable_user}|{admin_chat_id}|{user_chat_id}"),
            types.InlineKeyboardButton(text="Заблокировать", callback_data=f"{StatusAction.act_disable_user}|{admin_chat_id}|{user_chat_id}")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def cmd_signup(message: types.Message, state: FSMContext):
    """ Обработчик команды регистрации пользователя.
    Направляет всем администраторам уведомление о регистрации пользователя
    Предлагает набор кнопок для активации или блокировки пользователя """
    if user.is_user_exists(message.from_user.id):
        await message.answer("Вы уже зарегистрированы, обратитесь к администратору для активации")
        return

    user.add_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username, Status.inactive)

    admin_notify_message = f"Зарегистрирован новый пользователь: {message.from_user.username}. Разрешить ему взаимодействие с ботом?"
    
    admin_chat_ids = tg_config.get_admin_chat_ids()
    for admin in admin_chat_ids:
        keyboard = get_user_states_keyboard(admin, message.from_user.id)
        await bot.send_message(admin, admin_notify_message, reply_markup=keyboard)
    
    await message.answer("Запрос регистрации отправлен администратору, дождитесь уведомления о подтверждении регистрации")


@dp.callback_query_handler(lambda command: command.data and command.data.startswith('act_'))
async def process_user(callback_query: types.CallbackQuery):
    """ Обработка действий администратора для подтверждения регистрации 
    пользователя """
    params = callback_query.data.split("|")
    action = params[0]
    admin_chat_id = params[1]
    user_chat_id = params[2]
    if not user.is_user_exists(user_chat_id):
        msg = f"Пользователь с ID чата {user_chat_id} отсутствует в БД и к нему невозможно применить данное действие. Возможно пользователь был удален"
        await bot.send_message(admin_chat_id, msg)
        return
    if action == StatusAction.act_enable_user:
        admin_reply_message = "Вы подтвердили запрос. Теперь пользователь может получить доступ к функциям бота"
        user_reply_message = "Администратор подтвердил ваш запрос. Теперь вы можете получить доступ к функциям бота"
        status = Status.active
    elif action == StatusAction.act_disable_user:
        admin_reply_message = "Вы отклонили запрос. Теперь пользователь не может получить доступ к функциям бота"
        user_reply_message = "Администратор отклонил ваш запрос. Теперь вы не можете получить доступ к функциям бота"
        status = Status.inactive
    else:
        await bot.send_message(admin_chat_id, "Передано неизвестное событие. Указанная команда не может быть выполнена")
        return
    user.change_status(user_chat_id, status)
    # TODO связать с техником
    await bot.send_message(admin_chat_id, admin_reply_message)
    await bot.send_message(user_chat_id, user_reply_message)

def register_handlers_signup(dp: Dispatcher):
    dp.register_message_handler(cmd_signup, commands="signup", state="*")

    