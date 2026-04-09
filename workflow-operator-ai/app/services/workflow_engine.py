from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.models.approval import Approval

from app.tools.company_scraper import fetch_company_website
from app.agents.research_agent import run_research_agent
from app.agents.qualification_agent import run_qualification_agent
from app.agents.email_agent import run_email_agent


def run_lead_workflow(lead_id: int, db: Session):
    lead = db.query(Lead).get(lead_id)

    if not lead:
        return {"success": False, "error": "Lead not found"}

    # Step 1: Scrape
    scraped = fetch_company_website(lead.website_url)

    if not scraped["success"]:
        return {"success": False, "error": "Scraping failed"}

    # Step 2: Research
    research = run_research_agent(scraped)

    if not research["success"]:
        return {"success": False, "error": "Research failed"}

    # Step 3: Qualification
    qualification = run_qualification_agent(research["data"])

    if not qualification["success"]:
        return {"success": False, "error": "Qualification failed"}

    decision = qualification["data"]

    # Step 4: Decision check
    if not decision.get("qualified"):
        return {
            "success": True,
            "message": "Lead not qualified",
            "decision": decision
        }

    # Step 5: Generate Email
    email = run_email_agent(research["data"], decision)

    if not email["success"]:
        return {"success": False, "error": "Email generation failed"}

    # Step 6: Create Approval
    approval = Approval(
        type="email",
        content=email["data"]
    )

    db.add(approval)
    db.commit()
    db.refresh(approval)

    return {
        "success": True,
        "message": "Workflow completed",
        "approval_id": approval.id
    }