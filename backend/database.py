from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.config import settings

DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required. Configure your PostgreSQL connection string before starting the app.")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from sqlalchemy import text


def init_db():
    import backend.models  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)

    # Safe auto-migration for newly added columns in SQLite
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT webhook_url FROM brand_settings LIMIT 1"))
        except Exception:
            try:
                conn.execute(text("ALTER TABLE brand_settings ADD COLUMN webhook_url VARCHAR(500)"))
                conn.commit()
            except Exception:
                pass

