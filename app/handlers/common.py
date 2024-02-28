from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Для получения доступа к функциям бота зарегистрируйтесь и дождитесь \
подтверждения администратором. Для запуска процесса регистрации введите или \
выберите в меню бота команду /signup"
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    reply_kb = types.ReplyKeyboardRemove()
    await message.answer("Диалог завершен", reply_markup=reply_kb)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
