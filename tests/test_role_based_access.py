import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.note import Note
from tests.utils import create_test_user, create_test_note


def get_auth_header(client, user_email="test@example.com", user_password="password123"):
    """Helper function to get authentication headers"""
    login_data = {
        "username": user_email,  # OAuth2 form expects 'username', not 'email'
        "password": user_password
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_access_to_all_notes(client: TestClient, db: Session):
    """
    Test that an admin can access notes from all users
    """
    # Create an admin user
    admin = create_test_user(
        db, 
        email="admin@example.com", 
        password="adminpass123", 
        name="Admin User", 
        role=UserRole.ADMIN
    )
    admin_header = get_auth_header(client, "admin@example.com", "adminpass123")
    
    # Create a regular user
    user = create_test_user(
        db, 
        email="user@example.com", 
        password="userpass123", 
        name="Regular User"
    )
    
    # Create notes for the regular user
    user_note = create_test_note(db, user.id, "User Note", "This belongs to the regular user")
    
    # Test admin can access the user's note
    response = client.get(f"/api/v1/notes/{user_note.id}", headers=admin_header)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == user_note.id
    assert data["title"] == user_note.title
    assert data["owner_id"] == user.id


def test_admin_can_edit_any_note(client: TestClient, db: Session):
    """
    Test that an admin can edit notes from any user
    """
    # Create an admin user
    admin = create_test_user(
        db, 
        email="admin@example.com", 
        password="adminpass123", 
        name="Admin User", 
        role=UserRole.ADMIN
    )
    admin_header = get_auth_header(client, "admin@example.com", "adminpass123")
    
    # Create a regular user
    user = create_test_user(
        db, 
        email="user@example.com", 
        password="userpass123", 
        name="Regular User"
    )
    
    # Create a note for the regular user
    user_note = create_test_note(db, user.id, "User Note", "This belongs to the regular user")
    
    # Update the note as admin
    update_data = {
        "title": "Admin Updated This",
        "description": "Note edited by admin"
    }
    
    response = client.put(
        f"/api/v1/notes/{user_note.id}",
        json=update_data,
        headers=admin_header
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == user_note.id
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["owner_id"] == user.id


def test_admin_can_delete_any_note(client: TestClient, db: Session):
    """
    Test that an admin can delete notes from any user
    """
    # Create an admin user
    admin = create_test_user(
        db, 
        email="admin@example.com", 
        password="adminpass123", 
        name="Admin User", 
        role=UserRole.ADMIN
    )
    admin_header = get_auth_header(client, "admin@example.com", "adminpass123")
    
    # Create a regular user
    user = create_test_user(
        db, 
        email="user@example.com", 
        password="userpass123", 
        name="Regular User"
    )
    
    # Create a note for the regular user
    user_note = create_test_note(db, user.id, "User Note", "This belongs to the regular user")
    
    # Delete the note as admin
    response = client.delete(f"/api/v1/notes/{user_note.id}", headers=admin_header)
    assert response.status_code == 200
    
    # Check that the note was actually deleted
    deleted_note = db.query(Note).filter(Note.id == user_note.id).first()
    assert deleted_note is None


def test_user_cannot_access_others_notes(client: TestClient, db: Session):
    """
    Test that a regular user cannot access notes from other users
    """
    # Create two regular users
    user1 = create_test_user(
        db, 
        email="user1@example.com", 
        password="userpass123", 
        name="User One"
    )
    user1_header = get_auth_header(client, "user1@example.com", "userpass123")
    
    user2 = create_test_user(
        db, 
        email="user2@example.com", 
        password="userpass123", 
        name="User Two"
    )
    
    # Create a note for user2
    user2_note = create_test_note(db, user2.id, "User2 Note", "This belongs to User Two")
    
    # Try to access user2's note as user1
    response = client.get(f"/api/v1/notes/{user2_note.id}", headers=user1_header)
    assert response.status_code == 403  # Forbidden


def test_user_cannot_edit_others_notes(client: TestClient, db: Session):
    """
    Test that a regular user cannot edit notes from other users
    """
    # Create two regular users
    user1 = create_test_user(
        db, 
        email="user1@example.com", 
        password="userpass123", 
        name="User One"
    )
    user1_header = get_auth_header(client, "user1@example.com", "userpass123")
    
    user2 = create_test_user(
        db, 
        email="user2@example.com", 
        password="userpass123", 
        name="User Two"
    )
    
    # Create a note for user2
    user2_note = create_test_note(db, user2.id, "User2 Note", "This belongs to User Two")
    
    # Try to edit user2's note as user1
    update_data = {
        "title": "Attempted Update by User1",
        "description": "This shouldn't work"
    }
    
    response = client.put(
        f"/api/v1/notes/{user2_note.id}",
        json=update_data,
        headers=user1_header
    )
    assert response.status_code == 403  # Forbidden


def test_user_cannot_delete_others_notes(client: TestClient, db: Session):
    """
    Test that a regular user cannot delete notes from other users
    """
    # Create two regular users
    user1 = create_test_user(
        db, 
        email="user1@example.com", 
        password="userpass123", 
        name="User One"
    )
    user1_header = get_auth_header(client, "user1@example.com", "userpass123")
    
    user2 = create_test_user(
        db, 
        email="user2@example.com", 
        password="userpass123", 
        name="User Two"
    )
    
    # Create a note for user2
    user2_note = create_test_note(db, user2.id, "User2 Note", "This belongs to User Two")
    
    # Try to delete user2's note as user1
    response = client.delete(f"/api/v1/notes/{user2_note.id}", headers=user1_header)
    assert response.status_code == 403  # Forbidden
    
    # Check that the note still exists
    note = db.query(Note).filter(Note.id == user2_note.id).first()
    assert note is not None