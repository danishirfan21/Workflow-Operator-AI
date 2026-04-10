from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, get_db
from app.models.approval import Approval
from app.api.schemas import ApprovalCreate, ApprovalResponse

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])



@router.post("/", response_model=ApprovalResponse)
def create_approval(item: ApprovalCreate, db: Session = Depends(get_db)):
    approval = Approval(**item.model_dump())
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


@router.get("/", response_model=list[ApprovalResponse])
def list_approvals(db: Session = Depends(get_db)):
    return db.query(Approval).all()


@router.post("/{approval_id}/approve")
def approve(approval_id: int, db: Session = Depends(get_db)):
    approval = db.query(Approval).get(approval_id)
    approval.status = "approved"
    db.commit()
    return {"status": "approved"}


@router.post("/{approval_id}/reject")
def reject(approval_id: int, db: Session = Depends(get_db)):
    approval = db.query(Approval).get(approval_id)
    approval.status = "rejected"
    db.commit()
    return {"status": "rejected"}