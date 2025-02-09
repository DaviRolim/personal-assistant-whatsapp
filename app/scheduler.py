import os
from random import choice
from typing import List
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.ai_companion_instance import ai_companion_service
from app.db.database import get_db

# Message lists for each scheduled time
five_am_messages: List[str] = [
    "Good morning, check my projects and tasks and suggest something for me to start the day accomplishing something",
    "Hi, ask me my energy level or free time and based on the information, suggest a task or an activity",
    "Check my projects and tasks and suggest something for me to start the day accomplishing something",
    "Check my tasks that are in_progress for a long time and there's no recent progress log and suggest something to do"
]

ten_am_messages: List[str] = [
    "It's 10 AM, review my schedule and provide any quick tasks to boost my productivity",
    "Good morning, ask me what I'm doing and if I'm doing something that is not aligned with my priorities, persuade me to do something more productive"
]


two_pm_messages: List[str] = [
    "It's 2 PM, any mid-day adjustments or tasks you recommend?",
    "Good afternoon, ask me what I'm doing and if I'm doing something that is not aligned with my priorities, persuade me to do something more productive"
]


four_pm_messages: List[str] = [
    "At 4 PM, summarize my progress and provide suggestions for wrapping up the day",
    "Good afternoon, ask me what I'm doing and if I'm doing something that is not aligned with my priorities, persuade me to do something more productive"
]



async def run_scheduled_webhook(messages: List[str]) -> None:
    """Execute the webhook task for a randomly selected message from the list."""
    async for db in get_db():
        try:
            message = choice(messages)
            payload = {
                "apikey": os.getenv("EVOLUTION_APIKEY"),
                "data": {
                    "message": {
                        "conversation": message

                    },
                    "key": {
                        "id": os.getenv("EVOLUTION_KEY_ID"),
                        "remoteJid": "558399763846@s.whatsapp.net",
                        "fromMe": True
                    }
                }
            }
            await ai_companion_service.handle_webhook_data(payload, db)
        except Exception as e:
            print(f"Error in scheduled webhook: {str(e)}")
        break  # Exit after first iteration since we only need one session


def start_scheduler() -> AsyncIOScheduler:
    """Initialize and start the APScheduler with cron triggers for specified times."""
    sch_timezone = ZoneInfo("America/Sao_Paulo")
    scheduler = AsyncIOScheduler(timezone=sch_timezone)

    scheduler.add_job(
        run_scheduled_webhook,
        CronTrigger(hour=5, minute=0, timezone=sch_timezone),
        args=[five_am_messages],
        id="webhook_5am"
    )
    scheduler.add_job(
        run_scheduled_webhook,
        CronTrigger(hour=10, minute=0, timezone=sch_timezone),
        args=[ten_am_messages],
        id="webhook_10am"
    )
    scheduler.add_job(
        run_scheduled_webhook,
        CronTrigger(hour=14, minute=0, timezone=sch_timezone),
        args=[two_pm_messages],
        id="webhook_2pm"
    )
    scheduler.add_job(
        run_scheduled_webhook,
        CronTrigger(hour=16, minute=0, timezone=sch_timezone),
        args=[four_pm_messages],
        id="webhook_4pm"
    )

    scheduler.start()
    return scheduler 