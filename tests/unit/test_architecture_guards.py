from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_backend_views_are_django_based() -> None:
    views_file = REPO_ROOT / "backend/app/views.py"
    content = views_file.read_text(encoding="utf-8")

    assert "from django.http" in content
    assert "from fastapi" not in content


def test_backend_main_fastapi_entrypoint_removed() -> None:
    legacy_main = REPO_ROOT / "backend/app/main.py"
    assert not legacy_main.exists()
