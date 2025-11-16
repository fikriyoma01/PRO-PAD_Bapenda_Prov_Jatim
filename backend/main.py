"""
FastAPI Backend for PRO-PAD Dashboard
Provides REST API endpoints for statistical modeling and data analysis
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import data, model, projection, analysis, audit, policy, settings

app = FastAPI(
    title="PRO-PAD API",
    description="REST API for PAD (Pendapatan Asli Daerah) Dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(model.router, prefix="/api/model", tags=["Model"])
app.include_router(projection.router, prefix="/api/projection", tags=["Projection"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(policy.router, prefix="/api/policy", tags=["Policy"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])


@app.get("/")
async def root():
    return {
        "message": "PRO-PAD API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
