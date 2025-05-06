from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
class DBInterface(ABC):
    @abstractmethod
    def add(self, session: AsyncSession, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, session: AsyncSession, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, session: AsyncSession, *args, **kwargs):
        pass

    @abstractmethod
    def list(self, session: AsyncSession, *args, **kwargs):
        pass