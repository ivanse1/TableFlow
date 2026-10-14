from pydantic import BaseModel, Field


class RestaurantTable(BaseModel):
    id: int
    number: int
    capacity: int = Field(gt=0)
    x: float
    y: float