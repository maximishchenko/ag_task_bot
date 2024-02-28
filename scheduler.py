"""
Скрипт реализует функции планировщика заданий приложения.

Используется для запуска заплатированных заданий и управления ими средствами
приложения. Запуск возможен через systemd или supervisor
"""

import asyncio

import aiocron  # noqa

from app.bot_global import tg_config  # noqa
from tasks_notify import send_all_tasks  # noqa
from tasks_notify import send_personal_tasks  # noqa


async def main():
    """
    Реализация планировщика заданий.

    Направляет общие и персональные уведомления по времени, заданном в
    файле конфигурации настроек
    """
    task_full_report_time = tg_config.get_task_full_report_shedule_time()
    task_full_report_min = task_full_report_time[1]
    task_full_report_hour = task_full_report_time[0]
    aiocron.crontab(
        f"{task_full_report_min} {task_full_report_hour} * * *",
        func=send_all_tasks,
        args=(),
        start=True,
    )

    personal_report_time = tg_config.get_task_personal_report_shedule_time()
    task_personal_report_min = personal_report_time[1]
    task_personal_report_hour = personal_report_time[0]
    aiocron.crontab(
        f"{task_personal_report_min} {task_personal_report_hour} * * *",
        func=send_personal_tasks,
        args=(),
        start=True,
    )

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
