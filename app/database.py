from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# 建立資料庫引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 檢查連線是否有效
    echo=False,          # 生產環境設為 False
)

# 建立 Session 工廠
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 建立 Base 類別
Base = declarative_base()


def get_db():
    """
    取得資料庫 session（依賴注入用）
    使用 yield 確保 session 會被正確關閉
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
