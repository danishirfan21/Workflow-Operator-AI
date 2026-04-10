from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.workflow import WorkflowRun
from app.models.lead_decision import LeadDecision
from app.models.email_draft import EmailDraft
from app.models.evaluation_run import EvaluationRun


def get_metrics(db: Session):
    # ---------------- TOTAL LEADS ----------------
    total_runs = db.query(func.count(WorkflowRun.id)).scalar() or 0

    # ---------------- QUALIFIED ----------------
    qualified_count = db.query(func.count(LeadDecision.id))\
        .filter(LeadDecision.qualified == True)\
        .scalar() or 0

    qualified_rate = (qualified_count / total_runs) if total_runs else 0

    # ---------------- EMAILS ----------------
    emails_generated = db.query(func.count(EmailDraft.id)).scalar() or 0

    # ---------------- AVG DECISION SCORE ----------------
    avg_decision_score = db.query(func.avg(EvaluationRun.score))\
        .filter(EvaluationRun.evaluation_type == "decision_quality")\
        .scalar() or 0

    # ---------------- AVG EMAIL SCORE ----------------
    avg_email_score = db.query(func.avg(EvaluationRun.score))\
        .filter(EvaluationRun.evaluation_type == "email_quality")\
        .scalar() or 0

    # ---------------- BUSINESS ESTIMATES ----------------
    # Assumption: each lead takes 10 mins manually
    time_saved_minutes = total_runs * 10

    # Assumption: $5 per 10 min task
    cost_saved_usd = total_runs * 5

    return {
        "leads_processed": total_runs,
        "qualified_rate": round(qualified_rate, 2),
        "emails_generated": emails_generated,
        "avg_decision_score": round(float(avg_decision_score), 2) if avg_decision_score else 0,
        "avg_email_score": round(float(avg_email_score), 2) if avg_email_score else 0,
        "estimated_time_saved_minutes": time_saved_minutes,
        "estimated_cost_saved_usd": cost_saved_usd
    }