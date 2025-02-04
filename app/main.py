from fastapi import FastAPI, Request, Depends, HTTPException
from app.core.ai.tools.sql_tool import insert
from app.services.ai_companion_service import AICompanionService
from app.core.ai.local_memory import clear_messages, get_messages, add_message
from app.db.database import engine, Base
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.db.database import get_db
from app.core.ai.agents.sql_agent import agent_response

app = FastAPI()
ai_companion_service = AICompanionService()

@app.on_event("startup")
async def init_db():
    print(f'Connecting to database...')
    async with engine.begin() as conn:
        print(f'Creating tables...')
        await conn.run_sync(Base.metadata.create_all)
        print(f'Tables created!')

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    print(f'Webhook received: {body}')
    return ai_companion_service.handle_webhook_data(body)

@app.post("/trials")
async def trials(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    print(f'body: {body}')
    add_message("user", body['message'])
    sql_agent_response = await agent_response(body['message'], get_messages())
    add_message("assistant", sql_agent_response)
    return sql_agent_response
    # response = await insert(body['statement'], body['values'])
    # return response

@app.get("/clear-history")
def clear_history():
    clear_messages()
    return {"status": "Message history cleared"}

def run():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
