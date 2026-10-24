from sqlalchemy import Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


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

    reservations: Mapped[list["ReservationDB"]] = relationship(
        secondary="reservation_tables",
        back_populates="tables",
    )


class ReservationDB(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    guest_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    guest_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )    

    tables: Mapped[list["RestaurantTableDB"]] = relationship(
        secondary="reservation_tables",
        back_populates="reservations",
    )


class ReservationTableDB(Base):
    __tablename__ = "reservation_tables"

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"),
        primary_key=True,
    )

    table_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant_tables.id"),
        primary_key=True,
    )