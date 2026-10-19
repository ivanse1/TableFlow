from typing import Annotated
from psycopg.errors import UniqueViolation

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db_models import RestaurantTableDB
from dependencies import get_db
from models import (
    RestaurantTable,
    RestaurantTableCreate,
    RestaurantTableUpdate,
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