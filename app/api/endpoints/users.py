from typing import Any, List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.deps import get_admin_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserResponse, UserDetailResponse, UserUpdateRole, UserUpdateStatus,
    PaginatedResponse, PaginationMeta
)

router = APIRouter(prefix=f"{settings.API_V1_STR}/admin/users")


@router.get("/", response_model=PaginatedResponse[UserResponse], summary="List Users", description="Get a paginated list of all users with optional filtering by role and active status.")
def get_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
    page: int = Query(1, gt=0, description="Page number, starting from 1"),
    size: int = Query(10, gt=0, le=100, description="Number of items per page (max 100)"),
    role: Optional[str] = Query(None, description="Filter by role (admin or user)"),
    is_active: Optional[bool] = Query(None, description="Filter by active status (true/false)")
) -> Any:
    """
    Retrieve a paginated list of users with optional filtering.
    
    - **page**: Page number (starting from 1)
    - **size**: Number of items per page (max 100)
    - **role**: Optional filter by user role ('admin' or 'user')
    - **is_active**: Optional filter by account status
    
    Returns:
    - Paginated list of users with pagination metadata
    
    Only accessible by admin users.
    """
    query = db.query(User)
    
    # Apply filters if provided
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Calculate total for pagination
    total = query.count()
    
    # Calculate pages
    total_pages = math.ceil(total / size) if total > 0 else 1
    
    # Ensure page is within bounds
    page = min(page, total_pages) if total > 0 else 1
    
    # Calculate offset
    offset = (page - 1) * size
    
    # Get paginated results
    users = query.offset(offset).limit(size).all()
    
    # Create pagination metadata
    pagination_meta = PaginationMeta(
        total=total,
        page=page,
        size=size,
        pages=total_pages
    )
    
    return {"items": users, "meta": pagination_meta}


@router.get(
    "/{user_id}", 
    response_model=UserDetailResponse,
    summary="Get User Details",
    description="Get detailed information about a specific user, including their notes.",
    responses={
        200: {"description": "User details retrieved successfully"},
        404: {"description": "User not found"},
        403: {"description": "Not enough permissions, admin role required"}
    }
)
def get_user_details(
    user_id: int = Path(..., title="User ID", description="The ID of the user to retrieve"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
) -> Any:
    """
    Get detailed information about a specific user, including their notes.
    
    - **user_id**: The ID of the user to retrieve
    
    Returns:
    - Detailed user information including profile data and notes
    
    Only accessible by admin users.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put(
    "/{user_id}/role", 
    response_model=UserResponse,
    summary="Update User Role",
    description="Update a user's role (admin/user). Only admins can promote other users to admin.",
    responses={
        200: {"description": "Role updated successfully"},
        400: {"description": "Invalid role or admin attempting to demote themselves"},
        404: {"description": "User not found"},
        403: {"description": "Not enough permissions, admin role required"}
    }
)
def update_user_role(
    user_id: int = Path(..., title="User ID", description="The ID of the user to update"),
    role_update: UserUpdateRole = Body(..., description="New role information"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
) -> Any:
    """
    Update a user's role. Only admins can set other users as admins.
    
    - **user_id**: The ID of the user to update
    - **role_update**: The new role ('admin' or 'user')
    
    Returns:
    - Updated user information
    
    Notes:
    - Admins cannot demote themselves
    - Only valid roles ('admin' or 'user') are accepted
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate role value
    if role_update.role not in [UserRole.ADMIN, UserRole.USER]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'admin' or 'user'"
        )

    # Prevent admin from demoting themselves
    if user.id == admin.id and role_update.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot demote themselves"
        )
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return user


@router.put(
    "/{user_id}/status", 
    response_model=UserResponse,
    summary="Update User Status",
    description="Activate or deactivate a user account. Admin cannot deactivate their own account.",
    responses={
        200: {"description": "Status updated successfully"},
        400: {"description": "Admin attempting to deactivate themselves"},
        404: {"description": "User not found"},
        403: {"description": "Not enough permissions, admin role required"}
    }
)
def update_user_status(
    user_id: int = Path(..., title="User ID", description="The ID of the user to update"),
    status_update: UserUpdateStatus = Body(..., description="New status information"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
) -> Any:
    """
    Activate or deactivate a user account.
    
    - **user_id**: The ID of the user to update
    - **status_update**: The new status (true=active, false=inactive)
    
    Returns:
    - Updated user information
    
    Notes:
    - Admins cannot deactivate their own account
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == admin.id and not status_update.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot deactivate themselves"
        )
    
    user.is_active = status_update.is_active
    db.commit()
    db.refresh(user)
    return user