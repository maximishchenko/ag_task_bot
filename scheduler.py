from tasks_notify import send_all_tasks
import asyncio
import aiocron
from app.bot_global import tg_config


async def main():
    task_full_report_time = tg_config.get_task_full_report_shedule_time()
    task_full_report_min = task_full_report_time[1]
    task_full_report_hour = task_full_report_time[0]
    send_tasks_to_chat = aiocron.crontab(f"{task_full_report_min} {task_full_report_hour} * * *", func=send_all_tasks, args=(), start=True)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
