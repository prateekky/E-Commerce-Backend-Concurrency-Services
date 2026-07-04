# from fastapi.testclient import TestClient

# from app.main import app


# client = TestClient(app)
def test_root_status(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["health"] == "healthy"
