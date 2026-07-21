import os
import ssl

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CA_PATH = os.path.join(BASE_DIR, "certs", "ca.pem")

connect_args = {}
if os.path.exists(CA_PATH):
    # Aiven's console lists this service as ssl-mode=REQUIRED (encrypt, don't
    # verify the chain) rather than VERIFY_CA/VERIFY_IDENTITY. Verifying against
    # ca.pem fails on Python 3.12 / OpenSSL 3.x with "self-signed certificate in
    # certificate chain" regardless of how the trust store is built (confirmed by
    # testing a from-scratch SSLContext with only ca.pem loaded, and pymysql's
    # ssl_ca/ssl_verify_cert kwargs - both hit the identical chain-build error) -
    # a known class of issue with managed MySQL providers sending their root CA
    # as part of the presented chain. So match Aiven's own mode: encrypt the
    # connection, skip chain verification.
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
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