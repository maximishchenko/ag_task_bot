"""
Обработчики событий диалога с ботом.

Взаимодействие с модулями КПО Кобра.
"""

# Standard Library
from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram_datepicker import Datepicker, DatepickerSettings
from aiogram_timepicker.panel import FullTimePicker, full_timep_callback

from app.bot_global import bot, cobra_config, cobra_tasks, dp, logger, tg_config, user
from app.handlers.state import CloseMyTaskDialog, MyTask, TaskParam
from app.service.cobra import CobraTaskEdit, CobraTaskReportMessage
from tasks_notify import send_all_tasks, send_personal_tasks


def is_group_or_supergroup(message: types.Message) -> bool:
    """
    Проверяет пришло ли полученное сообщение в группу или супергруппу.

    Args:
        message (types.Message): полученное сообщение

    Returns:
        bool: резуальтат проверки
    """
    type = message.chat.type
    return type == types.ChatType.GROUP or type == types.ChatType.SUPERGROUP


def is_private_chat(message: types.Message) -> bool:
    """
    Проверяет пришло ли полученное сообщение в приватный чат.

    Args:
        message (types.Message): полученное сообщение

    Returns:
        bool: результат проверки
    """
    return message.chat.type == types.ChatType.PRIVATE and user.get_user(
        message.from_user.id
    )


def get_task_action_params(data: str) -> tuple:
    """
    Возвращает параметры функции обратного вызова для обработки заявки.

    Разбирает строку передаваемую функции обратного вызова, через
    InlineKeyboard. Возвращает параметры

    Args:
        data (str): строка, содержащая данные параметров для функции обратного
        вызова

    Returns:
        tuple: набор параметров
    """
    params = data.split("|")
    cobra_task_id = params[1]
    chat_id = params[2]
    return cobra_task_id, chat_id


def get_datepicker_settings() -> DatepickerSettings:
    """
    Возвращает настройки виджета календаря.

    Returns:
        DatepickerSettings: Параметры виджета календаря.
    """
    return DatepickerSettings(
        initial_view="day",  # available views -> day, month, year
        initial_date=datetime.now().date(),  # default date
        views={
            "day": {
                "show_weekdays": True,
                "weekdays_labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
                "header": ["prev-year", "days-title", "next-year"],
                "footer": [
                    "prev-month",
                    "select",
                    "next-month",
                ],
            },
            "month": {
                "months_labels": [
                    "Янв",
                    "Фев",
                    "Март",
                    "Апр",
                    "Май",
                    "Июнь",
                    "Июль",
                    "Авг",
                    "Сен",
                    "Окт",
                    "Ноя",
                    "Дек",
                ],
                "header": [
                    "prev-year",
                    ["year", "select"],
                    "next-year",
                ],
                "footer": ["select"],
            },
            "year": {
                "header": [],
                "footer": ["prev-years", "next-years"],
            },
        },
        labels={
            "prev-year": "<<",
            "next-year": ">>",
            "prev-years": "<<",
            "next-years": ">>",
            "days-title": "{month} {year}",
            "selected-day": "{day} *",
            "selected-month": "{month} *",
            "present-day": "• {day} •",
            "prev-month": "<",
            "select": "Выбрать",
            "next-month": ">",
            "ignore": "",
        },
        custom_actions=[],  # some custom actions
    )


def get_close_task_buttons() -> types.InlineKeyboardMarkup:
    """Возвращает доступные действия для подтверждения закрытия задачи.

    Кнопки: подтверждение, корректировка отмена.

    Returns:
        types.InlineKeyboardMarkup: inline-keyboard-markup
    """
    my_actions_btns = [
        [
            types.InlineKeyboardButton(
                text="Подтвердить",
                callback_data="closing_act_accept",
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Корректировать текст результата",
                callback_data="closing_act_edit",
            ),
        ],
        [
            types.InlineKeyboardButton(
                text="Отмена",
                callback_data="closing_act_cancel",
            ),
        ],
    ]
    my_actions_kb = types.InlineKeyboardMarkup(inline_keyboard=my_actions_btns)
    return my_actions_kb


