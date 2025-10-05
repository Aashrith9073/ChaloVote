from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # Import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# For local development, we use a simple SQLite database.
# For production on a platform like Vercel, you'd use a cloud database like PostgreSQL.
#SQLALCHEMY_DATABASE_URL = "sqlite:///./chalovote.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


#engine = create_engine(
#    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
#)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()