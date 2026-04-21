"""
MindOS AI - FastAPI Entry Point
"""

from fastapi import FastAPI

app = FastAPI(
    title="MindOS AI",
    description="AI Mental Health Companion",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"name": "MindOS AI", "version": "0.1.0", "status": "running"}
