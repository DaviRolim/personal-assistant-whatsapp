import logging
from datetime import datetime, timedelta
from random import choice
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from app.services.message_scheduler_service import send_scheduled_message

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None

# Define timezone
TIMEZONE = ZoneInfo("America/Sao_Paulo")

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
    # "Good afternoon, ask me what I'm doing and if I'm doing something that is not aligned with my priorities, persuade me to do something more productive"
]

async def run_scheduled_webhook(messages: List[str]) -> None:
    """Execute the webhook task for a randomly selected message from the list."""
    try:
        message = choice(messages)
        await send_scheduled_message(message)
    except Exception as e:
        logger.error(f"Error in scheduled webhook: {str(e)}")

def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        
        # Add daily scheduled jobs with explicit timezone
        scheduler.add_job(
            run_scheduled_webhook,
            CronTrigger(hour=5, minute=0, timezone=TIMEZONE),
            args=[five_am_messages],
            id="webhook_5am"
        )
        scheduler.add_job(
            run_scheduled_webhook,
            CronTrigger(hour=10, minute=0, timezone=TIMEZONE),
            args=[ten_am_messages],
            id="webhook_10am"
        )
        # scheduler.add_job(
        #     run_scheduled_webhook,
        #     CronTrigger(hour=14, minute=0, timezone=TIMEZONE),
        #     args=[two_pm_messages],
        #     id="webhook_2pm"
        # )
        scheduler.add_job(
            run_scheduled_webhook,
            CronTrigger(hour=16, minute=0, timezone=TIMEZONE),
            args=[four_pm_messages],
            id="webhook_4pm"
        )
        
        scheduler.start()
    return scheduler

async def schedule_interaction(
    message: str,
    day: Optional[str] = None,
    hour: int = 0,
    minute: int = 0
) -> Dict[str, str]:
    """
    Schedule a new interaction for the specified time.
    
    Args:
        message: The message to send at the scheduled time
        day: The day to schedule the interaction (YYYY-MM-DD format). If None, uses today
        hour: The hour to schedule the interaction (0-23)
        minute: The minute to schedule the interaction (0-59)
    
    Returns:
        Dict containing success status and message
    """
    try:
        # Get the scheduler instance
        scheduler = get_scheduler()
        
        # Parse the target date/time
        if day is None:
            target_date = datetime.now(TIMEZONE).date()
        else:
            target_date = datetime.strptime(day, "%Y-%m-%d").date()
        
        # Create target datetime
        target_time = datetime.combine(
            target_date,
            datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
        ).replace(tzinfo=TIMEZONE)
        
        # If the target time is in the past, add a day
        if target_time < datetime.now(TIMEZONE):
            target_time += timedelta(days=1)
        
        # Schedule the job
        job_id = f"scheduled_interaction_{target_time.strftime('%Y%m%d_%H%M')}"
        scheduler.add_job(
            send_scheduled_message,
            DateTrigger(run_date=target_time),
            args=[message],
            id=job_id
        )
        
        scheduled_time = target_time.strftime("%Y-%m-%d %H:%M")
        return {
            "success": True,
            "message": f"Interaction scheduled for {scheduled_time}"
        }
        
    except Exception as e:
        logger.error(f"Failed to schedule interaction: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to schedule interaction: {str(e)}"
        } 