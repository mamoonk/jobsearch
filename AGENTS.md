# JobSearch AI — Agent Development Guide

## Architecture Overview

Monorepo with two primary services:
- **Backend**: FastAPI (Python 3.11+) — API, services, AI pipeline
- **Frontend**: Next.js 14 (App Router) — UI with Tailwind + shadcn/ui

## Key Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### Docker (full stack)
```bash
docker compose up -d
```

### Database Migrations
```bash
cd backend
alembic upgrade head
```

## External API Keys Required

Set in `.env`:
- `OPENAI_API_KEY` — Resume parsing, embedding, cover letters, interview prep
- `GEOAPIFY_API_KEY` — Location autocomplete/geocoding
- `THEIRSTACK_API_KEY` — Primary job feed
- `SERPAPI_API_KEY` — Fallback Google Jobs feed

## Code Conventions

- Python: Use Pydantic v2 for schemas, SQLAlchemy 2.0 async-style for models
- TypeScript: Strict mode, use `@/` path alias for imports
- UI: Prefer shadcn/ui components, use `cn()` utility for class merging
- API routes: Prefix with `/api/v1/`, return JSON with snake_case keys
- Do NOT add comments to code unless explaining non-obvious logic
- Keep frontend pages as "use client" when they use hooks or state

## Project Structure
```
jobsearch/
├── backend/app/
│   ├── api/v1/          # Route handlers
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic models
│   ├── services/        # Business logic
│   ├── middleware/       # Auth, rate-limit, PII
│   └── utils/           # Embedding helpers
├── frontend/src/
│   ├── app/             # Next.js pages
│   ├── components/      # React components
│   └── lib/             # API client, utils
└── docker-compose.yml
```
