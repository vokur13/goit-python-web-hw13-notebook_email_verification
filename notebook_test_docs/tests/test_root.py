from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    response = client.get('/')
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["massage"] == "FastAPI Workbook"
