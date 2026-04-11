# TelescopeWebApp

Aplikacja webowa do analizy danych z teleskopów czerenkowskich (projekt 6-osobowy).

## Co zawiera ten commit (zakres osoby #1)
- Szkielet monorepo (`backend`, `frontend`, `analysis_core`, `tests`)
- Kontrakty API (Django) dla:
  - theta²
  - sky map
  - spectrum
  - light curve
- Wspólna warstwa danych:
  - `data/datasets.yml`
  - `backend/app/domain/dataset_registry.py`
  - `backend/app/domain/data_loader.py`
- Podstawowa konteneryzacja:
  - `docker/Dockerfile.backend`
  - `docker/Dockerfile.frontend`
  - `compose.yaml`
- CI (lint + smoke + build obrazów): `.github/workflows/ci.yml`
- Dokumentacja projektu: `ARCHITECTURE.md`, `DATA.md`, `CONTRIBUTING.md`

## Szybki start (lokalnie)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

W osobnym terminalu:
```bash
streamlit run frontend/Home.py
```

## Szybki start (Docker)
```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- UI: http://localhost:8501

## Podział pracy zespołu
- Osoba 1: platforma/architektura/devops/data-loader (to repo setup)
- Osoba 2: theta² module + UI
- Osoba 3: sky map module + UI
- Osoba 4: spectrum module + UI
- Osoba 5: light curve module + UI
- Osoba 6: testy E2E i wieloużytkownikowe
