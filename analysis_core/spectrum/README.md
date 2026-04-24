# Energy Spectrum Module

## This module generates an energy spectrum from DL3 event data using logarithmic binning.

The module loads events from a configured dataset via `DataLoader`, filters them by
energy range and instruments, and produces a histogram with logarithmic energy bins.

---

## Dependencies

- numpy
- astropy
- DataLoader
- DatasetRegistry
- SpectrumRequest / SpectrumResponse schemas

---

## Initialization
`module = EnergySpectrumModule(data_loader)`

## Configuration
```
module.config(SpectrumRequest(
    dataset_id="hess-dl3-dr1",
    e_min_tev=0.05,
    e_max_tev=20,
    n_bins=20,
    instruments=["HESS"]
))
```

## Parameters:
* `dataset_id` — dataset identifier from datasets.yml
* `e_min_tev` — minimum energy (TeV)
* `e_max_tev` — maximum energy (TeV)
* `n_bins` — number of logarithmic bins
* `instruments` — optional instrument filter

## Run method:
`result = module.run()`

The module:
1. validates dataset
2. loads DL3 events
3. filters by instrument
4. filters by energy range
5. applies logarithmic binning
6. returns histogram


## Example output:
```json
{
  "dataset_id": "hess-dl3-dr1",
  "message": "Energy spectrum generated",
  "data": {
    "bin_edges": [...],
    "counts": [...]
  }
}
```

## Logarithmic Binning
Energy bins are computed using:

```
np.logspace(
    log10(e_min),
    log10(e_max),
    n_bins + 1
)
```

---

## Example

```
module = EnergySpectrumModule(data_loader)

module.config(
    SpectrumRequest(
        dataset_id="hess-dl3-dr1",
        e_min_tev=0.05,
        e_max_tev=20,
        n_bins=20
    )
)

result = module.run()
```