from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from datetime import datetime
from app.db.session import Base


class LeadResearch(Base):
    __tablename__ = "lead_research"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, index=True)

    company_summary = Column(String)
    industry = Column(String)

    possible_use_cases_for_ai = Column(JSON)
    target_customer_type = Column(String)

    confidence = Column(Float)

    raw_data = Column(JSON)  # full original response

    created_at = Column(DateTime, default=datetime.utcnow)