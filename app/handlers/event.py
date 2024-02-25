from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types
from tasks_notify import send_all_tasks, send_personal_tasks
from app.service.config import TelegramConfig
from aiogram.dispatcher.filters import ChatTypeFilter
from app.bot_global import db_file, cobra_config, dp, bot
from app.service.db import User
from app.bot_global import logger
from app.service.cobra import CobraTaskReport, CobraTaskReportMessage
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


tg_config = TelegramConfig()     

user = User(db_file)   
cobra_tasks = CobraTaskReport(cobra_config)


def is_group_or_supergroup(message: types.Message) -> bool:
    """ Проверяет пришло ли полученное сообщение в группу или супергруппу

    Args:
        message (types.Message): полученное сообщение

    Returns:
        bool: резуальтат проверки
    """
    return message.chat.type == types.ChatType.GROUP or \
        message.chat.type == types.ChatType.SUPERGROUP

def is_private_chat(message: types.Message) -> bool:
    """ Проверяет пришло ли полученное сообщение в приватный чат

    Args:
        message (types.Message): полученное сообщение

    Returns:
        bool: результат проверки
    """
    return message.chat.type == types.ChatType.PRIVATE and \
        user.get_user(message.from_user.id)

def get_task_action_params(data: str) -> tuple:
    params = data.split("|")
    cobra_task_id = params[1]
    chat_id = params[2]
    return cobra_task_id, chat_id


async def cmd_tasks_notifications(message: types.Message, state: FSMContext):
    """ Генерация списка оперативных заявоук в зависимости от типа чата
    Если команда была передана в группе - вернет общий список заявок
    Если команда была передана в приватном чате - персональный список заявок
    при наличии

    Args:
        message (types.Message): полученное сообщение
        state (FSMContext): состояние диалога
    """
    pre_msg = "Запуск генерации списка заявок. Пожалуйста ожидайте"
    if is_private_chat(message):
        await message.answer(pre_msg)
        await send_personal_tasks()
    elif is_group_or_supergroup(message):
        await message.answer(pre_msg)
        await send_all_tasks()
    else:
        logger.warning("Генерация отчета запрошена пользователем, \
                       не состоящим в группе и не прошедшим регистрацию")
        

async def cmd_my_tasks_list(message: types.Message, state: FSMContext):
    await state.finish()
    if is_private_chat(message):
        my_user = user.get_user(message.chat.id)
        if not my_user or not my_user.tehn:
            await message.answer("Вам не доступна возможность запроса списка \
персональных заявок, т.к. вы не зарегистрированы или отсутствует связь \
с техником КПО Кобра. Пройдите процедуру регистрации или обратитесь к \
администратору для проверки связи с техником КПО Кобра")
            await state.finish()
            return
        # Построить inline buttons и передать сообщение
        my_tasks = cobra_tasks.get_my_tasks(my_user.tehn)
        my_tasks_btns = []
        if len(my_tasks):
            for task in my_tasks:
                my_tasks_btns.append(types.InlineKeyboardButton(text=task['n_abs'], callback_data=f"task|{task['n_abs']}|{message.from_user.id}"),)
            my_tasks_kb = types.InlineKeyboardMarkup(inline_keyboard=[my_tasks_btns])
            await message.answer("Выберите заявку из предложенного списка. \
Текст кнопки - номер заявки в КПО Кобра", reply_markup=my_tasks_kb)
        else:
            await message.answer("У вас нет заявок")        
    else:
        msg = "Запрос событий доступен только для зарегистрированных пользователей в приватном чате с ботом"
        await message.answer(msg)
        logger.warning(msg)
        return
    

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("task"))
async def task_actions(callback: types.CallbackQuery):
    params = callback.data.split("|")
    cobra_task_id = params[1]
    chat_id = params[2]
    my_actions_btns = [
         [
            types.InlineKeyboardButton(text="Просмотр заявки", callback_data=f"view_action|{cobra_task_id}|{chat_id}"),
            types.InlineKeyboardButton(text="Перенос заявки", callback_data=f"change_date_action|{cobra_task_id}|{chat_id}"),
         ],
         [
            types.InlineKeyboardButton(text="Закрыть заявку", callback_data=f"close_action|{cobra_task_id}|{chat_id}"),
         ]
    ]
    my_actions_kb = types.InlineKeyboardMarkup(inline_keyboard=my_actions_btns)
    await bot.send_message(chat_id, f"Вы выбрали задачу {cobra_task_id}. Выберите действие:", reply_markup=my_actions_kb)



@dp.callback_query_handler(lambda c: c.data and c.data.startswith("view_action"))
async def view_task_actions(callback: types.CallbackQuery):
    cobra_task_id, chat_id = get_task_action_params(callback.data)
    task = cobra_tasks.get_one_task(cobra_task_id)
    if len(task):
        report_message = CobraTaskReportMessage()
        report_message.add_task_to_report_message(task[0])
        report_message.add_generation_datetime()
        await bot.send_message(chat_id, report_message.get_report_message_text(), parse_mode='html')

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("change_date_action"))
async def change_task_date_actions(callback: types.CallbackQuery):
    cobra_task_id, chat_id = get_task_action_params(callback.data)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("close_action"))
async def close_task_action(callback: types.CallbackQuery):
    cobra_task_id, chat_id = get_task_action_params(callback.data)


def register_handlers_event(dp: Dispatcher):
    dp.register_message_handler(
        cmd_tasks_notifications,
        commands="tasks",
        state="*"
        )
    
    dp.register_message_handler(
        cmd_my_tasks_list,
        commands="my_tasks",
        state="*"
        )
