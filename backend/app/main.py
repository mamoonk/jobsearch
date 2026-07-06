import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.database import engine, Base
from app.api.v1 import auth, resumes, jobs, search, alignments, cover_letters, interview_prep
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.error_handler import ErrorHandlingMiddleware
from app.logging_config import setup_logging

logger = logging.getLogger(__name__)

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError:
        logger.warning("Database unavailable during startup — skipping table creation")
    yield


app = FastAPI(
    title="JobSearch AI",
    description="Global Job Search, ATS Alignment & Interview Prep Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.rate_limit_requests_per_minute,
    window_seconds=60,
)

app.add_middleware(ErrorHandlingMiddleware)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(alignments.router, prefix="/api/v1/alignments", tags=["Alignments"])
app.include_router(cover_letters.router, prefix="/api/v1/cover-letters", tags=["Cover Letters"])
app.include_router(interview_prep.router, prefix="/api/v1/interview-prep", tags=["Interview Prep"])


@app.get("/health")
async def health():
    return {"status": "ok"}
