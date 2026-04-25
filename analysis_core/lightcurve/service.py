import pandas as pd

from backend.app.domain.schemas import LightCurveRequest, LightCurveResponse


class LightCurveService:
    def __init__(self, data_loader):
        self.data_loader = data_loader

        self.dataset_id = None
        self.energy_min = None
        self.energy_max = None
        self.time_bin_minutes = None

    def config(self, request: LightCurveRequest):
        if request.e_min_tev <= 0 or request.e_max_tev <= 0:
            raise ValueError("Energy must be > 0")

        if request.e_min_tev >= request.e_max_tev:
            raise ValueError("energy_min must be < energy_max")

        minutes = _parse_time_bin(request.time_bin)

        if minutes <= 0:
            raise ValueError("time_bin must be > 0")

        self.dataset_id = request.dataset_id
        self.energy_min = request.e_min_tev
        self.energy_max = request.e_max_tev
        self.time_bin_minutes = minutes

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
        df = df.set_index("time")

        bin_size = f"{self.time_bin_minutes}min"

        counts = df["energy"].resample(bin_size).count()
        flux = counts / (self.time_bin_minutes * 60)

        return pd.DataFrame({
            "time": counts.index,
            "counts": counts.values,
            "flux": flux.values
        })

    def run(self) -> LightCurveResponse:
        valid, message = self.data_loader.validate_dataset(self.dataset_id)

        if not valid:
            return LightCurveResponse(
                dataset_id=self.dataset_id,
                message=message,
                data={}
            )

        events = self.data_loader.load_lightcurve_events(self.dataset_id)

        filtered = self._filter_energy(events)
        result_df = self._bin_time(filtered)

        data = {
            "time": result_df["time"].astype(str).tolist(),
            "counts": result_df["counts"].tolist(),
            "flux": result_df["flux"].tolist(),
        }

        return LightCurveResponse(
            dataset_id=self.dataset_id,
            message="Light curve generated successfully",
            data=data
        )


def _parse_time_bin(time_bin: str) -> int:
    if time_bin.endswith("d"):
        return int(time_bin[:-1]) * 24 * 60
    if time_bin.endswith("h"):
        return int(time_bin[:-1]) * 60
    if time_bin.endswith("min"):
        return int(time_bin[:-3])

    raise ValueError(f"Unsupported time_bin format: {time_bin}")


def run_lightcurve(request: LightCurveRequest, data_loader) -> LightCurveResponse:
    service = LightCurveService(data_loader)
    service.config(request)
    return service.run()