import os
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx

AUTH_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:5001")
DATA_URL = os.getenv("DATA_SERVICE_URL", "http://data_service:5002")
VIZ_URL  = os.getenv("VIZ_SERVICE_URL", "http://viz_service:5003")
PORT = int(os.getenv("GATEWAY_PORT", "8080"))
origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else ["*"]

app = FastAPI(title="MarketView API Gateway", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1]
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{AUTH_URL}/verify", headers={"Authorization": f"Bearer {token}"})
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Token verification failed")
        return resp.json()["identity"]

@app.get("/healthz")
async def healthz():
    return {"ok": True}

# ---- Public auth passthrough ----
@app.post("/api/auth/register")
async def register(payload: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{AUTH_URL}/register", json=payload)
        return (r.json() if r.content else {}), r.status_code

@app.post("/api/auth/login")
async def login(payload: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{AUTH_URL}/login", json=payload)
        return (r.json() if r.content else {}), r.status_code

# ---- Protected routes ----
@app.get("/api/companies")
async def companies(identity: dict = Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{DATA_URL}/companies")
        return r.json()

@app.get("/api/sentiments")
async def sentiments(sector: Optional[str] = None, days: int = 7, identity: dict = Depends(verify_token)):
    params = {}
    if sector: params["sector"] = sector
    params["days"] = days
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{DATA_URL}/sentiments", params=params)
        return r.json()

@app.get("/api/treemap/top5")
async def treemap_top5(identity: dict = Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{VIZ_URL}/treemap/top5")
        return r.json()

@app.get("/api/treemap/low5")
async def treemap_low5(identity: dict = Depends(verify_token)):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{VIZ_URL}/treemap/low5")
        return r.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False)
