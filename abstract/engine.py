import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

url = sa.URL.create(
    drivername="postgresql+psycopg",
    username=settings.db_postgres_user,
    password=settings.db_postgres_password,
    host=settings.db_postgres_host,
    database=settings.db_postgres_name,
    port=settings.db_postgres_port,
)

engine = sa.create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
