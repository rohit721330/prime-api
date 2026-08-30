from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.generator import generate_account, generate_multiple_accounts

app = FastAPI(
    title="PRIME API",
    description="⚡ Prime Account Generator – Ultra Fast Free Fire Accounts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AccountResponse(BaseModel):
    success: bool
    uid: Optional[str] = None
    game_uid: Optional[str] = None
    password: Optional[str] = None
    nickname: Optional[str] = None
    region: Optional[str] = None
    error: Optional[str] = None

class GenerateRequest(BaseModel):
    count: int = 1
    region: str = "IND"
    retries: int = 3

class GenerateResponse(BaseModel):
    success: bool
    total: int
    successful: int
    failed: int
    accounts: List[AccountResponse]

@app.get("/")
def root():
    return {
        "name": "PRIME API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/generate/single": "GET – Generate one account",
            "/generate": "POST – Generate multiple accounts",
            "/generate/bulk": "GET – Bulk generate",
            "/health": "GET – Health check",
            "/docs": "Swagger Docs"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/generate/single", response_model=AccountResponse)
def generate_single(region: str = "IND", retries: int = 3):
    result = generate_account(region, retries)
    return AccountResponse(**result)

@app.post("/generate", response_model=GenerateResponse)
def generate_multiple(req: GenerateRequest):
    if req.count < 1 or req.count > 50:
        raise HTTPException(400, "Count must be between 1 and 50")
    results = generate_multiple_accounts(req.count, req.region, req.retries)
    return GenerateResponse(
        success=True,
        total=req.count,
        successful=sum(1 for r in results if r.get("success")),
        failed=sum(1 for r in results if not r.get("success")),
        accounts=[AccountResponse(**r) for r in results]
    )

@app.get("/generate/bulk")
def generate_bulk(count: int = 10, region: str = "IND", retries: int = 3):
    if count < 1 or count > 50:
        raise HTTPException(400, "Count must be between 1 and 50")
    results = generate_multiple_accounts(count, region, retries)
    return {
        "success": True,
        "total": count,
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "accounts": results
    }
