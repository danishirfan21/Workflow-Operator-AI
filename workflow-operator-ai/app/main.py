from fastapi import FastAPI
from app.db.session import engine, Base
from app.api.leads import router as leads_router

app = FastAPI(
    title="Workflow Operator AI",
    version="0.1.0"
)

# Create DB tables
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Register routes
app.include_router(leads_router)