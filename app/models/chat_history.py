from sqlalchemy import Column, Integer, String, DateTime, JSON, text
from app.db.database import Base

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False)
    message = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
