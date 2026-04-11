import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

import django
from django.test import Client

django.setup()


def test_datasets_list_exists() -> None:
    client = Client()
    response = client.get("/datasets")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
