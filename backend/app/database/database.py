# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL (SQLite file database)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app_data.db"

# 1. Create Engine (This is what main.py is trying to import)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 2. Create SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create Base class for ORM models
Base = declarative_base()

# 4. Dependency to get DB session in routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        