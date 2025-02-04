from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, Numeric, text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Goal(Base):
    __tablename__ = 'goals'
    
    goal_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    goal_type = Column(String(50))
    target_value = Column(Numeric)
    current_value = Column(Numeric, server_default='0')
    unit = Column(String(50))
    frequency = Column(String(20))
    status = Column(String(20), server_default='active')
    deadline = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    user = relationship("User", back_populates="goals")
    
    __table_args__ = (
        CheckConstraint("goal_type IN ('fitness', 'learning', 'project', 'habit', 'personal')"),
        CheckConstraint("status IN ('active', 'achieved', 'abandoned')"),
    )
