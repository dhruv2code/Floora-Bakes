import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.core.database import Base, get_db
from app.models.sales import Sales, UploadBatch


@pytest.fixture
def database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def api_client(database):
    def override_get_db():
        yield database

    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as client:
        yield client
    main.app.dependency_overrides.clear()
