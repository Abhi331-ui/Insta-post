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

        try:
            conn.execute(text("SELECT posting_times FROM brand_settings LIMIT 1"))
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE brand_settings ADD COLUMN posting_times TEXT DEFAULT '[\"09:00\"]'"))
                conn.commit()
            except Exception:
                pass

        # Safe auto-migration for Telegram columns
        for col, col_type in [
            ("telegram_bot_token", "VARCHAR(200)"),
            ("telegram_chat_id", "VARCHAR(100)"),
            ("telegram_connected", "BOOLEAN DEFAULT FALSE"),
        ]:
            try:
                conn.execute(text(f"SELECT {col} FROM brand_settings LIMIT 1"))
            except Exception:
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    conn.execute(text(f"ALTER TABLE brand_settings ADD COLUMN {col} {col_type}"))
                    conn.commit()
                except Exception:
                    pass

        # Safe auto-migration for Instagram profile columns
        for col, col_type in [
            ("username", "VARCHAR(100)"),
            ("profile_picture_url", "VARCHAR(500)"),
        ]:
            try:
                conn.execute(text(f"SELECT {col} FROM instagram_accounts LIMIT 1"))
            except Exception:
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    conn.execute(text(f"ALTER TABLE instagram_accounts ADD COLUMN {col} {col_type}"))
                    conn.commit()
                except Exception:
                    pass

        # Safe auto-migration for Post monetization columns
        for col, col_type in [
            ("share_token", "VARCHAR(64)"),
            ("dm_keyword", "VARCHAR(50)"),
            ("dm_message", "TEXT"),
            ("client_feedback", "TEXT"),
        ]:
            try:
                conn.execute(text(f"SELECT {col} FROM posts LIMIT 1"))
            except Exception:
                try:
                    conn.rollback()
                except Exception:
                    pass
                try:
                    conn.execute(text(f"ALTER TABLE posts ADD COLUMN {col} {col_type}"))
                    conn.commit()
                except Exception:
                    pass


