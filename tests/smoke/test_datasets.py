from fastapi.testclient import TestClient

from backend.app.main import app


def test_datasets_list_exists() -> None:
    client = TestClient(app)
    response = client.get("/datasets")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
