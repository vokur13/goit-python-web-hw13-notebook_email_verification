from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


from src.conf.config import settings


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    """
    The get_db function is a context manager that returns the database session.
    It also ensures that the connection to the database is closed after each request.

    :return: A database session, which is used to query the database
    :doc-author: Trelent"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
