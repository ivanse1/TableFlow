from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class RestaurantTable(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: int
    capacity: int = Field(gt=0)
    x: float
    y: float

class RestaurantTableCreate(BaseModel):
    number: int = Field(gt=0)
    capacity: int = Field(gt=0)
    x: float
    y: float

class RestaurantTableUpdate(BaseModel):
    number: int | None = Field(default=None, gt=0)
    capacity: int | None = Field(default=None, gt=0)
    x: float | None = None
    y: float | None = None

class ReservationResponse(BaseModel):
    id: int
    guest_name: str
    guest_count: int
    starts_at: datetime
    ends_at: datetime
    table_ids: list[int]    

class ReservationCreate(BaseModel):
    guest_name: str = Field(min_length=1, max_length=100)
    guest_count: int = Field(gt=0)
    starts_at: datetime
    ends_at: datetime
    table_ids: list[int] = Field(default_factory=list)    

class ReservationUpdate(BaseModel):
    guest_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    guest_count: int | None = Field(default=None, gt=0)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    table_ids: list[int] | None = None