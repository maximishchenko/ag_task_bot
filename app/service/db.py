import sqlite3


class DB:

    def __init__(self, db_file) -> None:
        self._connection = sqlite3.connect(db_file)
        self._cursor = self._connection.cursor()


class User(DB):
    
    def add_user(self, chat_id: int, first_name: str, last_name: str = None, username: str = None, status: int = 0):
        with self._connection:
            return self._cursor.execute("INSERT INTO `user` (`chat_id`, `first_name`, `last_name`, `username`, `status`) VALUES (?, ?, ?, ?, ?)", (chat_id, first_name, last_name, username, status))

    def is_user_exists(self, chat_id: int):
        with self._connection:
            result = self._cursor.execute("SELECT * FROM `user` WHERE `chat_id` = ? ", (chat_id, )).fetchall()
            return bool(len(result))
        
    def change_status(self, chat_id: int, status: int):
        with self._connection:
            return self._cursor.execute("UPDATE `user` SET `status` = ? WHERE `chat_id` = ?", (status, chat_id))
        

class CobraLkUser(DB):

    def add_user(self, name: str, n_abs: int) -> None:
        with self._connection:
            return self._cursor.execute("INSERT INTO `cobra_lkuser` (`name`, `n_abs`) VALUES (?, ?)", (name, n_abs))

    def delete_user(self, n_abs: int) -> None:
        with self._connection:
            return self._cursor.execute("DELETE FROM `cobra_lkuser` WHERE `n_abs` = ?", (n_abs))

    def is_user_exists(self, name: str, n_abs: int) -> bool:
        with self._connection:
            result = self._cursor.execute("SELECT * FROM `cobra_lkuser` WHERE `name` = ? AND `n_abs` = ? ", (name, n_abs, )).fetchall()
            return bool(len(result))

    def get_users(self) -> tuple:
        with self._connection:
            result = self._cursor.execute("SELECT * FROM `cobra_lkuser`").fetchall()
            return result