async def cmd_tasks_notify(message: types.Message, state: FSMContext):
    """
    Генерация списка оперативных заявоук в зависимости от типа чата.

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
        if str(message.from_user.id) not in tg_config.get_admin_chat_ids():
            await message.answer(
                "Вы не имеете права выполнять запрошенную \
команду в группе. Если вам нужна персональная статистика - перейдите в \
личный чат с ботом"
            )
            return
        await message.answer(pre_msg)
        await send_all_tasks()
    else:
        logger.warning(
            "Генерация отчета запрошена пользователем, \
не состоящим в группе и не прошедшим регистрацию"
        )


async def cmd_my_tasks(message: types.Message, state: FSMContext):
    """
    Получение списка заявок текущего зарегистрированного пользователя.

    Args:
        message (types.Message): сообщение Telegram
        state (FSMContext): состояние диалога
    """
    await state.finish()
    if is_private_chat(message):
        my_user = user.get_user(message.chat.id)
        if not my_user or not my_user.tehn:
            await message.answer(
                "Вам не доступна возможность запроса списка \
персональных заявок, т.к. вы не зарегистрированы или отсутствует связь \
с техником КПО Кобра. Пройдите процедуру регистрации или обратитесь к \
администратору для проверки связи с техником КПО Кобра"
            )
            await state.finish()
            return
        my_tasks = cobra_tasks.get_my_tasks(my_user.tehn)
        btns = []
        if len(my_tasks):
            for task in my_tasks:
                callback_data = f"task|{task['n_abs']}|{message.from_user.id}"
                btns.append(
                    types.InlineKeyboardButton(
                        text=task["n_abs"],
                        callback_data=callback_data,
                    ),
                )
            my_tasks_kb = types.InlineKeyboardMarkup(inline_keyboard=[btns])
            await message.answer(
                "Выберите заявку из предложенного списка. \
Текст кнопки - номер заявки в КПО Кобра",
                reply_markup=my_tasks_kb,
            )
        else:
            await message.answer("У вас нет заявок")
    else:
        msg = "Запрос событий доступен только для зарегистрированных \
пользователей в личном чате с ботом"
        await message.answer(msg)
        logger.warning(msg)
        return


async def ask_before_close(message: types.Message, state: FSMContext) -> str:
    """Запрос причины закрытия заявки.

    Args:
        message (types.Message): полученное сообщение.
        state (FSMContext): текущее состояние диалога.

    Returns:
        str: текст сообщения
    """
    task_closing_reason = message.text
    async with state.proxy() as data:
        data[TaskParam.reason_for_close.value] = task_closing_reason
    return task_closing_reason


async def cmd_close_task(message: types.Message, state: FSMContext):
    """Принимает текст с результатом закрытия заявки.

    После ввода текста отправляет кнопки, позволяющие подтвердить закрытие
    заявки, скорректировать текст, или отменить закрытие.

    Args:
        message (types.Message): сообщение, с текстом результата закрытия заявки
        state (FSMContext): состояние диалога
    """
    task_param = await state.get_data()
    cobra_task_id = task_param[TaskParam.task_id.value]
    task_closing_reason = await ask_before_close(message, state)
    my_actions_kb = get_close_task_buttons()
    await message.answer(
        f"Заявка {cobra_task_id} будет закрыта. Причина: {task_closing_reason}.\
 Выберите действие:",
        reply_markup=my_actions_kb,
    )
    return


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("task"))
async def task_actions(callback: types.CallbackQuery):
    """
    Действие при выборе заявки.

    Генерация кнопок со списком доступных действий

    Args:
        callback (types.CallbackQuery): полученная функция обратного вызова
    """
    cobra_task_id, chat_id = get_task_action_params(callback.data)
    await bot.delete_message(
        chat_id=callback.from_user.id, message_id=callback.message.message_id
    )
    my_actions_btns = [
        [
            types.InlineKeyboardButton(
                text="Просмотр заявки",
                callback_data=f"view_act|{cobra_task_id}|{chat_id}",
            ),
            # types.InlineKeyboardButton(
            #     text="Перенос заявки",
            #     callback_data=f"change_act|{cobra_task_id}|{chat_id}",
            # ),
        ],
        [
            types.InlineKeyboardButton(
                text="Закрыть заявку",
                callback_data=f"close_action|{cobra_task_id}|{chat_id}",
            ),
        ],
    ]
    my_actions_kb = types.InlineKeyboardMarkup(inline_keyboard=my_actions_btns)
    await bot.send_message(
        chat_id,
        f"Вы выбрали задачу {cobra_task_id}. Выберите действие:",
        reply_markup=my_actions_kb,
    )


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("view_act"))
async def view_task_action(callback: types.CallbackQuery):
    """
    Просмотр заявки.

    Присылает ответное сообщение с детальным описанием заявки

    Args:
        callback (types.CallbackQuery): полученная функция обратного вызова
    """
    cobra_task_id, chat_id = get_task_action_params(callback.data)
    await bot.delete_message(
        chat_id=callback.from_user.id, message_id=callback.message.message_id
    )
    task = cobra_tasks.get_one_task(cobra_task_id)
    if len(task):
        report_message = CobraTaskReportMessage()
        report_message.add_task_to_report_message(task[0])
        report_message.add_generation_datetime()
        text = report_message.get_report_message_text()
        await bot.send_message(chat_id, text, parse_mode="html")


@dp.callback_query_handler(lambda c: c.data.startswith("change_act"))
async def change_date_action(callback: types.CallbackQuery, state: FSMContext):
    """
    Перенос даты заявки.

    Позволяет запустить процесс изменяющий дату исполнения заявки в КПО Кобра.

    Args:
        callback (types.CallbackQuery): полученная функция обратного вызова
    """
    cobra_task_id, chat_id = get_task_action_params(callback.data)
    await bot.delete_message(
        chat_id=callback.from_user.id, message_id=callback.message.message_id
    )
    datepicker = Datepicker(get_datepicker_settings())
    markup = datepicker.start_calendar()
    async with state.proxy() as data:
        data[MyTask.task_id_param] = cobra_task_id
    await callback.message.answer(
        "Выберите дату переноса заявки: ", reply_markup=markup
    )


@dp.callback_query_handler(Datepicker.datepicker_callback.filter())
async def process_datepicker(
    callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    """
    Обрабатывает выбор даты в календаре.

    Принимает данные (дата переноса заявки) от виджета DatePicker.
    Запрашивает время, на которое будет перенесена заявка.
    Направляет запрос в КПО Кобра

    Args:
        callback_query (types.CallbackQuery): _description_
        callback_data (dict): _description_
        state (FSMContext): _description_
    """
    datepicker = Datepicker(get_datepicker_settings())

    date = await datepicker.process(callback_query, callback_data)
    if date:
        async with state.proxy() as data:
            data[MyTask.task_new_date_param] = date.strftime("%d.%m.%Y")
        await bot.delete_message(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
        )

        await callback_query.message.answer(
            "Выберите время переноса заявки: ",
            reply_markup=await FullTimePicker().start_picker(),
        )
    await callback_query.answer()


@dp.callback_query_handler(full_timep_callback.filter())
async def process_full_timepicker(
    callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    """
    Обрабатывает данные, полученные от виджета TimePicker.

    Направляет информацию о дате переноса заявки в КПО Кобра.
    Устанавливает метку принятия заявки техником при необходимости

    Args:
        callback_query (types.CallbackQuery): _description_
        callback_data (dict): _description_
        state (FSMContext): _description_
    """
    r = await FullTimePicker().process_selection(callback_query, callback_data)
    if r.selected:
        task_new_param = await state.get_data()
        task_id = task_new_param[MyTask.task_id_param]
        task_time = r.time.strftime("%H:%M:%S")
        task_date = task_new_param[MyTask.task_new_date_param]
        async with state.proxy() as data:
            data[MyTask.task_new_time_param] = task_time

        task_modify = CobraTaskEdit(cobra_config)
        task_n_abs = task_new_param[MyTask.task_id_param]
        task_new_datetime = f"{task_date} {task_time}"
        task_modify.accept_one_task(task_n_abs)
        task_modify.update_one_task_time(task_n_abs, task_new_datetime)
        await callback_query.message.answer(
            f"Заявка №{task_id}. Перенесена на {task_date} {task_time}",
            # reply_markup=start_kb
        )
        await callback_query.message.delete_reply_markup()


@dp.callback_query_handler(lambda c: c.data.startswith("close_action"))
async def close_task_action(callback: types.CallbackQuery, state: FSMContext):
    """
    Закрытие заявки.

    Args:
        callback (types.CallbackQuery): полученная функция обратного вызова
    """
    cobra_task_id, chat_id = get_task_action_params(callback.data)
    await bot.delete_message(
        chat_id=callback.from_user.id, message_id=callback.message.message_id
    )
    async with state.proxy() as data:
        data[TaskParam.task_id.value] = cobra_task_id
    await callback.message.answer("Введите результат исполнения заявки:")
    await CloseMyTaskDialog.waiting_input_reason.set()
    return


@dp.callback_query_handler(
    lambda c: c.data == "closing_act_cancel",
    state=CloseMyTaskDialog.waiting_input_reason,
)
async def cancel_closing_task(callback: types.CallbackQuery, state: FSMContext):
    """Отмена действия закрытия заявки.

    Удаляет клавиатуру. Завершает диалог.
    Присылает уведомление ответным сообщением

    Args:
        callback (types.CallbackQuery): полученная функция обратного вызова
        state (FSMContext): состояние диалога
    """
    await bot.delete_message(
        chat_id=callback.from_user.id, message_id=callback.message.message_id
    )
    await callback.message.answer("Вы отменили закрытие заявки")
    await callback.answer("Закрытие заявки отменено техником")
    await state.finish()


@dp.callback_query_handler(
    lambda c: c.data == "closing_act_edit", state=CloseMyTaskDialog.waiting_input_reason
)
async def edit_closing_task_reason(callback: types.CallbackQuery):
    """Модифицирует текст результата завершения заявки.

    Args:
        callback (types.CallbackQuery): полученная функция обратного вызова
        state (FSMContext): текущее состояние диалога
    """
    await bot.delete_message(
        chat_id=callback.from_user.id, message_id=callback.message.message_id
    )
    await callback.message.answer("Введите результат исполнения заявки")


@dp.callback_query_handler(
    lambda c: c.data == "closing_act_accept",
    state=CloseMyTaskDialog.waiting_input_reason,
)
async def accept_closing_task(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение закрытия заявки.

    Завершает заявку. Отправляет уведомление пользователю. Отправляет
    уведомления в группу. Завершает состояние диалога

    Args:
        callback (types.CallbackQuery): полученная функция обратного вызова
        state (FSMContext): текущее состояние диалога
    """
    task_param = await state.get_data()
    cobra_task_id = task_param[TaskParam.task_id.value]
    task_closing_reason = task_param[TaskParam.reason_for_close.value]
    my_user = user.get_user(callback.message.chat.id)
    msg = f"Заявка {cobra_task_id} закрыта. Техник: {my_user.tehn} \
Результат: {task_closing_reason}"

    task_modify = CobraTaskEdit(cobra_config)
    task_modify.finish_one_task(cobra_task_id)
    task_modify.add_finish_task_reason(cobra_task_id, task_closing_reason)

    await state.finish()
    await callback.message.answer(msg)
    await callback.answer("Заявка закрыта")
    for chat in tg_config.get_task_full_report_chat_ids():
        await bot.send_message(
            chat,
            msg,
        )


