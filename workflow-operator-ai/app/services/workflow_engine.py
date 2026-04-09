from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.models.approval import Approval

from app.tools.company_scraper import fetch_company_website
from app.agents.research_agent import run_research_agent
from app.agents.qualification_agent import run_qualification_agent
from app.agents.email_agent import run_email_agent

from datetime import datetime
from app.models.workflow import WorkflowRun
from app.services.logger import log_step_start, log_step_success, log_step_failure


def run_lead_workflow(lead_id: int, db):
    run = WorkflowRun(
        lead_id=lead_id,
        status="running",
        started_at=datetime.utcnow()
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        # ---------------- STEP 1: Fetch Lead ----------------
        step = log_step_start(db, run.id, "fetch_lead", {"lead_id": lead_id})

        lead = db.query(Lead).get(lead_id)

        if not lead:
            raise Exception("Lead not found")

        log_step_success(db, step, {"lead": lead.id})

        # ---------------- STEP 2: Scrape ----------------
        step = log_step_start(db, run.id, "scrape_website", {"url": lead.website_url})

        scraped = fetch_company_website(lead.website_url)

        if not scraped["success"]:
            raise Exception("Scraping failed")

        log_step_success(db, step, scraped)

        # ---------------- STEP 3: Research ----------------
        step = log_step_start(db, run.id, "research_agent", scraped)

        research = run_research_agent(scraped)

        if not research["success"]:
            raise Exception("Research failed")

        log_step_success(db, step, research["data"])

        # ---------------- STEP 4: Qualification ----------------
        step = log_step_start(db, run.id, "qualification_agent", research["data"])

        qualification = run_qualification_agent(research["data"])

        if not qualification["success"]:
            raise Exception("Qualification failed")

        decision = qualification["data"]

        log_step_success(db, step, decision)

        # ---------------- STEP 5: Decision ----------------
        if not decision.get("qualified"):
            run.status = "success"
            run.finished_at = datetime.utcnow()
            db.commit()

            return {
                "success": True,
                "message": "Lead not qualified"
            }

        # ---------------- STEP 6: Email ----------------
        step = log_step_start(db, run.id, "email_agent", decision)

        email = run_email_agent(research["data"], decision)

        if not email["success"]:
            raise Exception("Email generation failed")

        log_step_success(db, step, email["data"])

        # ---------------- STEP 7: Approval ----------------
        step = log_step_start(db, run.id, "create_approval", email["data"])

        approval = Approval(
            type="email",
            content=email["data"]
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        log_step_success(db, step, {"approval_id": approval.id})

        # ---------------- FINAL ----------------
        run.status = "success"
        run.finished_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "approval_id": approval.id,
            "run_id": run.id
        }

    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)
        run.finished_at = datetime.utcnow()
        db.commit()

        log_step_failure(db, step, str(e))

        return {
            "success": False,
            "error": str(e),
            "run_id": run.id
        }