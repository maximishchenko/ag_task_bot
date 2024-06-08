"""
Скрипт для отправки уведомлений в чаты Telegram вручную.

Используется в случае, если не сработала автоматическая отправка.
Отправляет персональные уведомления о незавершенных заявках, которые техник
не успел отработать до конца рабочей смены
"""

# Standard Library
import asyncio

from tasks_notify import send_personal_tasks

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_personal_tasks(False))
