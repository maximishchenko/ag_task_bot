import sqlite3
from dataclasses import dataclass
from typing import Union
        

@dataclass
class CobraOneLkUser:
    n_abs: int
    name: str
    status: int
    password: str = None


@dataclass
class OneUser:
    chat_id: int
    first_name: str
    last_name: str|None
    username: str|None
    status: int = 0
    tehn: str = None


@dataclass
class MobileAppAccount:
    username: str
    password: str


class DB:

    def __init__(self, db_file) -> None:
        self._connection = sqlite3.connect(db_file)
        self._cursor = self._connection.cursor()


class User(DB):
    
    def add_user(self, user: OneUser):
        with self._connection:
            params = (user.chat_id, user.first_name, user.last_name, user.username, user.status, user.tehn)
            query_str = "INSERT INTO `user` (`chat_id`, `first_name`, `last_name`, `username`, `status`, `tehn`) VALUES (?, ?, ?, ?, ?, ?)"
            return self._cursor.execute(query_str, params)
        
    def get_user(self, chat_id: int) -> OneUser:
        with self._connection:
            params = (chat_id, )
            query_str = "SELECT * FROM `user` WHERE `chat_id` = ? "
            result = self._cursor.execute(query_str, params).fetchall()
            if len(result):
                user = OneUser(chat_id=result[0][1], first_name=result[0][2], last_name=result[0][3], username=result[0][4], status=result[0][5], tehn=result[0][6])
                return user
            return None
        
    def get_user_by_tehn(self, tehn: str):
        with self._connection:
            params = (tehn, )
            query_str = "SELECT * FROM `user` WHERE `tehn` = ? "
            result = self._cursor.execute(query_str, params).fetchall()
            if len(result):
                return OneUser(chat_id=result[0][1], first_name=result[0][2], last_name=result[0][3], username=result[0][4], status=result[0][5], tehn=result[0][6])
            return None

    def is_user_exists(self, chat_id: int):
        result = self.get_user(chat_id)
        return True if result else False
        
    def change_status(self, user: OneUser):
        with self._connection:
            params = (user.status, user.chat_id)
            query_str = "UPDATE `user` SET `status` = ? WHERE `chat_id` = ?"
            return self._cursor.execute(query_str, params)