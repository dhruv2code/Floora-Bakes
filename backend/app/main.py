from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import Base, engine
from app.routers.analytics import router as analytics_router
from app.routers.insights import router as insights_router
from app.routers.reports import router as reports_router
from app.routers.sales import router as sales_router
from app.routers.upload import router as upload_router

settings = get_settings()

app = FastAPI(
    title=f"{settings.app_name} API",
    version="1.0.0",
    description="Bakery sales import, analytics, insights, and reporting API.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(upload_router)
app.include_router(sales_router)
app.include_router(analytics_router)
app.include_router(insights_router)
app.include_router(reports_router)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
