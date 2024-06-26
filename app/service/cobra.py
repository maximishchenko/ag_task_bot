"""Логика взаимодействия с КПО Кобра.

Содержит логику API-запростов к REST API КПО Кобра.
"""

# Standard Library
import urllib.parse
import urllib.request
from abc import ABC
from datetime import datetime

import requests

from app.service.config import CobraConfig
from app.service.db import CobraOneLkUser, MobileAppAccount


class TaskReportHeader:
    """Объект передачи данных, содержащий соответствие названий заголовков.

    таблицы полям, возвращаемым REST API КПО Кобра.
    """

    n_abs = "№ заявки"
    zay = "Дефект"
    timez = "Дата поступления"
    prin = "Заявку принял"
    nameobj = "Наименование объекта"
    numobj = "Пультовой номер"
    addrobj = "Адрес объекта"
    tehn = "Техник"
    timev = "Назначенное время"


class CobraTable(ABC):
    """Базовый класс для получения данных из таблиц КПО Кобра."""

    """ Метод для получения данных таблиц """
    endpoint_root = "api.table.get"

    """ Наименование параметра, в котором передается пароль
    удаленного доступа """
    token_key = "pud"

    def __init__(self, config: CobraConfig) -> None:  # noqa D107
        self._host = config.get_host()
        self._port = config.get_port()
        self._token = config.get_token()
        self._endpoint_url = self._get_endpoint_url()

    def _get_endpoint_url(self) -> str:
        """Генерирует полный url для отправки http-запроса."""
        endpoint = f"{self._host}:{self._port}/{self.endpoint_root}"
        token = urllib.parse.urlencode({self.token_key: self._token})
        return f"{endpoint}?{token}"


class CobraTaskReport(CobraTable):
    """Реализует запрос к REST API КПО Кобра, формирует параметры запроса.

    Фильтр, набор возвращаемых полей
    """

    name_template = "***"
    """ Шаблон наименования заявки. В отчет попадают только заявки, формируемые
    оперативным дежурным начинаются с *** """

    table_name = "zayavki"
    """ Название таблицы, хранящей данные заявок """

    def get_tasks(self) -> tuple:
        """Получает заявки из КПО Кобра."""
        response = self._get_unfinished_tasks()
        tasks_list = list()
        current_date = datetime.today().date()
        for task in response:
            timev = datetime.strptime(task["timev"], "%d.%m.%Y %H:%M:%S")
            if current_date >= timev.date() and task["sttech"] != 3:
                tasks_list.append(task)
        return tuple(tasks_list)

    def get_my_tasks(self, name: str) -> tuple:
        """Возвращает заявки техника по его имени из МТ.

        Args:
            name (str): имя техника из приложения МТ КПО Кобра.

        Returns:
            tuple: кортеж, содержащий данные заявок.
        """
        response = self._get_unfinished_tasks()
        tasks_list = []
        for task in response:
            if task["tehn"] == name and task["sttech"] != 3:
                tasks_list.append(task)
        return tuple(tasks_list)

    def get_one_task(self, n_abs: str) -> tuple:
        """Получение данных одной заявки по ее абсолютному номеру.

        Args:
            n_abs (str): абсолютный номер заявки. Используется str, т.к.
            в этом формате возвращается от REST API КПО Кобра.

        Returns:
            tuple: данные одной заявки.
        """
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "filter": '[{"n_abs": "' + n_abs + '"}]',
        }
        response = requests.get(url=url, params=params).json()
        return (response["result"][0],)

    def _get_unfinished_tasks(self):
        """Запрос текущих заявок из КПО Кобра."""
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "filter": self._get_filter(),
        }
        response = requests.get(url=url, params=params).json()
        result = sorted(response["result"], key=lambda task: task["tehn"])
        return result

    def _get_filter(self):
        """Установка фильтра при запросе заявок из КПО Кобра."""
        filter_value = '[{"zay": "' + self.name_template + '"}]'
        return f"{filter_value}"

    def _get_fields(self):
        """Запрос полей из таблицы КПО Кобра.

        Запрашиваются только поля, соответствующие формату отчета.
        """
        fields_value = '[{"n_abs": "1"}, {"zay": "1"}, {"prin": "1"}, \
{"timez": "1"}, {"nameobj": "1"}, {"numobj": "1"}, {"addrobj": "1"}, \
{"tehn": "1"}, {"timev": "1"}, {"who": 1}, {"sttech": 1}]'
        return f"{fields_value}"


