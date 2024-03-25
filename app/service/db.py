"""Содержит логику взаимодействия с БД.

Набор объектов передачи данных и классов для взаимодействия с БД.
"""

# Standard Library
import sqlite3
from dataclasses import dataclass


@dataclass
class CobraOneLkUser:
    """Объект передачи данных.

    Содержит данные таблица lkuser КПО Кобра
    """

    n_abs: int
    name: str
    status: int
    password: str | None = None


@dataclass
class OneUser:
    """Объект передачи данных.

    Содержит данные таблицы в БД user.
    """

    chat_id: int
    first_name: str
    last_name: str | None
    username: str | None
    status: int = 0
    tehn: str | None = None


@dataclass
class MobileAppAccount:
    """Объект передачи данных.

    Используется для передачи авторизации приложения МТ из КПО Кобра.
    """

    username: str
    password: str


class DB:
    """Базовый класс для работы с БД."""

    def __init__(self, db_file) -> None:  # noqa D107
        self._connection = sqlite3.connect(db_file)
        self._cursor = self._connection.cursor()


class User(DB):
    """Взаимодействие с поьлзователями в БД."""

    def add_user(self, user: OneUser):
        """Добавляет пользователя в БД.

        Args:
            user (OneUser): DTO с данными пользователя
        """
        with self._connection:
            params = (
                user.chat_id,
                user.first_name,
                user.last_name,
                user.username,
                user.status,
                user.tehn,
            )
            query_str = "INSERT INTO `user` \
(`chat_id`, `first_name`, `last_name`, `username`, `status`, `tehn`) VALUES \
(?, ?, ?, ?, ?, ?)"
            return self._cursor.execute(query_str, params)

    def get_user(self, chat_id: int) -> OneUser | None:
        """Возвращает данные техника по Telegram chat id.

        Args:
            chat_id (int): Telegram Chat ID

        Returns:
            OneUser|None: DTO с данными пользователя
        """
        with self._connection:
            params = (chat_id,)
            query_str = "SELECT * FROM `user` WHERE `chat_id` = ? "
            result = self._cursor.execute(query_str, params).fetchall()
            if len(result):
                user = OneUser(
                    chat_id=result[0][1],
                    first_name=result[0][2],
                    last_name=result[0][3],
                    username=result[0][4],
                    status=result[0][5],
                    tehn=result[0][6],
                )
                return user
            return None

    def get_user_by_tehn(self, tehn: str) -> OneUser | None:
        """Возвращает данные техника по имени пользователя МТ.

        Сверяет имя пользователя приложения Мобильный Техник КПО Кобра
        с данными, сохраненными в БД и возвращает данные техника при наличии.

        Args:
            tehn (str): Имя техника в приложении МТ.

        Returns:
            OneUser|None: DTO с данными пользователя или None.
        """
        with self._connection:
            params = (tehn,)
            query_str = "SELECT * FROM `user` WHERE `tehn` = ? "
            result = self._cursor.execute(query_str, params).fetchall()
            if len(result):
                return OneUser(
                    chat_id=result[0][1],
                    first_name=result[0][2],
                    last_name=result[0][3],
                    username=result[0][4],
                    status=result[0][5],
                    tehn=result[0][6],
                )
            return None

    def is_user_exists(self, chat_id: int) -> bool:
        """Проверяет существование пользователя.

        Проверка производится по chat_id в Telegram.

        Args:
            chat_id (int): Telegram chat_id

        Returns:
            bool: результат проверки (True/False)
        """
        result = self.get_user(chat_id)
        return True if result else False

    def change_status(self, user: OneUser) -> None:
        """Смена статуса пользователя.

        Args:
            user (OneUser): объект передачи данных, содержащий данные одного
            пользователя
        """
        with self._connection:
            params = (user.status, user.chat_id)
            query_str = "UPDATE `user` SET `status` = ? WHERE `chat_id` = ?"
            self._cursor.execute(query_str, params)
