# TelescopeWebApp – Architecture

## High-level
Monorepo z trzema warstwami:
1. `backend/` – Django, kontrakty API, walidacja datasetów
2. `frontend/` – Streamlit UI dla modułów analizy
3. `analysis_core/` – wspólna logika analityczna (modułowa, bez kodu UI)

## Moduły funkcjonalne
- Theta² (`analysis_core/theta2`)
- Sky map (`analysis_core/skymap`)
- Spectrum (`analysis_core/spectrum`)
- Light curve (`analysis_core/lightcurve`)

## Kontrakty API
Implementacja endpointów: `backend/app/views.py` (handlery) + `backend/app/urls.py` (routing).

- `GET /health`
- `GET /datasets`
- `GET /datasets/{id}/observations`
- `POST /theta2`
- `POST /skymap`
- `POST /spectrum`
- `POST /lightcurve`

## Rola osoby #1 (platform/DevOps)
- utrzymanie architektury i konwencji repo
- wspólna warstwa danych (`dataset_registry`, `data_loader`, `DATA.md`)
- konteneryzacja (`docker/`, `compose.yaml`)
- CI (`.github/workflows/ci.yml`)
- kontrakty API + stuby dla osób #2–#5

## Integracja zespołu
Każdy członek rozwija własny moduł w `analysis_core/*` i dedykowaną stronę w `frontend/pages/*`.


## Szczegółowy workflow zespołu
Operacyjny podział zadań osób #2–#6 i checklisty PR: `TEAM_WORKFLOW.md`.
