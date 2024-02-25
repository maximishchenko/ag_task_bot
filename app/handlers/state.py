
from aiogram.dispatcher.filters.state import (
    State, 
    StatesGroup
)

class Signup(StatesGroup):

    wating_username = State()
    waiting_password = State()

    username_param = 'username'
    password_param = 'password'


class MyTask(StatesGroup):

    waiting_input_date = State()
    waiting_input_time = State()