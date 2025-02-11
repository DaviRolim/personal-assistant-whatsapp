from sqlalchemy import (JSON, CheckConstraint, Column, DateTime, Integer,
                        String, Text, text)

from app.db.database import Base


class AIInteraction(Base):
    __tablename__ = 'ai_interactions'
    
    interaction_id = Column(Integer, primary_key=True)
    message_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    intent = Column(String(50))
    context_data = Column(JSON)
    effectiveness_rating = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    __table_args__ = (
        CheckConstraint("effectiveness_rating BETWEEN 1 AND 5"),
    )
