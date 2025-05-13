from contextlib import asynccontextmanager
from typing import AsyncContextManager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.models import Base
from config import PSQL_URL

engine = create_async_engine(PSQL_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_async_session() -> AsyncContextManager[AsyncSession]:
    async with async_session_maker() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
