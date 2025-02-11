from sqlalchemy import (CheckConstraint, Column, DateTime, Integer, String,
                        Text, text)

from app.db.database import Base


class ProcrastinationPattern(Base):
    __tablename__ = 'procrastination_patterns'
    
    pattern_id = Column(Integer, primary_key=True)
    trigger_type = Column(String(100), nullable=False)
    description = Column(Text)
    frequency = Column(Integer, server_default='1')
    impact_level = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    __table_args__ = (
        CheckConstraint("impact_level BETWEEN 1 AND 5"),
    )
