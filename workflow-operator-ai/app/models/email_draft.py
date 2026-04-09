from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from app.db.session import Base


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, index=True)

    subject = Column(String)
    body = Column(Text)

    tone = Column(String, nullable=True)
    confidence = Column(Float)

    status = Column(String, default="draft")  
    # draft, approved, sent, rejected

    approved_by = Column(String, nullable=True)
    sent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)