@dp.callback_query_handler(lambda c: c.data.startswith("accept_action"))
async def accept_tasks(callback: types.CallbackQuery):
    """Установка признака принятия заявки техником.

    Удаляет клавиатуру для избежания повторного нажатия. Запрашивает список
    заявок текущего техника. Устанавливает метку "Принято". Задает дату/время
    принятия заявки. Направляет уведомление в группу

    Args:
        callback (types.CallbackQuery): полученная функция обратного вызова
    """
    await bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    params = callback.data.split("|")
    tehn = params[1]
    my_tasks = cobra_tasks.get_my_tasks(tehn)
    current_date = datetime.today().strftime("%d.%m.%Y")
    current_datetime = datetime.today().strftime("%d.%m.%Y %H:%M:%S")
    msg = f"{tehn} с соcтавом аварийных заявок на {current_date} \
ознакомлен"

    for task in my_tasks:
        task_modify = CobraTaskEdit(cobra_config)
        task_modify.accept_one_task(task["n_abs"])
        task_modify.update_one_task_time(task["n_abs"], current_datetime)

    for chat in tg_config.get_task_full_report_chat_ids():
        await bot.send_message(
            chat,
            msg,
        )


def register_handlers_event(dp: Dispatcher):
    """
    Регистрация обработчиков событий модуля.

    Args:
        dp (Dispatcher): обработчик событий
    """
    dp.register_message_handler(cmd_tasks_notify, commands="tasks", state="*")
    dp.register_message_handler(cmd_my_tasks, commands="my_tasks", state="*")
    dp.register_message_handler(
        cmd_close_task, state=CloseMyTaskDialog.waiting_input_reason
    )
