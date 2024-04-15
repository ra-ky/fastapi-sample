from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
import asyncio

# PostgreSQL 연결 정보
# DATABASE_URL = "postgresql+asyncpg://raky:1234@postgres/raky"
# MariaDB 연결 정보
DATABASE_URL = "mysql+aiomysql://raky:1234@mariadb/raky"

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


# asyncio.run(init_db())

from models import User
from sqlmodel import select


async def main():
    async for db in get_db():
        stmt = select(User)
        user = (await db.exec(stmt)).all()
        print(user)


asyncio.run(main())
