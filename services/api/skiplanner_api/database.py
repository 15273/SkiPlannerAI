from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

if settings.skimate_dev_json_api:
    engine = None
    AsyncSessionLocal = None
else:
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncIterator[AsyncSession | None]:
    if settings.skimate_dev_json_api:
        yield None
        return
    assert AsyncSessionLocal is not None
    async with AsyncSessionLocal() as session:
        yield session
