from abc import ABC
from datetime import datetime
from app.service.config import CobraConfig
import requests
import urllib.request, urllib.parse



# Заявки
# № заявки n_abs
# дата поступления timez
# наименование объекта nameobj
# номер объекта numobj
# адрес объекта addrobj
# техник tehn
# назначенное время timev


class CobraTaskReportHeader:
    """Объект передачи данных, содержащий соответствие названий заголовков
    таблицы полям, возвращаемым REST API КПО Кобра"""

    n_abs = "№ заявки"
    zay = "Дефект"
    timez = "Дата поступления"
    prin = "Заявку принял"
    # account_number = "Пультовый номер"
    nameobj = "Наименование объекта"
    numobj = "Пультовой номер"
    addrobj = "Адрес объекта"
    tehn = "Техник"
    timev = "Назначенное время"



class CobraTable(ABC):
    """Базовый класс для получения данных из таблиц КПО Кобра"""

    endpoint_root = "api.table.get"
    """ Метод для получения данных таблиц """

    token_key = "pud"
    """ Наименование параметра, в котором передается пароль удаленного доступа """

    def __init__(self, config: CobraConfig) -> None:
        self._host = config.get_host()
        self._port = config.get_port()
        self._token = config.get_token()
        self._endpoint_url = self._get_endpoint_url()

    def _get_endpoint_url(self) -> str:
        """Генерирует полный url для отправки http-запроса"""
        endpoint = f"{self._host}:{self._port}/{self.endpoint_root}"
        token = urllib.parse.urlencode({self.token_key: self._token})
        return f"{endpoint}?{token}"


class CobraTaskReport(CobraTable):
    """Реализует запрос к REST API КПО Кобра, формирует параметры запроса
    (фильтр, набор возвращаемых полей)

    TODO генерировать набор возвращаемых полей из объекта передачи данных,
    хранящего названия заголовков таблицы отчета
    """

    name_template = "***"
    """ Шаблон наименования заявки. В отчет попадают только заявки, формируемые
    оперативным дежурным начинаются с *** """

    table_name = "zayavki"
    """ Название таблицы, хранящей данные заявок """

    def get_tasks(self) -> tuple:
        """Получает заявки из КПО Кобра"""
        response = self._get_unfinished_tasks()
        # return tuple(response)
        tasks_list = []
        current_date = datetime.today().date()
        for task in response:
            timev = datetime.strptime(task['timev'], "%d.%m.%Y %H:%M:%S").date()
            if current_date >= timev:
                print(task)
                tasks_list.append[task]
        return tuple(tasks_list)

    def _get_unfinished_tasks(self):
        """Запрос текущих заявок из КПО Кобра"""
        url = f"{self._endpoint_url}"
        params = {
            "name": self.table_name,
            "filter": self._get_filter(),
            "fields": self._get_fields(),
        }
        response = requests.get(url=url, params=params).json()
        result = sorted(response["result"], key=lambda task: task["tehn"])
        return result

    def _get_filter(self):
        """Установка фильтра при запросе заявок из КПО Кобра"""
        filter_value = '[{"zay": "' + self.name_template + '"}]'
        return f"{filter_value}"

    def _get_fields(self):
        """Запрос полей из таблицы КПО Кобра, соответствующих
        формату генерируемого отчета"""
        fields_value = '[{"n_abs": "1"}, {"zay": "1"}, {"prin": "1"}, {"timez": "1"}, {"nameobj": "1"}, {"numobj": "1"}, {"addrobj": "1"}, {"tehn": "1"}, {"timev": "1"}]'
        return f"{fields_value}"


class CobraTaskReportMessage:
    """Генерация текста сообщения отчета на основании данных
    заявки из КПО Кобра"""

    message: str = str()
    """ Пустая строка сообщения """

    def add_report_header(self) -> None:
        """Добавляет заголовок к сообщению отчета"""
        current_date = datetime.today().strftime("%d.%m.%Y")
        self.message += f"<b>Оперативные Заявки {current_date}</b>"
        self.add_empty_string_to_report_message()
        self.add_empty_string_to_report_message()

    def add_tehn_to_report_message(self, tehn: str) -> None:
        """Добавление имени техника в сообщение отчета

        Args:
            tehn (str): Ф.И.О. техника, закрепленного за заявкой из КПО Кобра
        """
        self.message += f"<b>{str(tehn)}</b>"
        self.add_empty_string_to_report_message()

    def add_task_to_report_message(self, task: dict) -> None:
        """Добавление данных одной заявки, полученной из КПО Кобра,
        в строку сообщения отчета

        Args:
            task (dict): словарь содержащий данные одной заявки, полученный из
            КПО Кобра
        """
        task_string = f"{task['n_abs']}\r\n{task['numobj']} {task['nameobj']} {task['addrobj']}\r\n<code>{task['zay']}</code>"
        self.message += str(task_string)
        self.add_empty_string_to_report_message()
        self.message += f"<ins>Заявку принял: {task['prin']} {task['timez']}</ins>"
        self.add_empty_string_to_report_message()

    def add_empty_string_to_report_message(self) -> None:
        """Добавляет пустую строку в текст сообщения отчета"""
        self.message += "\r\n"

    def add_generation_datetime(self) -> None:
        self.add_empty_string_to_report_message()
        current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.message += f"<ins>Дата формирования отчета: {current_datetime}</ins>"

    def get_report_message_text(self) -> str:
        """Возвращает сгенерированную строку сообщения отчета

        Returns:
            str: строка сообщения отчета
        """
        return self.message