"""
Database connection manager for SSO system using MariaDB
"""
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging
from config import settings

logger = logging.getLogger(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    "host": settings.db_host,
    "port": settings.db_port,
    "user": settings.db_user,
    "password": settings.db_password,
    "database": settings.db_name,
    "charset": "utf8mb4"
}

# SQLAlchemy setup
DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions
    Usage:
        with get_db_session() as session:
            user = session.query(User).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


def get_db():
    """
    Dependency for FastAPI endpoints
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test database connection"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            logger.info(f"✅ MariaDB connection successful! Version: {version[0]}")
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()
            logger.info(f"✅ Users table accessible. Count: {user_count[0]}")
        connection.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing SSO database connection...")
    if test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
