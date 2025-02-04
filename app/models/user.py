from sqlalchemy import Column, Integer, String, DateTime, JSON, text
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    whatsapp_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(100))
    timezone = Column(String(50), nullable=False, server_default='UTC')
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    last_active = Column(DateTime(timezone=True))
    settings = Column(JSON)
    
    projects = relationship("Project", back_populates="user")
    goals = relationship("Goal", back_populates="user")
