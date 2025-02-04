from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Project(Base):
    __tablename__ = 'projects'
    
    project_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), server_default='planning')
    priority = Column(String(10), server_default='medium')
    start_date = Column(DateTime(timezone=True))
    deadline = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    
    __table_args__ = (
        CheckConstraint("status IN ('planning', 'active', 'paused', 'completed', 'abandoned')"),
        CheckConstraint("priority IN ('high', 'medium', 'low')"),
    )
