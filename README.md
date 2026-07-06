# JobSearch AI

> Global job search, ATS alignment scoring, and AI-powered interview preparation.

[![Python](https://img.shields.io/badge/python-3.12-3776AB?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://postgresql.org)
[![pgvector](https://img.shields.io/badge/pgvector-0.3.6-316192?logo=postgresql)](https://github.com/pgvector/pgvector)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen)](#testing)

---

## Architecture

```
                         ┌──────────────────────┐
                         │     Frontend          │
                         │  Next.js 14 (App Rtr) │
                         │  Tailwind + shadcn/ui │
                         │  localhost:3000        │
                         └──────────┬───────────┘
                                    │  /api/* rewrites to backend
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Backend (FastAPI)                            │
│                     localhost:8000 /api/v1/*                        │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────────┐  │
│  │  Auth    │  │ Resumes  │  │  Jobs    │  │   Alignments       │  │
│  │  JWT     │  │ Upload   │  │ Search   │  │   Score + Gaps     │  │
│  │  bcrypt  │  │ GPT Pars │  │ Global   │  │   Cover Letters    │  │
│  └──────────┘  └──────────┘  └──────────┘  │   Interview Prep   │  │
│                                             └────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │  Geo Service │  │  PII Guard   │  │  Rate Limiter            │   │
│  │  Geoapify    │  │  Redaction   │  │  5 req/min (AI routes)   │   │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│   PostgreSQL 16  │  │   Redis 7        │  │    S3 / Local FS     │
│   + pgvector     │  │   Geo cache      │  │    Resume storage    │
│   1536-d vectors │  │   Arq job queue  │  │    Presigned URLs    │
└──────────────────┘  └──────────────────┘  └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Background Worker (arq)                          │
│  Daily cron: 8 geo targets x 7 keywords = 56 API calls             │
│  Sources: TheirStack (primary) -> SerpApi Google Jobs (fallback)   │
└─────────────────────────────────────────────────────────────────────┘
```

## Features

### Resume Intelligence
- **PDF Upload + Parsing** — Extracts text via `pdfplumber`, then GPT-4o structures into a typed profile (skills, work history, education)
- **PII Redaction** — Emails, phones, SSNs, and URLs are redacted before storage
- **S3 Storage** — Resumes stored with KMS encryption, served via presigned URLs (with local fallback)

### Global Job Search
- **56 Daily API Calls** — 8 geographic targets x 7 job keywords, powered by background cron worker
- **Dual Source Fallback** — TheirStack API as primary, SerpApi Google Jobs as secondary
- **Semantic Embeddings** — Each job gets a 1536-dimension vector via OpenAI `text-embedding-3-small`

### ATS Alignment Scoring
Three-layer scoring engine:

```
                    ┌──────────────────────┐
                    │  Keyword Overlap 30%  │  Hard skills in resume vs job description
                    ├──────────────────────┤
                    │  Experience Δ    30%  │  Total months vs target months
                    ├──────────────────────┤
                    │  Cosine Similarity 40%│  Semantic vector distance
                    └──────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Overall Match Score  │  0-100 weighted aggregate
                    └──────────────────────┘
```

- **Gap Analysis** — Detects missing critical competencies (React, TypeScript, AWS, Docker, etc.)
- **Sub-scores** — Each layer reported individually for transparency

### AI Content Generation

| Feature | Model | Prompt Strategy |
|---------|-------|-----------------|
| Resume Parsing | GPT-4o | Structured JSON extraction with PII redaction |
| Cover Letters | GPT-4o | Constraint-based: includes recipient, role, your skills, company context |
| Interview Prep | GPT-4o | STAR behavioral + Technical question generation from resume + job |

### Infrastructure
- **Rate Limiting** — 5 requests/minute on AI endpoints (token bucket, per-IP)
- **Geo-Caching** — Dual cache: Redis (24h TTL) + PostgreSQL `location_cache` table
- **Error Handling** — Global JSON error middleware, structured JSON logging
- **Security** — JWT bearer auth, bcrypt hashing, CORS whitelist

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL 16 + pgvector |
| Cache / Queue | Redis 7 + arq |
| AI | OpenAI GPT-4o + text-embedding-3-small |
| Auth | python-jose (JWT) + passlib (bcrypt) |
| Storage | boto3 S3 (local fallback) |
| Jobs | TheirStack + SerpApi |
| Geo | Geoapify |
| Testing | pytest 8.3 (22 tests) |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript (strict) |
| Styling | Tailwind CSS 3.4 |
| UI Library | shadcn/ui (Radix primitives) |
| Icons | lucide-react |
| State | React Context (auth) |

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker Desktop (recommended) or PostgreSQL 16 + pgvector + Redis

### 1. Clone & Environment
```bash
git clone https://github.com/mamoonk/jobsearch.git
cd jobsearch
cp .env.example .env   # Edit with your API keys
```

### 2. Run (choose one)

**Docker (full stack):**
```bash
docker compose up -d --wait
```

**Without Docker:**
```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

**Or use the launcher:**
```bash
.\run.bat
```

### 3. Open
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Resume parsing, embeddings, cover letters, interview prep |
| `GEOAPIFY_API_KEY` | Yes | Location autocomplete / geocoding |
| `THEIRSTACK_API_KEY` | Yes | Primary job feed |
| `SERPAPI_API_KEY` | Yes | Fallback Google Jobs feed |
| `JWT_SECRET` | No | JWT signing key (default: change-this-secret) |
| `POSTGRES_*` | No | Database defaults to jobsearch/changeme@localhost:5432 |
| `REDIS_*` | No | Redis defaults to localhost:6379 |
| `AWS_*` | No | S3 storage (optional, falls back to in-memory) |

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Create account |
| `/api/v1/auth/login` | POST | Login, get JWT |
| `/api/v1/auth/me` | GET | Current user |
| `/api/v1/resumes` | POST/GET | Upload / list resumes |
| `/api/v1/resumes/{id}` | GET/DELETE | Single resume |
| `/api/v1/jobs` | GET | Search jobs with filters |
| `/api/v1/search/geo` | POST | Geoapify autocomplete |
| `/api/v1/alignments` | POST/GET | Create / list alignments |
| `/api/v1/alignments/{id}` | GET | Alignment with score + gaps |
| `/api/v1/cover-letters` | POST | Generate cover letter |
| `/api/v1/interview-prep` | POST | Generate interview Q&A |

## Project Structure

```
jobsearch/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers (7 routers)
│   │   ├── models/           # SQLAlchemy ORM (5 models)
│   │   ├── schemas/          # Pydantic v2 schemas
│   │   ├── services/         # Business logic (10 services)
│   │   ├── middleware/       # Auth, rate-limit, PII, error handler
│   │   ├── utils/            # Embedding helpers
│   │   ├── config.py         # pydantic-settings
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   ├── logging_config.py # JSON logging
│   │   ├── main.py           # FastAPI entrypoint
│   │   └── worker.py         # arq background worker
│   ├── alembic/              # Database migrations
│   └── tests/                # 8 test files (22 tests)
├── frontend/
│   ├── src/
│   │   ├── app/              # 9 Next.js routes
│   │   ├── components/       # shadcn/ui + custom components
│   │   └── lib/              # API client, auth context, utils
│   └── ...config files
├── docker-compose.yml        # 5 services (postgres, redis, backend, worker, frontend)
├── run.bat                   # Windows launcher
└── AGENTS.md                 # Development guide
```

## Testing

```bash
cd backend
python -m pytest tests/ -v

# 22 passed in 2.61s
```

| Test File | Tests | What It Covers |
|-----------|-------|----------------|
| `test_api_integration.py` | 7 | Health, register, login, JWT auth (end-to-end) |
| `test_auth.py` | 1 | Password hashing round-trip |
| `test_scoring.py` | 2 | Keyword score logic + zero edge case |
| `test_pii_redaction.py` | 3 | Email, phone, SSN redaction |
| `test_job_ingestion.py` | 3 | TheirStack response normalization + SerpApi fallback |
| `test_geo_cache.py` | 3 | Redis cache set/get/miss/invalidate |
| `test_error_handler.py` | 1 | Global error middleware returns JSON |
| `test_cover_letter.py` | 2 | Validation: missing API key, empty inputs |

## License

MIT
