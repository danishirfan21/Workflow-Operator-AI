from datetime import datetime
from app.models.workflow import WorkflowStepLog


def log_step_start(db, run_id, step_name, input_data):
    step = WorkflowStepLog(
        run_id=run_id,
        step_name=step_name,
        status="running",
        input_json=input_data,
        started_at=datetime.utcnow()
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def log_step_success(db, step, output_data):
    step.status = "success"
    step.output_json = output_data
    step.finished_at = datetime.utcnow()
    db.commit()


def log_step_failure(db, step, error_message):
    step.status = "failed"
    step.error_message = str(error_message)
    step.finished_at = datetime.utcnow()
    db.commit()