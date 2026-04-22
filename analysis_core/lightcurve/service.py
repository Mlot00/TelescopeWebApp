import pandas as pd
from astropy.time import Time
from gammapy.data import DataStore
from typing import Any
from pydantic import BaseModel, Field

from backend.app.domain.schemas import LightCurveRequest, LightCurveResponse


class LightCurveService:
    def __init__(self):
        self.energy_min = None
        self.energy_max = None
        self.time_bin_minutes = None
        self.dl3_path = None

    def config(self, dl3_path: str, energy_min: float, energy_max: float, time_bin_minutes: int):
        if energy_min <= 0 or energy_max <= 0:
            raise ValueError("Energy must be > 0")

        if energy_min >= energy_max:
            raise ValueError("energy_min must be < energy_max")

        if time_bin_minutes <= 0:
            raise ValueError("time_bin_minutes must be > 0")

        self.dl3_path = dl3_path
        self.energy_min = energy_min
        self.energy_max = energy_max
        self.time_bin_minutes = time_bin_minutes

    def _load_events(self):
        datastore = DataStore.from_dir(self.dl3_path)
        observations = datastore.get_observations()

        all_events = []

        for obs in observations:
            events = obs.events
            df = events.table.to_pandas()

            # lepsze niż pd.to_datetime (Gammapy = MJD)
            df["time"] = Time(df["TIME"], format="mjd").datetime
            df["energy"] = df["ENERGY"]

            all_events.append(df[["time", "energy"]])

        if not all_events:
            raise ValueError("No events found")

        return pd.concat(all_events)

    def _filter_energy(self, df: pd.DataFrame):
        filtered = df[
            (df["energy"] >= self.energy_min) &
            (df["energy"] <= self.energy_max)
            ]

        if filtered.empty:
            raise ValueError("No events in selected energy range")

        return filtered

    def _bin_time(self, df: pd.DataFrame):
        df = df.sort_values("time")
        df.set_index("time", inplace=True)

        bin_size = f"{self.time_bin_minutes}min"

        counts = df["energy"].resample(bin_size).count()
        flux = counts / (self.time_bin_minutes * 60)

        return pd.DataFrame({
            "time": counts.index,
            "counts": counts.values,
            "flux": flux.values
        })

    def run(self):
        if not all([self.dl3_path, self.energy_min, self.energy_max, self.time_bin_minutes]):
            raise ValueError("Call config() first")

        events = self._load_events()
        filtered = self._filter_energy(events)
        return self._bin_time(filtered)


def _parse_time_bin(time_bin: str) -> int:
    if time_bin.endswith("d"):
        return int(time_bin[:-1]) * 24 * 60
    if time_bin.endswith("h"):
        return int(time_bin[:-1]) * 60
    if time_bin.endswith("min"):
        return int(time_bin[:-3])

    raise ValueError(f"Unsupported time_bin format: {time_bin}")


def run_lightcurve(request: LightCurveRequest) -> LightCurveResponse:
    service = LightCurveService()

    service.config(
        dl3_path=request.dataset_id,
        energy_min=request.e_min_tev,
        energy_max=request.e_max_tev,
        time_bin_minutes=_parse_time_bin(request.time_bin)
    )

    result_df = service.run()

    data = {
        "time": result_df["time"].astype(str).tolist(),
        "counts": result_df["counts"].tolist(),
        "flux": result_df["flux"].tolist(),
    }

    return LightCurveResponse(
        dataset_id=request.dataset_id,
        message="Light curve generated successfully",
        data=data
    )
