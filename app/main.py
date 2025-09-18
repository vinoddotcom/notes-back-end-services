from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import auth, notes, users
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    # Notes Application API
    
    A REST API for a notes application with user authentication, role-based access control, and admin management features.
    
    ## Features
    - **User Management**: Registration, authentication, admin controls
    - **Notes Management**: Create, read, update, delete notes with permission controls
    - **Role-based Access Control**: Admin and regular user roles
    - **JWT Authentication**: Secure token-based API access
    
    ## Endpoints
    The API provides endpoints for user registration, authentication, note management, and admin user management.
    
    ## Authentication
    - Use the `/api/v1/auth/register` endpoint to create a new user account
    - Use the `/api/v1/auth/login` endpoint to obtain an access token
    - Include the token in the Authorization header as `Bearer {token}` for authenticated endpoints
    
    """,
    version="1.0.0",
    openapi_tags=[
        {"name": "auth", "description": "Authentication and user registration operations"},
        {"name": "notes", "description": "Note management operations"},
        {"name": "admin", "description": "Admin-only operations for user and system management"},
        {"name": "users", "description": "User management operations (admin only)"},
        {"name": "health", "description": "Health check endpoints for monitoring and load balancing"}
    ],
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
    },
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex="https?://.*" if "*" in settings.ALLOWED_ORIGINS else None,
)

# Include API routers
app.include_router(auth.router, tags=["auth"])
app.include_router(notes.router, tags=["notes"])
app.include_router(users.router, tags=["admin", "users"])


@app.get("/", tags=["health"])
def root():
    """Root endpoint"""
    return {"status": "ok", "message": "Notes API is running"}


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint for load balancers and container health checks"""
    return {"status": "ok", "service": "notes-backend"}


@app.get("/api/health", tags=["health"])
def api_health_check():
    """API health check endpoint for ECS container health checks"""
    return {"status": "ok", "service": "notes-backend-api"}