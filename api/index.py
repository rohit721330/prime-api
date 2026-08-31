from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys, os

# ============================================================
#  PATH FIX FOR VERCEL
# ============================================================
# Vercel-এ সঠিক পাথ সেট করা
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.generator import generate_account, generate_multiple_accounts
except ImportError:
    # যদি ইমপোর্ট না হয়, তাহলে অল্টারনেটিভ পাথ ট্রাই করুন
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from utils.generator import generate_account, generate_multiple_accounts

# ============================================================
#  FASTAPI APP
# ============================================================
app = FastAPI(
    title="PRIME API",
    description="⚡ Prime Account Generator – Ultra Fast Free Fire Accounts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
#  PYDANTIC MODELS
# ============================================================
class AccountResponse(BaseModel):
    success: bool
    uid: Optional[str] = None
    game_uid: Optional[str] = None
    password: Optional[str] = None
    nickname: Optional[str] = None
    region: Optional[str] = None
    error: Optional[str] = None
    attempt: Optional[int] = None

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

# ============================================================
#  API ENDPOINTS
# ============================================================
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
def generate_single(
    region: str = Query("IND", description="Region (IND, TH, ME, etc)"),
    retries: int = Query(3, description="Retry attempts", ge=1, le=5)
):
    """
    Generate a single Free Fire account
    """
    try:
        result = generate_account(region, retries)
        return AccountResponse(**result)
    except Exception as e:
        return AccountResponse(
            success=False,
            error=str(e),
            attempt=0
        )

@app.post("/generate", response_model=GenerateResponse)
def generate_multiple(req: GenerateRequest):
    """
    Generate multiple Free Fire accounts (max 50)
    """
    if req.count < 1 or req.count > 50:
        raise HTTPException(400, "Count must be between 1 and 50")
    
    try:
        results = generate_multiple_accounts(req.count, req.region, req.retries)
        return GenerateResponse(
            success=True,
            total=req.count,
            successful=sum(1 for r in results if r.get("success")),
            failed=sum(1 for r in results if not r.get("success")),
            accounts=[AccountResponse(**r) for r in results]
        )
    except Exception as e:
        raise HTTPException(500, f"Generation failed: {str(e)}")

@app.get("/generate/bulk")
def generate_bulk(
    count: int = Query(10, description="Number of accounts", ge=1, le=50),
    region: str = Query("IND", description="Region"),
    retries: int = Query(3, description="Retry attempts", ge=1, le=5)
):
    """
    Generate multiple accounts (simplified GET version)
    """
    if count < 1 or count > 50:
        raise HTTPException(400, "Count must be between 1 and 50")
    
    try:
        results = generate_multiple_accounts(count, region, retries)
        return {
            "success": True,
            "total": count,
            "successful": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success")),
            "accounts": results
        }
    except Exception as e:
        raise HTTPException(500, f"Generation failed: {str(e)}")

# ============================================================
#  VERCEL SERVERLESS HANDLER
# ============================================================
def handler(request, response):
    """
    Vercel serverless function handler
    """
    return app(request, response)

# ============================================================
#  IF RUN LOCALLY
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
