from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.lead import Lead
from app.api.schemas import LeadCreate, LeadResponse
from app.tools.company_scraper import fetch_company_website
from app.agents.research_agent import run_research_agent

router = APIRouter(prefix="/api/leads", tags=["Leads"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ingest", response_model=LeadResponse)
def ingest_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    db_lead = Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/test-scrape")
def test_scrape(url: str):
    result = fetch_company_website(url)
    return result

@router.get("/research")
def research_company(url: str):
    scraped = fetch_company_website(url)
    result = run_research_agent(scraped)
    return result