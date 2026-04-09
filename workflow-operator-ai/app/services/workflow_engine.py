import json
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
from app.models.lead_research import LeadResearch
from app.models.lead_decision import LeadDecision
from app.models.email_draft import EmailDraft
from app.models.evaluation_run import EvaluationRun
from app.services.evaluation_service import evaluate_decision, evaluate_email


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

        research_data = research["data"]

        log_step_success(db, step, research_data)

        # Store in lead_research table
        lead_research_record = LeadResearch(
            lead_id=lead.id,
            company_summary=research_data.get("company_summary"),
            industry=research_data.get("industry"),
            possible_use_cases_for_ai=research_data.get("possible_use_cases_for_ai"),
            target_customer_type=research_data.get("target_customer_type"),
            confidence=float(research_data.get("confidence", 0)),
            raw_data=json.loads(json.dumps(research_data))
        )

        db.add(lead_research_record)

        try:
            db.commit()
            db.refresh(lead_research_record)
            print("LeadResearch saved:", lead_research_record.id)
        except Exception as e:
            db.rollback()
            print("Error saving LeadResearch:", str(e))
            raise e

        # ---------------- STEP 4: Qualification ----------------
        step = log_step_start(db, run.id, "qualification_agent", research_data)

        qualification = run_qualification_agent(research_data)

        if not qualification["success"]:
            raise Exception("Qualification failed")

        decision = qualification["data"]

        log_step_success(db, step, decision)

        # Store Decision
        lead_decision_record = LeadDecision(
            lead_id=lead.id,
            qualified=decision.get("qualified"),
            score=decision.get("score"),
            confidence=float(decision.get("confidence", 0)),
            segment=decision.get("segment"),
            recommended_action=decision.get("recommended_action"),
            reasoning=decision.get("reasons") or decision.get("reasoning"),
            raw_data=decision
        )

        db.add(lead_decision_record)

        try:
            db.commit()
            db.refresh(lead_decision_record)
            print("LeadDecision saved:", lead_decision_record.id)
        except Exception as e:
            db.rollback()
            print("Error saving LeadDecision:", str(e))
            raise e

        # ---------------- STEP 5: Decision ----------------
        if not decision.get("qualified"):
            run.status = "success"
            run.finished_at = datetime.utcnow()
            db.commit()

            return {
                "success": True,
                "message": "Lead not qualified"
            }

        # ---------------- EVALUATE DECISION ----------------

        decision_eval = evaluate_decision(decision)

        decision_eval_record = EvaluationRun(
            run_id=run.id,
            lead_id=lead.id,
            evaluation_type="decision_quality",
            score=decision_eval["score"],
            result=decision_eval
        )

        db.add(decision_eval_record)

        try:
            db.commit()
            db.refresh(decision_eval_record)
            print("Decision Evaluation saved:", decision_eval_record.id)
        except Exception as e:
            db.rollback()
            print("Error saving Decision Evaluation:", str(e))
        

        # ---------------- STEP 6: Email ----------------
        step = log_step_start(db, run.id, "email_agent", decision)

        email = run_email_agent(research_data, decision)

        if not email["success"]:
            raise Exception("Email generation failed")

        email_data = email["data"]

        log_step_success(db, step, email_data)

        # Store Email Draft
        email_draft = EmailDraft(
            lead_id=lead.id,
            subject=email_data.get("subject"),
            body=email_data.get("email_body"),
            tone=email_data.get("tone"),
            confidence=float(email_data.get("confidence", 0)),
            status="draft"
        )

        db.add(email_draft)

        try:
            db.commit()
            db.refresh(email_draft)
            print("EmailDraft saved:", email_draft.id)
        except Exception as e:
            db.rollback()
            print("Error saving EmailDraft:", str(e))
            raise e

        # ---------------- EVALUATE EMAIL ----------------

        email_eval = evaluate_email(email_data)

        email_eval_record = EvaluationRun(
            run_id=run.id,
            lead_id=lead.id,
            evaluation_type="email_quality",
            score=email_eval["score"],
            result=email_eval
        )

        db.add(email_eval_record)

        try:
            db.commit()
            db.refresh(email_eval_record)
            print("Email Evaluation saved:", email_eval_record.id)
        except Exception as e:
            db.rollback()
            print("Error saving Email Evaluation:", str(e))

        # ---------------- STEP 7: Approval ----------------
        step = log_step_start(db, run.id, "create_approval", email["data"])

        approval = Approval(
            type="email",
            content={
                "email_draft_id": email_draft.id
            }
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