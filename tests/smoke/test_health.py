import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

import django
from django.test import Client

django.setup()


def test_health_ok() -> None:
    client = Client()
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
