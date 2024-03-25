"""
Скрипт для отправки уведомлений в чаты Telegram по расписанию планировщика.

Отправляет общую информацию в группу и персональные уведомления
"""

# Standard Library
import asyncio
import shutil
from itertools import groupby

from aiogram import types

from app.bot_global import bot, cobra_config, db_file, tg_config
from app.service.cobra import CobraTaskReport, CobraTaskReportMessage
from app.service.db import User
from app.service.report import CobraTaskExcelReport


async def send_all_tasks():
    """
    Формирование общей статистики по аварийным заявкам .

    Запрашивает статистику заявок по аварийным объектам не старше
    текущей даты из КПО Кобра. Сортирует по исполнителю.
    Отправляет в общую группу
    """
    cobra_base = CobraTaskReport(cobra_config)
    task_objects = cobra_base.get_tasks()
    if task_objects:
        task_report = CobraTaskExcelReport()
        task_report.set_header()
        tehn_count = 0
        report_message = CobraTaskReportMessage()
        report_message.add_report_header()
        for tehn, one_tehn_tasks in groupby(
            task_objects, lambda task_list: task_list["tehn"]
        ):
            tehn_count += 1
            report_message.add_tehn_to_report_message(tehn)
            for task in one_tehn_tasks:
                task_report.set_row(task)
                report_message.add_task_to_report_message(task)
                report_message.add_empty_string_to_report_message()

            if tehn_count == 3:
                report_message.add_generation_datetime()
                for chat in tg_config.get_task_full_report_chat_ids():
                    report_msg = report_message.get_report_message_text()
                    await bot.send_message(chat, report_msg, parse_mode="html")
                report_message = CobraTaskReportMessage()
                report_message.add_report_header()
                tehn_count = 0

        report_message.add_generation_datetime()

        task_report.set_footer()
        task_report.save()

        for chat in tg_config.get_task_full_report_chat_ids():
            # report_msg = report_message.get_report_message_text()
            # await bot.send_message(chat, report_msg, parse_mode="html")
            document = open(task_report.export_filename, "rb")
            await bot.send_document(chat, document)
    else:
        for chat in tg_config.get_task_full_report_chat_ids():
            await bot.send_message(
                chat, "Заявки на текущую дату отсутствуют", parse_mode="html"
            )

    # Очистка каталог экспорта отчетов
    shutil.rmtree(
        CobraTaskExcelReport.export_path,
        ignore_errors=True,
    )


async def send_personal_tasks():
    """
    Отправляет персональные уведомления.

    Выбирает заявки каждого техника, с датой исполнения не превосходящей
    текущую дату. В случае, если техник прошел процедуру регистрации -
    отправляет персональное уведомление
    """
    user = User(db_file)
    cobra_base = CobraTaskReport(cobra_config)
    task_objects = cobra_base.get_tasks()
    if task_objects:
        for tehn, one_tehn_tasks in groupby(
            task_objects, lambda task_list: task_list["tehn"]
        ):
            current_user = user.get_user_by_tehn(tehn)
            if current_user:
                report_message_personal = CobraTaskReportMessage()
                report_message_personal.add_tehn_to_report_message(tehn)
                tasks_for_accept = []
                for task in one_tehn_tasks:
                    tasks_for_accept.append(task["n_abs"])
                    report_message_personal.add_task_to_report_message(task)
                report_message_personal.add_empty_string_to_report_message()
                kb = (
                    types.InlineKeyboardButton(
                        text="Ознакомлен",
                        callback_data=f"accept_action|{task['tehn']}",
                    ),
                )
                accept_kb = types.InlineKeyboardMarkup(inline_keyboard=[kb])
                await bot.send_message(
                    current_user.chat_id,
                    report_message_personal.get_report_message_text(),
                    parse_mode="html",
                    reply_markup=accept_kb,
                )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_all_tasks())
    loop.run_until_complete(send_personal_tasks())
