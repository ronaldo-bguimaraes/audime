import os
import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker, declarative_base


url = sa.URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_POSTGRES_USER"],
    password=os.environ["DB_POSTGRES_PASSWORD"],
    host=os.environ["DB_POSTGRES_HOST"],
    database=os.environ["DB_POSTGRES_NAME"],
    port=int(os.getenv("DB_POSTGRES_PORT", "5432")),
)


engine = sa.create_engine(url)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
