from sqlalchemy import Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RestaurantTableDB(Base):
    __tablename__ = "restaurant_tables"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    x: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    y: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )