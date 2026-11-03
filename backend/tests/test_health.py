from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/health")

    # Verify HTTP 200 status code
    assert response.status_code == 200

    # Verify response is valid JSON
    data = response.json()
    assert isinstance(data, dict)

    # Verify required fields exist
    assert "name" in data
    assert "status" in data
    assert "version" in data

    # Verify content and healthy status
    assert data["name"] == settings.PROJECT_NAME
    assert data["status"] == "healthy"
    assert data["version"] == settings.VERSION
