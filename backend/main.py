from typing import Annotated
from psycopg.errors import UniqueViolation
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_models import RestaurantTableDB, ReservationDB
from dependencies import get_db
from models import (
    RestaurantTable,
    RestaurantTableCreate,
    RestaurantTableUpdate,
    ReservationResponse,
    ReservationCreate,
    ReservationUpdate
)

app = FastAPI()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/tables", response_model=list[RestaurantTable])
def get_tables(
    session: Annotated[Session, Depends(get_db)]
):
    statement = select(RestaurantTableDB).order_by(
        RestaurantTableDB.number
    )

    tables = session.scalars(statement).all()

    return tables


@app.post(
    "/api/tables",
    response_model=RestaurantTable,
    status_code=201,
)
def create_table(
    table_data: RestaurantTableCreate,
    session: Annotated[Session, Depends(get_db)],
):
    new_table = RestaurantTableDB(
        number=table_data.number,
        capacity=table_data.capacity,
        x=table_data.x,
        y=table_data.y,
    )

    session.add(new_table)

    try:
        session.commit()

    except IntegrityError as error:
        session.rollback()

        if isinstance(error.orig, UniqueViolation):
            raise HTTPException(
                status_code=409,
                detail="A table with this number already exists.",
            ) from error

        raise

    session.refresh(new_table)

    return new_table


@app.patch(
    "/api/tables/{table_id}",
    response_model=RestaurantTable,
)
def update_table(
    table_id: int,
    table_data: RestaurantTableUpdate,
    session: Annotated[Session, Depends(get_db)],
):
    table = session.get(RestaurantTableDB, table_id)

    if table is None:
        raise HTTPException(
            status_code=404,
            detail="Table not found.",
        )

    update_data = table_data.model_dump(exclude_unset=True)

    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=422,
            detail="Table fields cannot be null.",
        )

    for field, value in update_data.items():
        setattr(table, field, value)

    try:
        session.commit()

    except IntegrityError as error:
        session.rollback()

        if isinstance(error.orig, UniqueViolation):
            raise HTTPException(
                status_code=409,
                detail="A table with this number already exists.",
            ) from error

        raise

    session.refresh(table)

    return table


@app.delete("/api/tables/{table_id}", status_code=204)
def delete_table(
    table_id: int,
    session: Annotated[Session, Depends(get_db)],
):
    table = session.get(RestaurantTableDB, table_id)

    if table is None:
        raise HTTPException(
            status_code=404,
            detail="Table not found.",
        )

    session.delete(table)
    session.commit()


@app.get(
    "/api/reservations",
    response_model=list[ReservationResponse],
)
def get_reservations(
    session: Annotated[Session, Depends(get_db)],
):
    statement = select(ReservationDB).order_by(
        ReservationDB.starts_at
    )

    reservations = session.scalars(statement).all()

    result = []

    for reservation in reservations:
        result.append(
            ReservationResponse(
                id=reservation.id,
                guest_name=reservation.guest_name,
                guest_count=reservation.guest_count,
                starts_at=reservation.starts_at,
                ends_at=reservation.ends_at,
                table_ids=[
                    table.id
                    for table in reservation.tables
                ],
            )
        )

    return result    


