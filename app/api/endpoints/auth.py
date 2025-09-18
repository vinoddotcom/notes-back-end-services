from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, Token
from app.utils.auth import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix=f"{settings.API_V1_STR}/auth")


@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register User",
    description="Register a new user account. All new users are created with 'user' role by default.",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Email already registered"},
        422: {"description": "Validation error in input data"}
    }
)
def register(
    user_in: UserCreate = Body(..., description="User registration data"), 
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user account.
    
    - **email**: User's email address (must be unique)
    - **name**: User's full name
    - **password**: User's password (minimum 8 characters)
    
    Returns:
    - Created user profile (without password)
    
    Notes:
    - All new users are created with 'user' role by default
    - Only admin users can later promote other users to admin role
    """
    # Check if the email is already registered
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Force role to be "user" during registration
    # Only admins can promote users to admin role via the admin endpoints
    user_role = UserRole.USER
    
    # Create new user
    db_user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=get_password_hash(user_in.password),
        role=user_role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post(
    "/login", 
    response_model=Token,
    summary="Login",
    description="OAuth2 compatible token login. Returns an access token for use in authenticated API calls.",
    responses={
        200: {"description": "Login successful, access token returned"},
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error in input data"}
    }
)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    - **username**: User's email address
    - **password**: User's password
    
    Returns:
    - Access token and token type
    
    Notes:
    - The access token includes user role information
    - Use the returned token in Authorization header as "Bearer {token}"
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, role=user.role, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get Current User Profile",
    description="Get information about the currently authenticated user.",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Not authenticated"}
    }
)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get information about the currently authenticated user.
    
    Returns:
    - Current user profile information
    
    Notes:
    - Requires authentication
    - Returns the user associated with the provided access token
    """
    return current_user