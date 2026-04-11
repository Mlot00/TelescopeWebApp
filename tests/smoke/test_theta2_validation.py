import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

import django
from django.test import Client

django.setup()


def test_theta2_requires_existing_dataset() -> None:
    client = Client()
    response = client.post(
        "/theta2",
        data="{\"dataset_id\":\"does-not-exist\"}",
        content_type="application/json",
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
