import uvicorn
from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Base, engine, get_db
from app.services.ai_companion_service import AICompanionService

app = FastAPI()
ai_companion_service = AICompanionService(memory_type="local")

@app.on_event("startup")
async def init_db():
    print('Connecting to database...')
    async with engine.begin() as conn:
        print('Creating tables...')
        await conn.run_sync(Base.metadata.create_all)
        print('Tables created!')

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
