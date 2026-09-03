# PlantPulse

[![CI](https://github.com/Akhilesh-Vangala/plantpulse/actions/workflows/ci.yml/badge.svg)](https://github.com/Akhilesh-Vangala/plantpulse/actions/workflows/ci.yml)

S&OP exception desk for a two-plant lens network. Each row is a detector with a dollar impact and one recommended action. The queue is sorted by dollars, not by raw forecast error.

## Seeded week (seed 42, week 12)

| Shock | Where | Trigger |
|---|---|---|
| Toric demand +25% | Dallas, weeks 8–12 | Cover under 2 weeks; 8-week bias > 12% |
| Overtime | Fort Worth | Hours used = 114% of the 80-hour cap |
| Scrap spike | Singapore Toric | Scrap rate 2.1× the 8.5% family baseline |

## Stack

Python 3.13, FastAPI, SQLAlchemy 2, PostgreSQL. React 18, TypeScript, Vite. Ports: UI 3009, API 8009, Postgres 5439.

## Quick start

```bash
git clone https://github.com/Akhilesh-Vangala/plantpulse.git
cd plantpulse
cp .env.example .env
docker compose up --build
```

Open http://localhost:3009 — `planner@plantpulse.example.com` / `planner-password`.

```bash
python3.13 -m venv .venv
./.venv/bin/python -m pip install -r backend/requirements.txt
cd backend && ../.venv/bin/python -m pytest -q
```

## License

MIT. See [LICENSE](LICENSE).
