from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


from pathlib import Path
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CA_CERT = BASE_DIR / "certs" / "ca.pem"

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
            "ca": str(CA_CERT)
        }
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()