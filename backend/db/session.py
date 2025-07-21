import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# The connect_args are specific to SQLite. For PostgreSQL, they are not needed.
engine = create_engine(DATABASE_URL, echo=True)

# For PostgreSQL, you might want to use a connection pool
# engine = create_engine(
#     DATABASE_URL, pool_size=10, max_overflow=20
# )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
