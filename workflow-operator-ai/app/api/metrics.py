from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.metrics_service import get_metrics

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/overview")
def metrics_overview(db: Session = Depends(get_db)):
    return get_metrics(db)