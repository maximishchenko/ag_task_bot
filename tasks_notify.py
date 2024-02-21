import requests
from app.service.config import CobraConfig, TelegramConfig
from app.service.cobra import CobraTaskReport, CobraTaskReportMessage
from app.service.report import CobraTaskExcelReport
import logging
import shutil
from itertools import groupby

PYTHONDONTWRITEBYTECODE=1

logger = logging.getLogger(__name__)

# TODO Отказаться от класса Telegram в пользу встроенных методов aiogram

class Telegram:
    """Отправка информации в Telegram"""

    base_url = "https://api.telegram.org/bot"
    """ Базовый URL Telegram Bot API для направления запросов """

    text_message_endpoint = "/sendMessage"
    """ Метод REST API Telegram Bot API для отправки текстовых сообщений """

    document_attachment_endpoint = "/sendDocument"
    """ Метод REST API Telegram Bot API для отправки файлов """

    def __init__(self, config: TelegramConfig) -> None:
        self._token = config.get_token()
        self._chat_id = config.get_chat_id()

    def send_text_message(self, text: str) -> None:
        """Отправка текстового сообщения

        Args:
            text (str): текст отправляемого сообщения
        """
        url = f"{self.base_url}{self._token}{self.text_message_endpoint}"
        params = {"chat_id": self._chat_id, "text": text, "parse_mode": "HTML"}
        requests.get(url=url, params=params)

    def send_document_attachment(self, document_path: str) -> None:
        """Отправка документа

        Args:
            document_path (str): путь к отправляемому документу
        """
        files = {"document": open(document_path, "rb")}
        url = f"{self.base_url}{self._token}{self.document_attachment_endpoint}"
        data = {
            "chat_id": self._chat_id,
        }
        requests.post(url=url, data=data, files=files)


def main():
    # Запрос заявок из КПО Кобра
    cobra_config = CobraConfig()
    cobra_base = CobraTaskReport(cobra_config)
    task_objects = cobra_base.get_tasks()
    if len(task_objects):
        # Генерация файла отчета и текста сообщения в Telegram
        task_report = CobraTaskExcelReport()
        report_message = CobraTaskReportMessage()
        report_message.add_report_header()
        task_report.set_header()
        for tehn, one_tehn_tasks in groupby(
            task_objects, lambda task_list: task_list["tehn"]
        ):
            report_message.add_tehn_to_report_message(tehn)
            for task in one_tehn_tasks:
                report_message.add_task_to_report_message(task)
                task_report.set_row(task)
            report_message.add_empty_string_to_report_message()
        task_report.set_footer()
        task_report.save()
        report_message.add_generation_datetime()

        # Отправка уведомлений Telegram
        tg_config = TelegramConfig()
        tg = Telegram(tg_config)
        tg.send_text_message(report_message.get_report_message_text())
        tg.send_document_attachment(task_report.export_filename)
    else:
        logger.info("Заявки отсутствуют")

    # Очистка каталог экспорта отчетов
    shutil.rmtree(
        CobraTaskExcelReport.export_path,
        ignore_errors=True,
    )


if __name__ == "__main__":
    main()