@app.post(
    "/api/reservations",
    response_model=ReservationResponse,
    status_code=201,
)
def create_reservation(
    reservation_data: ReservationCreate,
    session: Annotated[Session, Depends(get_db)],
):
    if reservation_data.ends_at <= reservation_data.starts_at:
        raise HTTPException(
            status_code=422,
            detail="Reservation end time must be after start time.",
        )

    if len(reservation_data.table_ids) != len(set(reservation_data.table_ids)):
        raise HTTPException(
            status_code=422,
            detail="Duplicate table IDs are not allowed.",
        )

    tables = []

    if reservation_data.table_ids:
        statement = (
            select(RestaurantTableDB)
            .where(
                RestaurantTableDB.id.in_(reservation_data.table_ids)
            )
            .order_by(RestaurantTableDB.id)
            .with_for_update()
        )

        tables = session.scalars(statement).all()

        if len(tables) != len(reservation_data.table_ids):
            raise HTTPException(
                status_code=404,
                detail="One or more tables were not found.",
            )

        if len(tables) != len(reservation_data.table_ids):
            raise HTTPException(
                status_code=404,
                detail="One or more tables were not found.",
            )

    conflict = find_reservation_conflict(
        session=session,
        table_ids=reservation_data.table_ids,
        starts_at=reservation_data.starts_at,
        ends_at=reservation_data.ends_at,
    )

    if conflict is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Table conflict with reservation {conflict.id}."
            ),
        )

    reservation = ReservationDB(
        guest_name=reservation_data.guest_name,
        guest_count=reservation_data.guest_count,
        starts_at=reservation_data.starts_at,
        ends_at=reservation_data.ends_at,
    )

    reservation.tables = tables

    session.add(reservation)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    session.refresh(reservation)

    return ReservationResponse(
        id=reservation.id,
        guest_name=reservation.guest_name,
        guest_count=reservation.guest_count,
        starts_at=reservation.starts_at,
        ends_at=reservation.ends_at,
        table_ids=[table.id for table in tables],
    )


@app.patch(
    "/api/reservations/{reservation_id}",
    response_model=ReservationResponse,
)
def update_reservation(
    reservation_id: int,
    update_data: ReservationUpdate,
    session: Annotated[Session, Depends(get_db)],
):
    reservation = session.get(ReservationDB, reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found.",
        )

    changes = update_data.model_dump(exclude_unset=True)

    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=422,
            detail="Null values are not allowed.",
        )

    new_start = changes.get("starts_at", reservation.starts_at)
    new_end = changes.get("ends_at", reservation.ends_at)

    if new_end <= new_start:
        raise HTTPException(
            status_code=422,
            detail="Reservation end time must be after start time.",
        )

    if "table_ids" in changes:
        requested_ids = changes["table_ids"]
    else:
        requested_ids = [table.id for table in reservation.tables]

    if len(requested_ids) != len(set(requested_ids)):
        raise HTTPException(
            status_code=422,
            detail="Duplicate table IDs are not allowed.",
        )

    tables = []

    if requested_ids:
        statement = (
            select(RestaurantTableDB)
            .where(RestaurantTableDB.id.in_(requested_ids))
            .order_by(RestaurantTableDB.id)
            .with_for_update()
        )

        tables = session.scalars(statement).all()

        if len(tables) != len(requested_ids):
            raise HTTPException(
                status_code=404,
                detail="One or more tables were not found.",
            )

    conflict = find_reservation_conflict(
        session=session,
        table_ids=requested_ids,
        starts_at=new_start,
        ends_at=new_end,
        exclude_reservation_id=reservation_id,
    )

    if conflict is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Table conflict with reservation {conflict.id}.",
        )

    for field in (
        "guest_name",
        "guest_count",
        "starts_at",
        "ends_at",
    ):
        if field in changes:
            setattr(reservation, field, changes[field])

    if "table_ids" in changes:
        reservation.tables = tables

    session.commit()
    session.refresh(reservation)

    return ReservationResponse(
        id=reservation.id,
        guest_name=reservation.guest_name,
        guest_count=reservation.guest_count,
        starts_at=reservation.starts_at,
        ends_at=reservation.ends_at,
        table_ids=[table.id for table in reservation.tables],
    )


@app.delete(
    "/api/reservations/{reservation_id}",
    status_code=204,
)
def delete_reservation(
    reservation_id: int,
    session: Annotated[Session, Depends(get_db)],
):
    reservation = session.get(ReservationDB, reservation_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail="Reservation not found.",
        )

    session.delete(reservation)
    session.commit()



def find_reservation_conflict(
    session: Session,
    table_ids: list[int],
    starts_at: datetime,
    ends_at: datetime,
    exclude_reservation_id: int | None = None,
):
    if not table_ids:
        return None

    statement = (
        select(ReservationDB)
        .join(ReservationDB.tables)
        .where(
            RestaurantTableDB.id.in_(table_ids),
            ReservationDB.starts_at < ends_at,
            ReservationDB.ends_at > starts_at,
        )
    )

    if exclude_reservation_id is not None:
        statement = statement.where(
            ReservationDB.id != exclude_reservation_id
        )

    return session.scalars(statement.limit(1)).first()