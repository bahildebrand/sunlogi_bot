from psycopg2.pool import ThreadedConnectionPool
from sqlalchemy import URL
from sqlalchemy import create_engine
from sunbot.models import Base
from sunbot.models import Stockpiles
from sunbot.models import MsgIds
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import delete


class SunDB:
    def __init__(self):
        url_object = URL.create(
            "postgresql+psycopg2",
            username="postgres",
            password="password",
            host="localhost",
            database="postgres",
        )

        self.engine = create_engine(url_object, echo=True)
        Base.metadata.create_all(self.engine)

    def addStockPile(self, name: str, depot: str, code: int):
        with Session(self.engine) as session:
            new_stockpile = Stockpiles(
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

    def deleteStockpile(self, name: str):
        with Session(self.engine) as session:
            stmt = delete(Stockpiles).where(Stockpiles.stockpile_name == name)
            session.execute(stmt)
            session.commit()

    def clearStockpiles(self):
        with Session(self.engine) as session:
            stmt = delete(Stockpiles)
            session.execute(stmt)
            session.commit()

    def getAllStockpiles(self):
        with Session(self.engine) as session:
            statement = select(Stockpiles)

            result = session.execute(statement)
            return result.all()

    def getMessageId(self, channel_id):
        with Session(self.engine) as session:
            statement = select(MsgIds).where(
                MsgIds.channel_id == str(channel_id))
            result = session.execute(statement)
            return result.one_or_none()

    def setMessageId(self, channel_id, message_id):
        with Session(self.engine) as session:
            new_msg = MsgIds(
                channel_id=channel_id,
                message_id=message_id
            )

            session.add(new_msg)
            session.commit()
