import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from database import create_document, get_documents, db
from schemas import Campaign, Contribution

app = FastAPI(title="Crowd Fund Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Crowdfunding API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# ----------------------- Crowdfunding Endpoints -----------------------

class CreateCampaignRequest(Campaign):
    pass

class CampaignOut(BaseModel):
    id: str
    title: str
    description: str
    goal_amount: float
    max_supporters: Optional[int]
    deadline: Optional[datetime]
    created_at: datetime

class CreateContributionRequest(Contribution):
    pass

class ContributionOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    amount: float
    message: Optional[str]
    is_public: bool
    created_at: datetime

@app.post("/api/campaigns", response_model=dict)
def create_campaign(payload: CreateCampaignRequest):
    # Only allow a single active campaign for this simple app
    existing = get_documents("campaign", {})
    if existing:
        raise HTTPException(status_code=400, detail="A campaign already exists")
    inserted_id = create_document("campaign", payload)
    return {"id": inserted_id}

@app.get("/api/campaigns", response_model=List[CampaignOut])
def list_campaigns():
    items = get_documents("campaign", {})
    # sort newest first
    items.sort(key=lambda x: x.get("created_at"), reverse=True)
    result: List[CampaignOut] = []
    for it in items:
        result.append(CampaignOut(
            id=str(it.get("_id")),
            title=it.get("title"),
            description=it.get("description"),
            goal_amount=float(it.get("goal_amount")),
            max_supporters=it.get("max_supporters"),
            deadline=it.get("deadline"),
            created_at=it.get("created_at")
        ))
    return result

@app.post("/api/contributions", response_model=dict)
def add_contribution(payload: CreateContributionRequest):
    # default amount to 1000 if not provided
    amount = payload.amount
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    inserted_id = create_document("contribution", payload)
    return {"id": inserted_id}

@app.get("/api/contributions", response_model=List[ContributionOut])
def list_contributions(limit: int = 200):
    items = get_documents("contribution", {})
    # newest first
    items.sort(key=lambda x: x.get("created_at"), reverse=True)
    items = items[:limit]
    result: List[ContributionOut] = []
    for it in items:
        result.append(ContributionOut(
            id=str(it.get("_id")),
            name=it.get("name"),
            email=it.get("email"),
            amount=float(it.get("amount")),
            message=it.get("message"),
            is_public=bool(it.get("is_public", True)),
            created_at=it.get("created_at")
        ))
    return result

@app.get("/api/summary")
def get_summary():
    # One campaign expected
    campaigns = get_documents("campaign", {})
    goal = 100000.0
    if campaigns:
        c = campaigns[0]
        goal = float(c.get("goal_amount", goal))
        max_supporters = c.get("max_supporters", 100)
    else:
        max_supporters = 100
    contributions = get_documents("contribution", {})
    total = sum(float(x.get("amount", 0)) for x in contributions)
    count = len(contributions)
    percent = round((total / goal) * 100, 2) if goal > 0 else 0
    remaining_supporters = max(0, max_supporters - count)
    return {
        "goal": goal,
        "raised": total,
        "backers": count,
        "percent": percent,
        "remaining_supporters": remaining_supporters
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
