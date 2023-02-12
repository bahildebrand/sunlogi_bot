from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Stockpiles(Base):
    __tablename__ = "stockpiles"

    stockpile_name: Mapped[str] = mapped_column(primary_key=True)
    depot: Mapped[str]
    code: Mapped[int]

    def __repr__(self) -> str:
        return f"Stockpiles(stockpile_name={self.stockpile_name}, depot={self.depot}, code={self.code})"


class MsgIds(Base):
    __tablename__ = "stockpile_msgs"

    channel_id: Mapped[str] = mapped_column(primary_key=True)
    message_id: Mapped[str]
