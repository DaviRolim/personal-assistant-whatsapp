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
    "Hi, ask me my energy level or free time and based on the information, suggest a task or an activity"
]

ten_am_messages: List[str] = [
    "It's 10 AM, review my schedule and provide any quick tasks to boost my productivity",
    "Good morning, remind me of any urgent work that may require immediate attention"
]

two_pm_messages: List[str] = [
    "It's 2 PM, any mid-day adjustments or tasks you recommend?",
    "Afternoon check: suggest a task to re-energize or refocus me"
]

four_pm_messages: List[str] = [
    "At 4 PM, summarize my progress and provide suggestions for wrapping up the day",
    "It's nearly the end of the workday; suggest priority tasks to finish remaining activities"
]


async def run_scheduled_webhook(messages: List[str]) -> None:
    """Execute the webhook task for a randomly selected message from the list."""
    async for db in get_db():
        try:
            message = choice(messages)
            payload = {
                "apikey": "35AC53D3BC28-4F9B-A25C-6B53F7BF624E",
                "data": {
                    "message": {
                        "conversation": message
                    },
                    "key": {
                        "id": "3EB06A1CDC76D828C0193A",
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
        CronTrigger(hour=11, minute=20, timezone=sch_timezone),
        args=[ten_am_messages],
        id="webhook_11am_20"
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