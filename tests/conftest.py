import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import DB_PATH, init_db

@pytest.fixture(autouse=True)
def setup_db():
    # Use a separate test database
    test_db = "test_links.db"
    import app.database
    original_db = app.database.DB_PATH
    app.database.DB_PATH = test_db
    
    # Initialize fresh DB for each test
    if os.path.exists(test_db):
        os.remove(test_db)
    init_db()
    
    yield
    
    # Cleanup
    if os.path.exists(test_db):
        os.remove(test_db)
    app.database.DB_PATH = original_db

@pytest.fixture
def client():
    return TestClient(app)
