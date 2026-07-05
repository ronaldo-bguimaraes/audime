import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from abstract.base import Base

# Ensure test environment has required secrets
os.environ.setdefault("JWT_SECRET", "test-secret-not-for-production-use")
os.environ.setdefault("APP_ENV", "development")

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        execution_options={"schema_translate_map": {"raw": None, "core": None, "staging": None, "analytics": None}},
    )

    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
