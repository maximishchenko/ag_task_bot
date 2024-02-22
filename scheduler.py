from tasks_notify import send_tasks
import asyncio
import aiocron


async def main():
    send_tasks_to_chat = aiocron.crontab("36 16 * * *", func=send_tasks, args=(), start=True)
    # cron_sender_third = aiocron.crontab("00 16 * * *", func=sender, args=(), start=True)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
