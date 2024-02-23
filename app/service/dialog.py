
from aiogram.dispatcher.filters.state import (
    State, 
    StatesGroup
)

class Signup(StatesGroup):

    wating_username = State()
    waiting_password = State()

    username_param = 'username'
    password_param = 'password'