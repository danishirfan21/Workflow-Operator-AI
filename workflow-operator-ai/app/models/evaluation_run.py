from sqlalchemy import Column, Integer, Float, String, JSON, DateTime
from datetime import datetime
from app.db.session import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)

    run_id = Column(Integer, index=True)
    lead_id = Column(Integer, index=True)

    evaluation_type = Column(String)  
    # decision_quality, email_quality, overall

    score = Column(Float)

    result = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)