from pydantic import BaseModel, EmailStr
from typing import Optional, Any

class LeadCreate(BaseModel):
    full_name: str
    email: EmailStr
    company_name: Optional[str] = None
    website_url: Optional[str] = None
    job_title: Optional[str] = None
    source: Optional[str] = None

class LeadResponse(LeadCreate):
    id: int

    class Config:
        from_attributes = True

class ApprovalCreate(BaseModel):
    type: str
    content: Any

class ApprovalResponse(BaseModel):
    id: int
    type: str
    content: Any
    status: str

    class Config:
        from_attributes = True