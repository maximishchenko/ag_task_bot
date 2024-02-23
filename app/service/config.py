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
    """ Имя параметра, хранящего адрес или FQDN-имя хоста для подключения к КПО Кобра """

    port_param = "port"
    """ Имя параметра, хранящего порт для подключения к КПО КОбра """

    token_param = "token"
    """ Имя параметра, хранящего пароль удаленного доступа pud для подключения к КПО Кобра """

    def get_host(self) -> str:
        """Возвращает адрес хоста или FQDN-имя сервера КПО Кобра"""
        return self.config.get(self.section, self.host_param)

    def get_port(self) -> str:
        """Возвращает порт для подключения к КПО Кобра"""
        return self.config.get(self.section, self.port_param)

    def get_token(self) -> str:
        """Возвращает пароль удаленного доступа pud для подключения к КПО Кобра"""
        return self.config.get(self.section, self.token_param)


class TelegramConfig(Config):
    """Получение параметров, отвечающих за взаимодействие с Telegram API"""

    section = "Telegram"
    """ Название секции файла конфигурации """

    token_param = "token"
    """ Имя параметра, хранящего данные токена бота """

    chat_id_param = "chat_id"
    """ Имя параметра, хранящего данные с ID чата в Telegram """

    debug_chat_id = "debug_chat_id"

    admin_chat_ids_param = 'admin_chat_ids'
    """ Имя параметра, хранящего данные ID чатов администраторов в Telegram """

    def get_token(self) -> str:
        """Возвращает токен бота Telegram"""
        return self.config.get(self.section, self.token_param)

    def get_chat_id(self) -> str:
        """Возвращает ID чата в Telegram для отправки уведомлений"""
        return self.config.get(self.section, self.chat_id_param)
    
    def get_debug_chat_id(self) -> str:
        return self.config.get(self.section, self.debug_chat_id_param)
    
    def get_admin_chat_ids(self) -> tuple:
        """ Возвращает ID чатов администраторов бота в Telegram

        Returns:
            tuple: кортеж, содержащий ID чатов администраторов в Telegram
        """
        admin_chat_ids = self.config.get(self.section, self.admin_chat_ids_param)
        admin_chat_ids_list = admin_chat_ids.split(",")
        return tuple(admin_chat_ids_list)