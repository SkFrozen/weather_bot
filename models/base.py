from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine("sqlite:///db.sqlite")
Base = declarative_base()
