"""Detect old migration chain and stamp DB to current baseline."""
import sys
sys.path.insert(0, ".")

from sqlalchemy import create_engine, inspect, text
from sqlalchemy import URL
from app.core.config import settings

TARGET = "ebb53dc90cdf"

url = URL.create(
    drivername="postgresql+psycopg",
    username=settings.db_postgres_user,
    password=settings.db_postgres_password,
    host=settings.db_postgres_host,
    database=settings.db_postgres_name,
    port=settings.db_postgres_port,
)
eng = create_engine(url.render_as_string(hide_password=False))
with eng.connect() as c:
    tables = inspect(c).get_table_names(schema="core")
    if "usuario" in tables:
        c.execute(text(f"UPDATE core.alembic_version SET version_num = '{TARGET}'"))
        c.commit()
        print("yes")
    else:
        print("no")
eng.dispose()
