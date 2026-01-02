# MarketView Microservices (Starter)

This scaffold refactors the Flask S&P 500 sentiment app into microservices with a FastAPI gateway and a React front-end.

## Services
- **auth_service** (Flask + JWT): registration/login/verify
- **data_service** (Flask): companies, sentiments, ingestion
- **viz_service** (Flask): top5/low5 treemaps
- **gateway** (FastAPI): API gateway & Swagger (/docs)
- **frontend** (React+Vite): SPA consuming gateway APIs
- **db** (PostgreSQL 16): schema with indexes + pg_stat_statements

## Quickstart
```bash
cp .env.example .env
docker compose up --build
```
- Gateway: http://localhost:8080/docs
- Frontend: http://localhost:5173
- Auth: POST /api/auth/register and /api/auth/login → Bearer token
- Use the Bearer token for protected routes

## Database
Schema is initialized from `db/schema.sql`. Includes normalized tables, indexes, FTS on headlines, and a materialized view.

## Testing
- Python: see `auth_service/tests/` and `gateway/tests/`. Use `pytest` or `python -m unittest` variants.
- Frontend: add Jest + React Testing Library as needed.

## Next Steps
- Replace `data_service` ingestion with your real scraping + VADER pipeline
- Add pagination/filters to `/sentiments`
- Schedule periodic refresh (cron/Celery) for ingest
- Harden security (rate limits, HTTPS, secrets management)
``` 
