from typing import Dict, Optional

from app.models.user import User, UserRole
from app.models.note import Note
from app.utils.auth import get_password_hash


def create_test_user(
    db, 
    email: str = "test@example.com", 
    password: str = "password123", 
    name: str = "Test User",
    role: UserRole = UserRole.USER
) -> User:
    """
    Create a test user in the database
    """
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        name=name,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_note(
    db, 
    user_id: int, 
    title: str = "Test Note", 
    description: str = "This is a test note"
) -> Note:
    """
    Create a test note in the database
    """
    note = Note(
        title=title,
        description=description,
        owner_id=user_id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note