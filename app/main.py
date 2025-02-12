import logging

import uvicorn
from fastapi import FastAPI, Request

from app.api.dependencies import chatbot_controller
# from app.integrations.evolution_api import get_base64_from_media_message
from app.core.scheduler import get_scheduler
from app.db.database import Base, engine, get_db

# Configure root logger

logging.basicConfig(
    level=logging.INFO,  # Capture all log levels
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"./logs/app_{logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, None, None, None), '%Y-%m-%d')}.log"),  # Daily log file
        logging.StreamHandler()  # Print logs to console
    ]
)
app = FastAPI()

@app.on_event("startup")
async def init_db():
    print('Connecting to database...')
    async with engine.begin() as conn:
        print('Creating tables...')
        await conn.run_sync(Base.metadata.create_all)
        print('Tables created!')

@app.on_event("startup")
async def start_scheduler_event():
    try:
        # Initialize the global scheduler
        get_scheduler()  # This initializes and starts the scheduler if not already running
        print("Scheduler started successfully.")
    except Exception as e:
        print(f"Failed to start scheduler: {str(e)}")

@app.on_event("shutdown")
async def shutdown_scheduler_event():
    try:
        # Get the global scheduler instance and shut it down
        get_scheduler().shutdown()  # Get the instance and shut it down in one line
        print("Scheduler shutdown successfully.")
        
        # dispose the engine
        await engine.dispose()
        print("Engine disposed successfully.")
    except Exception as e:
        print(f"Error during scheduler shutdown: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    logging.info(f'Webhook received: {body}')
    async with get_db() as db:
        return await chatbot_controller.handle_webhook_data(body, db)


def run():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
