from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime
from app.db.session import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, index=True)
    workflow_type = Column(String, default="lead_processing")

    status = Column(String, default="running")  # running, success, failed

    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    current_step = Column(String, nullable=True)
    error_message = Column(String, nullable=True)


class WorkflowStepLog(Base):
    __tablename__ = "workflow_step_logs"

    id = Column(Integer, primary_key=True, index=True)

    run_id = Column(Integer, ForeignKey("workflow_runs.id"))

    step_name = Column(String)
    status = Column(String)  # success, failed

    input_json = Column(JSON)
    output_json = Column(JSON)

    error_message = Column(String, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)