from abc import ABC
import configparser


class Config(ABC):
    """Базовый класс для реализации методов получения параметров"""

    default_encoding = "utf-8"
    """ Кодировка файла конфигурации """

    def __init__(self, config_file_path: str = "config/config.ini") -> None:
        self.config = configparser.ConfigParser()
        self.config.read(config_file_path, encoding=self.default_encoding)


class CobraConfig(Config):
    """Получение параметров, отвечающих за подключение к КПО Кобра"""

    section = "Cobra"
    """ Название секции файла конфигурации """

    host_param = "host"
    """ Имя параметра, хранящего адрес или FQDN-имя хоста для подключения к КПО
      Кобра """

    port_param = "port"
    """ Имя параметра, хранящего порт для подключения к КПО КОбра """

    token_param = "token"
    """ Имя параметра, хранящего пароль удаленного доступа pud для подключения
    к КПО Кобра """

    def get_host(self) -> str:
        """Возвращает адрес хоста или FQDN-имя сервера КПО Кобра"""
        return self.config.get(self.section, self.host_param)

    def get_port(self) -> str:
        """Возвращает порт для подключения к КПО Кобра"""
        return self.config.get(self.section, self.port_param)

    def get_token(self) -> str:
        """Возвращает пароль удаленного доступа pud для подключения к
        КПО Кобра"""
        return self.config.get(self.section, self.token_param)


class TelegramConfig(Config):
    """Получение параметров, отвечающих за взаимодействие с Telegram API"""

    section = "Telegram"
    """ Название секции файла конфигурации """

    token_param = "token"
    """ Имя параметра, хранящего данные токена бота """

    task_full_report_chat_ids = "task_full_report_chat_ids"
    """ Имя параметра, хранящего данные с ID чата в Telegram """

    admin_chat_ids_param = "admin_chat_ids"
    """ Имя параметра, хранящего данные ID чатов администраторов в Telegram """

    task_full_report_time = "task_full_report_time"
    """ Имя параметра, хранящего время запуска генерации отчета для отправки
    в группу """

    task_personal_report_time = "task_personal_report_time"
    """ Имя параметра, хранящего время запуска генерации отчета для отправки
    перснальных уведомлений """

    def get_token(self) -> str:
        """Возвращает токен бота Telegram"""
        return self.config.get(self.section, self.token_param)

    def get_task_full_report_chat_ids(self) -> tuple:
        """Возвращает ID чата в Telegram для отправки уведомлений"""
        task_chat_ids = self.task_full_report_chat_ids
        chat_ids = self.config.get(self.section, task_chat_ids)
        return tuple(chat_ids.split(","))

    def get_task_full_report_shedule_time(self) -> tuple:
        """Возвращает время запуска генерации отчета для отправки в группу"""
        sch_time = self.config.get(self.section, self.task_full_report_time)
        return tuple(sch_time.split(":"))

    def get_task_personal_report_shedule_time(self) -> tuple:
        """Возвращает время запуска генерации отчета для отправки персональных
        уведомлений"""
        report_time = self.task_personal_report_time
        sch_time = self.config.get(self.section, report_time)
        return tuple(sch_time.split(":"))

    def get_admin_chat_ids(self) -> tuple:
        """Возвращает ID чатов администраторов бота в Telegram

        Returns:
            tuple: кортеж, содержащий ID чатов администраторов в Telegram
        """
        chat_ids = self.config.get(self.section, self.admin_chat_ids_param)
        admin_chat_ids_list = chat_ids.split(",")
        return tuple(admin_chat_ids_list)