class CobraTaskEdit(CobraTaskReport):
    """Реализует модификацию данных в таблице заявок."""

    endpoint_root = "api.table.edit"
    """ Метод для редактирования данных таблиц """

    def update_one_task_time(self, n_abs: int, event_time: str) -> None:
        """Редактирует время исполнения одной заявки.

        Args:
            n_abs (int): абсолютный номер заявки
            event_time (str): время исполнения
        """
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "n_abs": n_abs,
            "fields": '[{"timev":"' + event_time + '"}]',
        }
        requests.get(url=url, params=params).json()

    def accept_one_task(self, n_abs: int) -> None:
        """Устанавливает метку принятия заявки.

        Args:
            n_abs (int): абсолютный номер заявки
        """
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "n_abs": n_abs,
            "fields": '[{"sttech": "1"}]',
        }
        requests.get(url=url, params=params).json()
        self._set_task_accept_time(n_abs)

    def finish_one_task(self, n_abs: int) -> None:
        """Завершает одну заявку.

        Args:
            n_abs (int): абсолютный номер заявки в КПО Кобра.
        """
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "n_abs": n_abs,
            "fields": '[{"sttech": "3"}]',
        }
        requests.get(url=url, params=params).json()

    def add_finish_task_reason(self, n_abs: int, reason: str) -> None:
        """Записывает результат выполнения заявки.

        Args:
            n_abs (int): абсолютный номер заявки.
            reason (str): текст описания результата завершения заявки.
        """
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "n_abs": n_abs,
            "fields": '[{"rez":"' + reason + '"}]',
        }
        requests.get(url=url, params=params).json()

    def _set_task_accept_time(self, n_abs: int) -> None:
        """Указывыает время принятия заявки.

        Args:
            n_abs (int): абсолютный номер заявки
        """
        current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "n_abs": n_abs,
            "fields": '[{"timer":"' + current_datetime + '"}]',
        }
        requests.get(url=url, params=params).json()


class CobraTaskDelete(CobraTaskReport):
    """Реализует удаления данных в таблице заявок."""

    endpoint_root = "api.table.delete"

    def delete_one_task(self, n_abs: int) -> None:
        """Удаление одной заявки.

        Реализует метод REST API КПО Кобра для удаления одной заявки.

        Args:
            n_abs (int): абсолютный номер заявки
        """
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "n_abs": n_abs,
        }
        requests.get(url=url, params=params).json()


class CobraTaskReportMessage:
    """Генерация текста сообщения отчета.

    Текст отчета генерируется на основании данных
    заявки из КПО Кобра
    """

    message: str = str()
    """ Пустая строка сообщения """

    def add_report_header(self) -> None:
        """Добавляет заголовок к сообщению отчета."""
        current_date = datetime.today().strftime("%d.%m.%Y")
        self.message += f"<b>Аварийные Заявки {current_date}</b>"
        self.add_empty_string_to_report_message()
        self.add_empty_string_to_report_message()

    def add_tehn_to_report_message(self, tehn: str) -> None:
        """Добавление имени техника в сообщение отчета.

        Args:
            tehn (str): Ф.И.О. техника, закрепленного за заявкой из КПО Кобра
        """
        self.message += f"<b>{str(tehn)}</b>"
        self.add_empty_string_to_report_message()

    def add_task_to_report_message(self, task: dict) -> None:
        """Добавление одной заявки из КПО Кобра в строку сообщения отчета.

        Args:
            task (dict): словарь содержащий данные одной заявки, полученный из
            КПО Кобра
        """
        task_string = f"{task['numobj']}\r\n{task['nameobj']} \
{task['addrobj']}\r\n<code>{task['zay']}</code>"
        self.message += str(task_string)
        self.add_empty_string_to_report_message()
        self.message += f"<ins>Заявку подал: {task['who']} \
({task['prin']})</ins>"
        self.add_empty_string_to_report_message()
        self.message += f"<ins>Дата поступления: {task['timez']}</ins>"
        self.add_empty_string_to_report_message()

    def add_empty_string_to_report_message(self) -> None:
        """Добавляет пустую строку в текст сообщения отчета."""
        self.message += "\r\n"

    def add_generation_datetime(self) -> None:
        """Добавляет дату/время генерации отчета к сообщению Telegram."""
        self.add_empty_string_to_report_message()
        current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.message += f"<ins>Дата формирования отчета: \
{current_datetime}</ins>"

    def get_report_message_text(self) -> str:
        """Возвращает сгенерированную строку сообщения отчета.

        Returns:
            str: строка сообщения отчета
        """
        return self.message


class CobraTehn(CobraTable):
    """Взаимодействие с таблицей lkuser КПО Кобра.

    Используются запросы REST API к таблице КПО Кобра lkuser, содержащую
    данные зарегистрированных техников.
    """

    table_name = "lkuser"
    """ Название таблицы, хранящей данные техников """

    def is_account_valid(self, account: MobileAppAccount) -> bool:
        """Валидация аккаунта приложения МТ в КПО Кобра.

        Args:
            account (MobileAppAccount): данные аккаунта приложения МТ.

        Returns:
            bool: результат проверки.
        """
        lk_users = self._get_tehn_list()
        for tehn in lk_users:
            lk_user = CobraOneLkUser(
                n_abs=tehn["n_abs"],
                name=tehn["fio"],
                status=tehn["status"],
                password=tehn["pass"],
            )
            user = account.username
            pwd = account.password
            if user == lk_user.name and pwd == lk_user.password:
                return True
        return False

    def _get_tehn_list(self):
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "fields": self._get_fields(),
        }
        response = requests.get(url=url, params=params).json()
        result = sorted(response["result"], key=lambda task: task["fio"])
        return result

    def _get_fields(self) -> str:
        fields_value = '[{"fio": 1}, {"n_abs": 1}, {"status": 1}, {"pass": 1}]'
        return f"{fields_value}"
