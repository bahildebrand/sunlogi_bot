from psycopg2.pool import ThreadedConnectionPool
from sqlalchemy import URL
from sqlalchemy import create_engine
from sunbot.models import Base
from sunbot.models import Stockpiles
from sunbot.models import MsgIds
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import delete
import os
from typing import List
import logging


class SunDB:
    def __init__(self):
        host = os.environ.get("DB_HOST")
        password = os.environ.get("DB_PASSWORD")

        url_object = URL.create(
            "postgresql+psycopg2",
            username="postgres",
            password=password,
            host=host,
            database="postgres",
        )

        self.engine = create_engine(url_object)
        Base.metadata.create_all(self.engine)

    def addStockPile(self, channel_id: str, name: str, depot: str, code: int):
        with Session(self.engine) as session:
            new_stockpile = Stockpiles(
                channel_id=channel_id,
                stockpile_name=name,
                depot=depot,
                code=code,
            )

            session.add(new_stockpile)
            session.commit()

    def getStockPile(self, name: str):
        with Session(self.engine) as session:
            statement = select(Stockpiles).where(
                Stockpiles.stockpile_name == name)

            result = session.execute(statement)

            return result.fetchone()

    def deleteStockpile(self, name: str, channel_id: str):
        with Session(self.engine) as session:
            stmt = delete(Stockpiles).where(Stockpiles.stockpile_name == name).where(
                Stockpiles.channel_id == str(channel_id))
            session.execute(stmt)
            session.commit()

    def clearStockpiles(self):
        with Session(self.engine) as session:
            stmt = delete(Stockpiles)
            session.execute(stmt)
            session.commit()

    def getAllStockpiles(self, channel_id: str):
        with Session(self.engine) as session:
            statement = select(Stockpiles).where(
                Stockpiles.channel_id == str(channel_id))

            result = session.execute(statement)
            return result.all()

    def getAllMessageIds(self) -> List[MsgIds]:
        with Session(self.engine) as session:
            statement = select(MsgIds)

            result = session.execute(statement)
            return [tuple[0] for tuple in result.all()]

    def getMessageId(self, channel_id):
        with Session(self.engine) as session:
            statement = select(MsgIds).where(
                MsgIds.channel_id == str(channel_id))
            result = session.execute(statement)

            output = result.one_or_none()
            logging.debug(output)
            return output

    def setMessageId(self, channel_id, message_id):
        with Session(self.engine) as session:
            new_msg = MsgIds(
                channel_id=channel_id,
                message_id=message_id
            )

            session.add(new_msg)
            session.commit()
