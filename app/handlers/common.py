"""
Обработчик базовых команд бота.

Реализует поведение базовых команд: /start и /cancel (сброс состояния диалога)
"""

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext


async def cmd_start(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start.

    Завершает состояние предыдущего диалога (при наличии).
    Выводит краткую справку.

    Args:
        message (types.Message): полученное сообщение
        state (FSMContext): состояние диалога
    """
    await state.finish()
    await message.answer(
        "Для получения доступа к функциям бота зарегистрируйтесь и дождитесь \
подтверждения администратором. Для запуска процесса регистрации введите или \
выберите в меню бота команду /signup"
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    """
    Обработчик команды /calcel (сброс состояния диалога).

    Сбрасывает состояние диалога. Возвращает ответное сообщение.

    Args:
        message (types.Message): полученное сообщение
        state (FSMContext): состояние диалога
    """
    await state.finish()
    reply_kb = types.ReplyKeyboardRemove()
    await message.answer("Диалог завершен", reply_markup=reply_kb)


def register_handlers_common(dp: Dispatcher):
    """
    Регистрация обработчиков событий.

    Args:
        dp (Dispatcher): диспетчер обновлений
    """
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
