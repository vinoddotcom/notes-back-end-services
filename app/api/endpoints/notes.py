from typing import Any, List
import math

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.deps import get_current_active_user, get_admin_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from app.schemas.user import PaginatedResponse, PaginationMeta

router = APIRouter(prefix=f"{settings.API_V1_STR}/notes")


@router.post(
    "/", 
    response_model=NoteResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create Note",
    description="Create a new note for the current authenticated user.",
    responses={
        201: {"description": "Note created successfully"},
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error in input data"}
    }
)
def create_note(
    note_in: NoteCreate = Body(..., description="Note data to create"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new note for the current user.
    
    - **title**: Note title
    - **description**: Optional note content
    
    Returns:
    - Created note with id and timestamps
    """
    note = Note(
        title=note_in.title,
        description=note_in.description,
        owner_id=current_user.id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get(
    "/", 
    response_model=PaginatedResponse[NoteResponse],
    summary="List Notes",
    description="Get paginated list of notes. Admins can see all notes, regular users can only see their own.",
    responses={
        200: {"description": "List of notes retrieved successfully"},
        401: {"description": "Not authenticated"}
    }
)
def get_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, gt=0, description="Page number, starting from 1"),
    size: int = Query(10, gt=0, le=100, description="Number of items per page (max 100)")
) -> Any:
    """
    Get paginated notes - if admin, get all notes, otherwise get only user's notes.
    
    - **page**: Page number (starting from 1)
    - **size**: Number of items per page (max 100)
    
    Returns:
    - Paginated list of notes with pagination metadata
    """
    # Build query based on user role
    if current_user.role == UserRole.ADMIN:
        query = db.query(Note)
    else:
        query = db.query(Note).filter(Note.owner_id == current_user.id)
    
    # Calculate total for pagination
    total = query.count()
    
    # Calculate pages
    total_pages = math.ceil(total / size) if total > 0 else 1
    
    # Ensure page is within bounds
    page = min(page, total_pages) if total > 0 else 1
    
    # Calculate offset
    offset = (page - 1) * size
    
    # Get paginated results
    notes = query.order_by(Note.created_at.desc()).offset(offset).limit(size).all()
    
    # Create pagination metadata
    pagination_meta = PaginationMeta(
        total=total,
        page=page,
        size=size,
        pages=total_pages
    )
    
    return {"items": notes, "meta": pagination_meta}


@router.get(
    "/{note_id}", 
    response_model=NoteResponse,
    summary="Get Note",
    description="Get a specific note by ID. Users can only access their own notes unless they are admins.",
    responses={
        200: {"description": "Note retrieved successfully"},
        404: {"description": "Note not found"},
        403: {"description": "Permission denied - note belongs to another user"},
        401: {"description": "Not authenticated"}
    }
)
def get_note(
    note_id: int = Path(..., title="Note ID", description="The ID of the note to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific note by ID.
    
    - **note_id**: The ID of the note to retrieve
    
    Returns:
    - Complete note details
    
    Notes:
    - Regular users can only access their own notes
    - Admin users can access any note
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Check if the user has permission to access this note
    if note.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    return note


@router.put(
    "/{note_id}", 
    response_model=NoteResponse,
    summary="Update Note",
    description="Update an existing note. Users can only update their own notes unless they are admins.",
    responses={
        200: {"description": "Note updated successfully"},
        404: {"description": "Note not found"},
        403: {"description": "Permission denied - note belongs to another user"},
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error in input data"}
    }
)
def update_note(
    note_id: int = Path(..., title="Note ID", description="The ID of the note to update"),
    note_in: NoteUpdate = Body(..., description="Updated note data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update a note.
    
    - **note_id**: The ID of the note to update
    - **title**: Optional new title
    - **description**: Optional new description
    
    Returns:
    - Updated note details
    
    Notes:
    - Regular users can only update their own notes
    - Admin users can update any note
    - Fields that are not provided will remain unchanged
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Check if the user has permission to update this note
    if note.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    # Update note fields
    if note_in.title is not None:
        note.title = note_in.title
    if note_in.description is not None:
        note.description = note_in.description
    
    db.commit()
    db.refresh(note)
    return note


@router.delete(
    "/{note_id}", 
    status_code=status.HTTP_200_OK,
    summary="Delete Note",
    description="Delete a note. Users can only delete their own notes unless they are admins.",
    responses={
        200: {"description": "Note deleted successfully"},
        404: {"description": "Note not found"},
        403: {"description": "Permission denied - note belongs to another user"},
        401: {"description": "Not authenticated"}
    }
)
def delete_note(
    note_id: int = Path(..., title="Note ID", description="The ID of the note to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a note.
    
    - **note_id**: The ID of the note to delete
    
    Returns:
    - Success message
    
    Notes:
    - Regular users can only delete their own notes
    - Admin users can delete any note
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Check if the user has permission to delete this note
    if note.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}