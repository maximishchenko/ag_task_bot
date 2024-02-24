from app.service.config import CobraConfig, TelegramConfig
from app.service.cobra import CobraTaskReport, CobraTaskReportMessage
from app.service.report import CobraTaskExcelReport
import shutil
from itertools import groupby
from app.bot_global import bot, db_file
from app.service.db import User
import asyncio

PYTHONDONTWRITEBYTECODE=1

user = User(db_file)

async def send_tasks():
    # Запрос заявок из КПО Кобра
    cobra_config = CobraConfig()
    cobra_base = CobraTaskReport(cobra_config)
    task_objects = cobra_base.get_tasks()
    tg_config = TelegramConfig()        
    if len(task_objects):
        # Генерация файла отчета и текста сообщения в Telegram
        task_report = CobraTaskExcelReport()
        report_message = CobraTaskReportMessage()
        report_message.add_report_header()
        task_report.set_header()
        for tehn, one_tehn_tasks in groupby(
            task_objects, lambda task_list: task_list["tehn"]
        ):
            
            current_user = user.get_user_by_tehn(tehn)
            if (current_user):
                # добавление заявки к персональному уведомлению
                report_message_personal = CobraTaskReportMessage()
                report_message_personal.add_tehn_to_report_message(tehn)


            report_message.add_tehn_to_report_message(tehn)
            for task in one_tehn_tasks:
                # добавление заявки к персональному уведомлению
                if (current_user):
                    report_message_personal.add_task_to_report_message(task)

                report_message.add_task_to_report_message(task)
                task_report.set_row(task)

            # добавление заявки к персональному уведомлению
            if (current_user):
                report_message_personal.add_empty_string_to_report_message()

            report_message.add_empty_string_to_report_message()

            # Отправка персонального уведомления для зарегистрированных пользователей
            # current_user = user.get_user_by_tehn(tehn)
            if (current_user):
                await bot.send_message(current_user.chat_id, report_message_personal.get_report_message_text(), parse_mode='html')

        task_report.set_footer()
        task_report.save()
        report_message.add_generation_datetime()

        # Отправка уведомлений Telegram
        for chat in tg_config.get_task_full_report_chat_ids():
            await bot.send_message(chat, report_message.get_report_message_text(), parse_mode='html')
            await bot.send_document(chat, open(task_report.export_filename, 'rb'))
    else:
        for chat in tg_config.get_task_full_report_chat_ids():
            await bot.send_message(chat, "Заявки на текущую дату отсутствуют", parse_mode='html')


    # Очистка каталог экспорта отчетов
    shutil.rmtree(
        CobraTaskExcelReport.export_path,
        ignore_errors=True,
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_tasks())
