import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)