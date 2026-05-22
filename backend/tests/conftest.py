import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import Base, get_db
from cache import get_cache, InMemoryCache
import models

from sqlalchemy.pool import StaticPool

# Create test database engine in-memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_cache():
    return InMemoryCache()

@pytest.fixture(scope="function")
def client(db_session, test_cache):
    # Setup dependency overrides
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_cache():
        return test_cache

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache] = override_get_cache
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def override_cron_session_local(monkeypatch):
    import routers.cron
    monkeypatch.setattr(routers.cron, "SessionLocal", TestingSessionLocal)
