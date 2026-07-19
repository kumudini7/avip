from __future__ import annotations

from sqlalchemy import select

from app.core.roles import ROLE_CLIENT
from app.core.security import hash_password
from app.data.use_cases import DOMAIN_NAMES
from app.db.session import SessionLocal
from app.models.domain import Domain
from app.models.user import User


def seed_assessment_data() -> None:
    db = SessionLocal()
    try:
        if db.execute(select(Domain)).first() is None:
            for domain_name in DOMAIN_NAMES:
                db.add(Domain(name=domain_name))
            db.commit()

        client = db.execute(select(User).where(User.email == "client@jade.com")).scalar_one_or_none()
        if client is None:
            client = User(
                email="client@jade.com",
                full_name="Acme Client",
                company="Acme Corp",
                hashed_password=hash_password("client123"),
                role=ROLE_CLIENT,
            )
            db.add(client)
            db.commit()
        elif client.full_name == "Acme Corp Contact" and client.company == "Acme Corp":
            client.full_name = "Acme Client"
            db.commit()
    finally:
        db.close()
