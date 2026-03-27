from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_datasets_route_does_not_import_main_dependency_providers() -> None:
    datasets_route = REPO_ROOT / "backend/app/api/routes/datasets.py"
    content = datasets_route.read_text(encoding="utf-8")

    assert "from ...main import get_data_loader, get_registry" not in content
    assert "from ...dependencies import get_data_loader, get_registry" in content


def test_dependency_providers_live_in_dependencies_module() -> None:
    dependencies_module = REPO_ROOT / "backend/app/dependencies.py"
    content = dependencies_module.read_text(encoding="utf-8")

    assert "def get_registry" in content
    assert "def get_data_loader" in content
