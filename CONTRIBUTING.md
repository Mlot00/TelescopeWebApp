# Contributing

## Workflow
1. Twórz branch od `main`.
2. Zmiany przez Pull Request.
3. Wymagane review oraz zielone CI.

## Konwencje
- Python 3.11+
- format/lint: `ruff`
- API kontrakty przez Pydantic
- brak hardcoded ścieżek do danych produkcyjnych

## Podział odpowiedzialności
- Osoba #1: platforma, data layer, CI/Docker, integracja
- Osoby #2-#5: logika modułów analitycznych + widoki
- Osoba #6: testy E2E i wieloużytkownikowość
