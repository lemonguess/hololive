from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete
from typing import AsyncIterator, Union
from config import app_config
db_config = app_config.database_config

class AsyncDatabaseManager:
    def __init__(self):
        self.database_url = self._init_engine_url()  # 修改为方法调用
        self.pool_size = int(db_config.db_pool_size)
        self.max_overflow = int(db_config.db_pool_max_overflow)
        self.engine = create_async_engine(self.database_url, pool_size=self.pool_size, max_overflow=self.max_overflow)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
    def _init_engine_url(self) -> str:
        db_type = db_config.db_type
        if db_type == 'sqlite':
            database = db_config.db_name
            engine_url = f"sqlite+aiosqlite:///{database}.db"
        elif db_type == 'mysql':
            user = db_config.db_user
            password = db_config.db_password
            host = db_config.db_host
            port = db_config.db_port
            database = db_config.db_name
            engine_url = f"mysql+asyncmy://{user}:{password}@{host}:{port}/{database}"
        elif db_type == 'pgsql':
            user = db_config.db_user
            password = db_config.db_password
            host = db_config.db_host
            port = db_config.db_port
            database = db_config.db_name
            engine_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError("Unsupported database type")
        return engine_url

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        session = self.async_session()
        try:
            yield session
            await session.commit()  # 自动提交事务
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    async def create(self, db: AsyncSession, model):
        db.add(model)
        await db.flush()
        db.expunge(model)
        return model

    async def read(self, db: AsyncSession, query):
        result = await db.execute(query)
        return result.scalars().all()

    async def update(self, db: AsyncSession, model, **kwargs):
        async with db.begin():
            for key, value in kwargs.items():
                setattr(model, key, value)
            await db.flush()
            db.expunge(model)
            return model

    async def delete(self, db: AsyncSession, model):
        async with db.begin():
            await db.delete(model)
    async def create_tables(self, Base):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

# 使用示例
async def main():
    database_url = "postgresql+asyncpg://user:password@localhost/dbname"
    manager = AsyncDatabaseManager(database_url)

    # 假设有一个User模型
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        email = Column(String)

    async with manager.get_session() as session:
        # 示例：插入数据
        new_user = User(name="John Doe", email="john@example.com")
        await manager.create(session, new_user)

        # 示例：查询数据
        query = select(User).where(User.id == 1)
        users = await manager.read(session, query)
        print(users)

        # 示例：更新数据
        user_to_update = await session.execute(select(User).where(User.id == 1))
        user_to_update = user_to_update.scalars().first()
        updated_user = await manager.update(session, user_to_update, name="Jane Doe")
        print(updated_user)

        # 示例：删除数据
        await manager.delete(session, user_to_update)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
