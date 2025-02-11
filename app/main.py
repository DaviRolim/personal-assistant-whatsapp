import logging

import uvicorn
from fastapi import FastAPI, Request

from app.core.ai.tools.whatsapp_tool import get_base64_from_media_message
from app.core.ai_companion_instance import ai_companion_service
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
        from app.scheduler import start_scheduler
        scheduler = start_scheduler()
        app.state.scheduler = scheduler
        print("Scheduler started successfully.")
    except Exception as e:
        print(f"Failed to start scheduler: {str(e)}")

@app.on_event("shutdown")
async def shutdown_scheduler_event():
    try:
        if hasattr(app.state, 'scheduler'):
            scheduler = app.state.scheduler
            scheduler.shutdown()
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
    print(f'Webhook received: {body}')
    async with get_db() as db:
        return await ai_companion_service.handle_webhook_data(body, db)

@app.post("/trials")
async def trials(request: Request):
    body = await request.json()
    print(f'body: {body}')
    async with get_db() as db:
        return await ai_companion_service.handle_webhook_data(body, db)

# @app.post("/try-audio")
# async def try_audio(request: Request):
#     body = await request.json()
#     print(f'body: {body}')
#     res = await get_base64_from_media_message(body['instance'], body['data']['key']['id'], body['apikey'])
#     return {"base64": res}


# @app.get("/clear-history")
# def clear_history():
#     clear_messages()
#     return {"status": "Message history cleared"}

def run():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
