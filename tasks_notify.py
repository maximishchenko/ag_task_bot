from app.service.config import CobraConfig, TelegramConfig
from app.service.cobra import CobraTaskReport, CobraTaskReportMessage
from app.service.report import CobraTaskExcelReport
import shutil
from itertools import groupby
from app.bot_global import bot
import asyncio

PYTHONDONTWRITEBYTECODE=1

async def send_tasks():
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
        for chat in tg_config.get_task_full_report_chat_ids():
            await bot.send_message(chat, report_message.get_report_message_text(), parse_mode='html')
            await bot.send_document(chat, open(task_report.export_filename, 'rb'))


    # Очистка каталог экспорта отчетов
    shutil.rmtree(
        CobraTaskExcelReport.export_path,
        ignore_errors=True,
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_tasks())
