from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import auth, notes
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Notes Application API",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, tags=["auth"])
app.include_router(notes.router, tags=["notes"])


@app.get("/", tags=["health"])
def root():
    """Root endpoint"""
    return {"status": "ok", "message": "Notes API is running"}


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint for Kubernetes liveness and readiness probes"""
    return {"status": "ok", "service": "notes-backend"}