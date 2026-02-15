from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import color_analysis, sessions, cart

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AuraWear 個人色彩診斷系統 API",
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(color_analysis.router, prefix="/api", tags=["Color Analysis"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(cart.router, prefix="/api", tags=["Cart"])


@app.get("/")
def root():
    """API 根路徑"""
    return {
        "message": "Welcome to AuraWear API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy"}
