import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

import django
from django.test import Client

django.setup()


def test_malformed_json_returns_400() -> None:
    client = Client()
    response = client.post(
        "/theta2",
        data="{not-valid-json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "Malformed JSON body" in response.content.decode("utf-8")
