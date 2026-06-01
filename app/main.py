from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Hackathon App",
    description="DevSecOps Hackathon Template",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Hello from DevSecOps Hackathon!", "status": "running"}


@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )