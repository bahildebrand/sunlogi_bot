import logging
import os
from sunbot.models import Base
from sunbot.models import MsgIds
from sunbot.models import Stockpiles
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from typing import List


class SunDB:
    def __init__(self):
        host = os.environ.get("DB_HOST")
        password = os.environ.get("DB_PASSWORD")

        url_object = URL.create(
            "postgresql+asyncpg",
            username="postgres",
            password=password,
            host=host,
            database="postgres",
        )

        self.engine = create_async_engine(url_object)
        self.async_session = async_sessionmaker(self.engine)

    async def init_models(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def addStockPile(self, channel_id: str, name: str, depot: str, code: int):
        async with self.async_session() as session:
            new_stockpile = Stockpiles(
                channel_id=channel_id,
                stockpile_name=name,
                depot=depot,
                code=code,
                archived=False
            )

            session.add(new_stockpile)
            await session.commit()

    async def getStockPile(self, name: str):
        async with self.async_session() as session:
            statement = select(Stockpiles).where(
                Stockpiles.stockpile_name == name)

            result = await session.execute(statement)

            return result.fetchone()

    async def archiveStockpile(self, name: str, channel_id: str) -> bool:
        async with self.async_session() as session:
            stmt = update(Stockpiles).where(Stockpiles.stockpile_name == name).where(
                Stockpiles.channel_id == str(channel_id)).values(archived=True)

            result = await session.execute(stmt)
            if result.rowcount == 0:
                return False

            await session.commit()

        return True

    async def restoreArchivedStockpile(self, name: str, channel_id: str) -> bool:
        async with self.async_session() as session:
            stmt = update(Stockpiles).where(Stockpiles.stockpile_name == name).where(
                Stockpiles.channel_id == str(channel_id)).values(archived=False)

            result = await session.execute(stmt)
            if result.rowcount == 0:
                return False

            await session.commit()

        return True

    async def deleteStockpile(self, name: str, channel_id: str) -> bool:
        async with self.async_session() as session:
            stmt = delete(Stockpiles).where(Stockpiles.stockpile_name == name).where(
                Stockpiles.channel_id == str(channel_id))
            result = await session.execute(stmt)

            if result.rowcount == 0:
                return False

            await session.commit()

        return True

    async def clearStockpiles(self):
        async with self.async_session() as session:
            stmt = delete(Stockpiles)
            await session.execute(stmt)
            await session.commit()

    async def getAllStockpiles(self, channel_id: str):
        async with self.async_session() as session:
            statement = select(Stockpiles).where(
                Stockpiles.channel_id == str(channel_id))

            result = await session.execute(statement)
            return result.all()

    async def getAllMessageIds(self) -> List[MsgIds]:
        async with self.async_session() as session:
            statement = select(MsgIds)

            result = await session.execute(statement)
            return [tuple[0] for tuple in result.all()]

    async def getMessageId(self, channel_id):
        async with self.async_session() as session:
            statement = select(MsgIds).where(
                MsgIds.channel_id == str(channel_id))
            result = await session.execute(statement)

            output = result.one_or_none()
            logging.debug(output)
            return output

    async def setMessageId(self, channel_id: str, message_id):
        async with self.async_session() as session:
            new_msg = MsgIds(
                channel_id=channel_id,
                message_id=message_id
            )

            session.add(new_msg)
            await session.commit()
