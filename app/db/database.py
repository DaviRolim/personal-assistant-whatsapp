import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

load_dotenv()

db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("DB_URL environment variable is not set")

print(f'[DH] DB_URL: {db_url}')
engine = create_async_engine(
    db_url,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections periodically
    connect_args={"statement_cache_size": 0}  # Disable statement caching for pgbouncer compatibility
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

@asynccontextmanager
async def get_db():
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()