from fastapi import Depends, FastAPI

from .api.routes import datasets, health, lightcurve, skymap, spectrum, theta2
from .core.config import Settings, get_settings
from .core.logging import configure_logging
from .domain.data_loader import DataLoader
from .domain.dataset_registry import DatasetRegistry

app = FastAPI(title="TelescopeWebApp API", version="0.1.0")


def get_registry(settings: Settings = Depends(get_settings)) -> DatasetRegistry:
    return DatasetRegistry(settings.datasets_file)


def get_data_loader(
    settings: Settings = Depends(get_settings),
    registry: DatasetRegistry = Depends(get_registry),
) -> DataLoader:
    return DataLoader(data_root=settings.data_dir, registry=registry)


@app.on_event("startup")
def on_startup() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)


app.include_router(health.router)
app.include_router(datasets.router)
app.include_router(theta2.router)
app.include_router(skymap.router)
app.include_router(spectrum.router)
app.include_router(lightcurve.router)
