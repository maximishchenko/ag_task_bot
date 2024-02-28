"""
Скрипт реализует логику регистрации.

Т.к. необходимо однозначно идентифицировать чат Telegram и пользователя
приложения "Мобильный техник", каждый пользователь должен пройти процедуру
регистрации для получения доступа к персональным функциям бота.

"""

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter

from app.bot_global import cobra_config, db_file
from app.handlers.state import Signup
from app.service.cobra import CobraTehn
from app.service.db import MobileAppAccount, OneUser, User
from app.service.status import Status

# TODO перенести в bot_global.py
user = User(db_file)
cobra_account = CobraTehn(cobra_config)
signup_state = Signup()


async def cmd_signup(message: types.Message, state: FSMContext):
    """
    Обработчик команды регистрации пользователя /signup.

    Проверяет тип чата.
    Если чат приватный запрашивает имя пользователя.
    В случае, если команда регистрации отправлена в группе (или супергруппе),
    возвращает сообщение об ошибке

    Args:
        message (types.Message): полученное сообщение
        state (FSMContext): текущее состояние диалога
    """
    await state.finish()
    if message.chat.type != types.ChatType.PRIVATE:
        await message.answer(
            "Регастрация не доступна в группе. \
Регистрация возможна только в прямом диалоге с ботом"
        )
        await state.finish()
        return
    if user.is_user_exists(message.from_user.id):
        already_signed_up_msg = "Вы уже зарегистрированы. Регистрация \
не требуется"
        await message.answer(already_signed_up_msg)
        await state.finish()
        return
    input_pwd_msg = 'Введите имя пользователя от приложения "Мобильный техник"'
    await message.answer(input_pwd_msg)
    await Signup.wating_username.set()


async def get_username(message: types.Message, state: FSMContext) -> None:
    """
    Обработка полученного имени пользователя.

    Получает имя пользователя из приложения "Мобильный техник".
    Сохраняет в FSM. Запрашивает пароль к приложению "Мобильный техник"

    Args:
        message (types.Message): полученное сообщение
        state (FSMContext): текущее состояние диалога
    """
    async with state.proxy() as data:
        data[signup_state.username_param] = message.text
    await message.answer('Введите пароль приложения "Мобильный техник"')
    await Signup.waiting_password.set()
    return


async def get_password(message: types.Message, state: FSMContext) -> None:
    """
    Обработка имени пользователя и пароля.

    Получает пароль от приложения "Мобильный техник".
    Получает имя пользователя, переданное на предыдущем этапе диалога из FSM.
    Сверяет данные с данными, возвращаемыми КПО Кобра.
    Если данные совпадают - добавляет пользователя в БД. В поле tehn таблицы
    user записывает имя пользователя от приложения "Мобильный техник".
    Сбрасывает состояние диалога

    Args:
        message (types.Message): полученное сообщение
        state (FSMContext): текущее состояние диалога
    """
    user_data = await state.get_data()
    username = user_data[signup_state.username_param]
    password = message.text
    account = MobileAppAccount(username=username, password=password)
    one_user = OneUser(
        chat_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        status=Status.active,
        tehn=username,
    )
    if cobra_account.is_account_valid(account):
        user.add_user(one_user)
        await message.answer(
            "Вы успешно зарегистрированы. Теперь вы можете получить доступ \
к функциям бота"
        )
    else:
        await message.answer(
            "Неверное имя пользователя или пароль. Пользователь \
не зарегистрирован. Если вы ошиблись при вводе данных - пройдите регистрацию \
заново"
        )
    await state.finish()
    return


def register_handlers_signup(dp: Dispatcher):
    """
    Регистрация обработчиков событий для команды регистрации.

    Args:
        dp (Dispatcher): диспетчер обновлений
    """
    dp.register_message_handler(cmd_signup, commands="signup", state="*")
    dp.register_message_handler(
        get_username,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        state=Signup.wating_username,
    )
    dp.register_message_handler(
        get_password,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        state=Signup.waiting_password,
    )
