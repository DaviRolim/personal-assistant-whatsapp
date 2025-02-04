from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, Numeric, text
from app.db.database import Base

class ProgressLog(Base):
    __tablename__ = 'progress_logs'
    
    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    log_type = Column(String(50), nullable=False)
    related_task_id = Column(Integer, ForeignKey('tasks.task_id'))
    related_goal_id = Column(Integer, ForeignKey('goals.goal_id'))
    related_project_id = Column(Integer, ForeignKey('projects.project_id'))
    value = Column(Numeric)
    description = Column(Text)
    media_url = Column(Text)
    duration = Column(Integer)  # minutes
    energy_level = Column(Integer)
    mood = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    __table_args__ = (
        CheckConstraint("log_type IN ('task_update', 'goal_progress', 'media_upload', 'activity', 'focus_session')"),
        CheckConstraint("energy_level BETWEEN 1 AND 5"),
    )
