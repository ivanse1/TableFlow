from fastapi import FastAPI
from models import RestaurantTable

app = FastAPI()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


tables = [
    RestaurantTable(
        id=1,
        number=1,
        capacity=4,
        x=100.0,
        y=150.0,
    ),
    RestaurantTable(
        id=2,
        number=2,
        capacity=6,
        x=300.0,
        y=150.0,
    ),
    RestaurantTable(
        id=3,
        number=3,
        capacity=2,
        x=500.0,
        y=150.0,
    ),
]


@app.get("/api/tables", response_model=list[RestaurantTable])
def get_tables():
    return tables