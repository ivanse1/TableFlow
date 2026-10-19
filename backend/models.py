from pydantic import BaseModel, ConfigDict, Field


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