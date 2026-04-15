# TEAM_WORKFLOW.md

Dokument operacyjny dla zespołu 6-osobowego (TelescopeWebApp).

## Cel
Ustalić **kto robi co**, **gdzie trafia kod**, **jakie są wspólne kontrakty** i jak uniknąć konfliktów między modułami.

---

## 1) Role osób #2–#6 (bez osoby #1)

> Założenie: osoba #1 dostarcza platformę (architektura, CI, data-layer, Docker, kontrakty API).

### Osoba #2 — Theta² (moduł + UI)
**Zakres funkcjonalny**
- Implementacja analizy theta² na bazie kontraktu `POST /theta2`.
- Walidacja parametrów wejściowych (zakres energii, selection obserwacji, binning theta²).
- Zwracanie danych gotowych do wykresu (bin edges, counts ON/OFF, excess/significance).

**Gdzie wrzucać pliki**
- Logika: `analysis_core/theta2/service.py`
- API route (jeśli potrzebne rozszerzenie request/response): `backend/app/api/routes/theta2.py`
- Schemy: `backend/app/domain/schemas.py`
- Widok UI: `frontend/pages/1_theta2.py`
- Testy: `tests/unit/` + `tests/smoke/`

**Definition of Done**
- Endpoint zwraca poprawne dane dla sample dataset.
- UI renderuje wykres i obsługuje błędy walidacji.
- Smoke test przechodzi w CI.

---

### Osoba #3 — Sky map (moduł + UI)
**Zakres funkcjonalny**
- Implementacja mapy nieba na bazie kontraktu `POST /skymap`.
- Obsługa parametrów przestrzennych (ROI, smoothing, binsz, frame/projection).
- Generowanie warstw (counts/background/excess/significance) jako dane do wizualizacji.

**Gdzie wrzucać pliki**
- Logika: `analysis_core/skymap/service.py`
- API: `backend/app/api/routes/skymap.py`
- Schemy: `backend/app/domain/schemas.py`
- UI: `frontend/pages/2_skymap.py`
- Testy: `tests/unit/` + `tests/smoke/`

**Definition of Done**
- Endpoint zwraca strukturę mapy możliwą do renderu.
- UI umożliwia zmianę parametrów i odświeżanie mapy.
- Smoke test dla `POST /skymap` przechodzi.

---

### Osoba #4 — Spectrum (moduł + UI)
**Zakres funkcjonalny**
- Implementacja widma energetycznego (`POST /spectrum`).
- Obsługa binowania, zakresu energii oraz wyboru instrumentów.
- Zwracanie punktów widma + błędy stat/syst (jeżeli dostępne).

**Gdzie wrzucać pliki**
- Logika: `analysis_core/spectrum/service.py`
- API: `backend/app/api/routes/spectrum.py`
- Schemy: `backend/app/domain/schemas.py`
- UI: `frontend/pages/3_spectrum.py`
- Testy: `tests/unit/` + `tests/smoke/`

**Definition of Done**
- Można policzyć widmo dla sample dataset.
- UI pozwala sterować binningiem/zakresem i pokazać wykres.
- Smoke test przechodzi w CI.

---

### Osoba #5 — Light curve (moduł + UI)
**Zakres funkcjonalny**
- Implementacja krzywej blasku (`POST /lightcurve`).
- Obsługa wyboru zakresu energii i binowania czasowego.
- Zwracanie flux vs time + niepewności.

**Gdzie wrzucać pliki**
- Logika: `analysis_core/lightcurve/service.py`
- API: `backend/app/api/routes/lightcurve.py`
- Schemy: `backend/app/domain/schemas.py`
- UI: `frontend/pages/4_lightcurve.py`
- Testy: `tests/unit/` + `tests/smoke/`

**Definition of Done**
- Endpoint zwraca serię czasową poprawną strukturalnie.
- UI poprawnie renderuje i filtruje zakresy.
- Smoke test przechodzi w CI.

---

### Osoba #6 — Testy E2E + wieloużytkownikowość
**Zakres funkcjonalny**
- Testy end-to-end przepływów użytkownika przez API/UI.
- Testy równoległego użycia aplikacji (concurrency/load): wielu użytkowników, kilka endpointów jednocześnie.
- Raport wydajności i stabilności.

**Gdzie wrzucać pliki**
- Testy smoke/integration: `tests/smoke/`, `tests/integration/`
- Testy obciążeniowe: `tests/load/`
- Fixtures/dane pomocnicze: `data/sample/` (małe tylko)
- Dokumentacja wyniku testów: `README.md` lub osobny raport w `tests/load/`

**Definition of Done**
- Zautomatyzowany scenariusz min. 2–3 równoległych użytkowników.
- Raport: czasy odpowiedzi, odsetek błędów, punkty krytyczne.
- Testy uruchamialne lokalnie i (w uproszczonej formie) w CI.

---

## 2) Co jest wspólne dla wszystkich

### Wspólne kontrakty i struktury
- API contracts: `backend/app/api/routes/*.py`
- Schemy wejścia/wyjścia: `backend/app/domain/schemas.py`
- Dane i dataset registry: `data/datasets.yml`, `backend/app/domain/dataset_registry.py`
- Loader i walidacja danych: `backend/app/domain/data_loader.py`

### Wspólne zasady techniczne
- Brak hardcoded pathów do danych produkcyjnych.
- Korzystanie z datasetów zarejestrowanych w `data/datasets.yml`.
- Każda nowa funkcja ma test (minimum smoke lub unit).
- Kod przechodzi `ruff` i `pytest`.
- PR-y tylko na branchach feature, merge przez review.

### Wspólne narzędzia
- Backend: Django + Pydantic
- Frontend: Streamlit
- Core analityczny: Python (`analysis_core`)
- Kontenery: Docker + Compose
- CI: GitHub Actions

---

## 3) Kolejność integracji (zalecana)
1. Osoby #2–#5 implementują logikę modułów na stubach endpointów.
2. Osoba #6 równolegle buduje smoke/integration harness.
3. Integracja po kolei: theta² → skymap → spectrum → lightcurve.
4. Na końcu testy równoległe + finalna stabilizacja release.

---

## 4) Checklist PR dla osób #2–#6
- [ ] Kod w odpowiednim katalogu modułu.
- [ ] Użyte wspólne schemy i kontrakty API.
- [ ] Brak twardych ścieżek do danych.
- [ ] Dodane/uzupełnione testy.
- [ ] `ruff check .` oraz `pytest` przechodzą lokalnie.
- [ ] Opis wpływu na UI/API w treści PR.
