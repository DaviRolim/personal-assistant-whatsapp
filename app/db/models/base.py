from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, Column

class Base(DeclarativeBase):
    pass

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
