from sqlalchemy import Column, Integer, Boolean, Float, String, JSON, DateTime
from datetime import datetime
from app.db.session import Base


class LeadDecision(Base):
    __tablename__ = "lead_decisions"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, index=True)

    qualified = Column(Boolean)
    score = Column(Integer)
    confidence = Column(Float)

    segment = Column(String, nullable=True)
    recommended_action = Column(String)

    reasoning = Column(JSON)

    raw_data = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)