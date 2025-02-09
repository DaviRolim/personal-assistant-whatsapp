import logging

import uvicorn
from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai_companion_instance import ai_companion_service
from app.db.database import Base, engine, get_db

# Configure root logger

logging.basicConfig(
    level=logging.DEBUG,  # Capture all log levels
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Save all logs to a file
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
    except Exception as e:
        print(f"Error during scheduler shutdown: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    print(f'Webhook received: {body}')
    return await ai_companion_service.handle_webhook_data(body, db)

@app.post("/trials")
async def trials(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    print(f'body: {body}')
    return await ai_companion_service.handle_webhook_data(body, db)

    # add_message("user", body['message'])
    # sql_agent_response = await agent_response(body['message'], get_messages())
    # add_message("assistant", sql_agent_response)
    # return sql_agent_response

    # response = await insert(body['statement'], body['values'])
    # return response

# @app.get("/clear-history")
# def clear_history():
#     clear_messages()
#     return {"status": "Message history cleared"}

def run():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
