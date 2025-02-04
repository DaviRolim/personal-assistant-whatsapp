from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Task(Base):
    __tablename__ = 'tasks'
    
    task_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id', ondelete='CASCADE'))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), server_default='todo')
    priority = Column(String(10), server_default='medium')
    estimated_duration = Column(Integer)  # minutes
    actual_duration = Column(Integer)  # minutes
    due_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    completed_at = Column(DateTime(timezone=True))
    parent_task_id = Column(Integer, ForeignKey('tasks.task_id'))
    
    project = relationship("Project", back_populates="tasks")
    subtasks = relationship("Task")
    
    __table_args__ = (
        CheckConstraint("status IN ('todo', 'in_progress', 'blocked', 'completed')"),
        CheckConstraint("priority IN ('high', 'medium', 'low')"),
        CheckConstraint("parent_task_id != task_id"),
    )
