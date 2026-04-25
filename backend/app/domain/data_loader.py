from pathlib import Path

import pandas as pd
from astropy.io import fits
from astropy import units as u
from astropy.time import Time
from gammapy.data import DataStore

from .dataset_registry import DatasetRegistry


class DataLoader:
    def __init__(self, data_root: Path, registry: DatasetRegistry):
        self.data_root = data_root
        self.registry = registry

    def get_dataset_path(self, dataset_id: str) -> Path:
        dataset = self.registry.get_dataset(dataset_id)
        return self.data_root / dataset.datastore_path

    def validate_dataset(self, dataset_id: str) -> tuple[bool, str]:
        dataset = self.registry.get_dataset(dataset_id)
        dataset_path = self.get_dataset_path(dataset_id)

        if not dataset_path.exists():
            return False, f"Dataset path does not exist: {dataset_path}"

        if dataset.dl3_index_required:
            hdu = dataset_path / "hdu-index.fits.gz"
            obs = dataset_path / "obs-index.fits.gz"
            if not hdu.exists() or not obs.exists():
                return (
                    False,
                    "Missing DL3 index files (hdu-index.fits.gz / obs-index.fits.gz).",
                )

        return True, "Dataset is valid"

    def load_events(self, dataset_id: str):
        dataset = self.registry.get_dataset(dataset_id)
        dataset_path = self.get_dataset_path(dataset_id)

        events = []

        for file in dataset_path.rglob("*.fits.gz"):
            with fits.open(file) as hdul:

                if "EVENTS" not in hdul:
                    continue

                table = hdul["EVENTS"].data
                header = hdul["EVENTS"].header

                energy_unit = header.get("TUNIT5", "TeV")

                for row in table:
                    energy = row["ENERGY"]
                    energy = (energy * u.Unit(energy_unit)).to(u.TeV).value
                    events.append(
                        {
                            "energy": float(energy),
                            "instrument": dataset.instrument,
                        }
                    )

        return events

    def load_lightcurve_events(self, dataset_id: str) -> pd.DataFrame:
        dataset_path = self.get_dataset_path(dataset_id)

        datastore = DataStore.from_dir(dataset_path)
        observations = datastore.get_observations()

        all_events = []

        for obs in observations:
            events = obs.events
            df = events.table.to_pandas()

            import numpy as np

            if "TIME" not in df.columns or "ENERGY" not in df.columns:
                continue

            time_col = df["TIME"]

            # 🔥 KLUCZOWY FIX
            if np.issubdtype(time_col.dtype, np.number):
                df["time"] = Time(time_col, format="mjd").datetime
            else:
                df["time"] = pd.to_datetime(time_col)

            df["energy"] = df["ENERGY"]

            all_events.append(df[["time", "energy"]])

        if not all_events:
            raise ValueError("No events found")

        return pd.concat(all_events)