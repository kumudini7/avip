from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.assessment_seed import seed_assessment_data
from app.services.demo_seed import seed_demo_data
from app.services.document_processor import ensure_directory
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.assessment_seed import seed_assessment_data
from app.services.demo_seed import seed_demo_data
from app.services.document_processor import ensure_directory

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://avip-21.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"message": "AVIP API is running"}


@app.on_event("startup")
def prepare_storage() -> None:
    ensure_directory(settings.upload_dir)
    ensure_directory(settings.report_dir)
    try:
        seed_demo_data()
    except Exception:
        # Demo seeding should never block app startup.
        pass
    try:
        seed_assessment_data()
    except Exception:
        # Assessment seeding should never block app startup.
        pass
