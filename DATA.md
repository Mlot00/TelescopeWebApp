# DATA policy

## Cel
Zapewnić powtarzalny, lekki i legalny obieg danych dla zespołu.

## Zasady
1. W repo trzymamy tylko małe dane testowe (`data/sample`) i metadane (`data/datasets.yml`).
2. Właściwe dane DL3 montujemy lokalnie przez volume (Docker) albo ścieżki konfiguracyjne.
3. Nie wrzucamy dużych surowych danych do Git.
4. Każdy dataset w `data/datasets.yml` musi mieć:
   - `id`, `title`, `instrument`, `source`
   - `datastore_path`
   - informację `dl3_index_required`

## Indeksy DL3
Dla datasetów DL3 wymagamy obecności plików indeksu:
- `hdu-index.fits.gz`
- `obs-index.fits.gz`

Jeśli ich brakuje, endpointy API zwracają jasny błąd walidacji.
