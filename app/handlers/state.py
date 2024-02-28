"""
Скрипт организует хранение логики состояний диалога.

Хранит базовые объекты, отвечающие за идентификацию стадии диалога.
"""

from aiogram.dispatcher.filters.state import State, StatesGroup


class Signup(StatesGroup):
    """
    Набор состояний для реализации диалога при выполнении команды /signup.

    Args:
        StatesGroup (_type_): Состояние диалога
    """

    wating_username = State()
    waiting_password = State()

    username_param = "username"
    password_param = "password"


class MyTask(StatesGroup):
    """
    Набор состояний для реализации диалога при обработке собственных задач.

    Args:
        StatesGroup (_type_): Состояние диалога
    """

    waiting_input_date = State()
    waiting_input_time = State()

    task_id_param = "task_id"
    task_new_date_param = "task_date"
    task_new_time_param = "task_time"

    tasks_for_user_accept_param = "tasks_for_accept"
